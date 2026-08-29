from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass

from backend.engine.robust import select_minimum_regret
from backend.finance.digital_twin import project_monthly_cashflow
from backend.models.venture import VentureCandidate


@dataclass(frozen=True)
class ScenarioDraw:
    scenario_id: str
    demand_factor: float
    price_factor: float
    variable_cost_factor: float
    fixed_cost_factor: float


def triangular_scenarios(seed_key: str, count: int = 512) -> list[ScenarioDraw]:
    """Reproducible non-Gaussian economic scenarios shared by every candidate."""
    if count < 2:
        raise ValueError("count must be at least two")
    seed = int(hashlib.sha256(seed_key.encode()).hexdigest()[:16], 16)
    rng = random.Random(seed)
    return [
        ScenarioDraw(
            scenario_id=f"scenario-{index:04d}",
            demand_factor=rng.triangular(0.65, 1.20, 1.0),
            price_factor=rng.triangular(0.82, 1.12, 1.0),
            variable_cost_factor=rng.triangular(0.92, 1.28, 1.0),
            fixed_cost_factor=rng.triangular(0.95, 1.18, 1.0),
        )
        for index in range(count)
    ]


def value_at_risk(losses: list[float], alpha: float = 0.95) -> float:
    if not losses or not 0 < alpha < 1:
        raise ValueError("losses are required and alpha must be between zero and one")
    ordered = sorted(losses)
    index = min(len(ordered) - 1, max(0, int(alpha * len(ordered))))
    return ordered[index]


def conditional_value_at_risk(losses: list[float], alpha: float = 0.95) -> float:
    threshold = value_at_risk(losses, alpha)
    tail = [loss for loss in losses if loss >= threshold]
    return sum(tail) / len(tail)


def analyze_candidate_scenarios(
    candidate: VentureCandidate,
    *,
    available_capital: float,
    monthly_demand: float,
    margin_share: float,
    draws: list[ScenarioDraw],
    unit_price: float = 1.0,
    variable_cost_per_unit: float | None = None,
    minimum_monthly_income: float = 0,
) -> dict:
    outcomes = []
    variable_cost = (
        max(0.0, unit_price - margin_share)
        if variable_cost_per_unit is None
        else variable_cost_per_unit
    )
    for draw in draws:
        twin = project_monthly_cashflow(
            opening_cash=max(available_capital - candidate.investment, 0),
            monthly_demand=monthly_demand * draw.demand_factor,
            capacity=float(candidate.total_capacity),
            unit_price=unit_price * draw.price_factor,
            variable_cost_per_unit=variable_cost * draw.variable_cost_factor,
            fixed_monthly_cost=float(candidate.monthly_opex) * draw.fixed_cost_factor,
            growth_rate=0.003,
            ramp_months=6,
            initial_investment=float(candidate.investment),
            owner_capital=float(candidate.investment),
        )
        month_12_income = twin.months[11].operating_cash_flow
        outcomes.append(
            {
                "scenario_id": draw.scenario_id,
                "survives": twin.default_month is None,
                "minimum_cash": twin.minimum_cash,
                "cumulative_cash": twin.cumulative_cash_flow,
                "payback_month": twin.investment_payback_month,
                "month_12_owner_income": month_12_income,
            }
        )
    losses = [-item["cumulative_cash"] for item in outcomes]
    count = len(outcomes)
    return {
        "candidate_id": candidate.candidate_id,
        "scenario_count": count,
        "distribution": "independent triangular planning factors; not empirically calibrated",
        "scenario_survival_rate": sum(item["survives"] for item in outcomes) / count,
        "target_income_rate": sum(
            item["month_12_owner_income"] >= minimum_monthly_income for item in outcomes
        )
        / count,
        "payback_within_36_months_rate": sum(
            item["payback_month"] is not None and item["payback_month"] <= 36 for item in outcomes
        )
        / count,
        "minimum_cash_p10": _quantile([item["minimum_cash"] for item in outcomes], 0.10),
        "cumulative_cash_p10": _quantile([item["cumulative_cash"] for item in outcomes], 0.10),
        "cumulative_cash_median": _quantile([item["cumulative_cash"] for item in outcomes], 0.50),
        "var95_loss": value_at_risk(losses),
        "cvar95_loss": conditional_value_at_risk(losses),
        "outcomes": outcomes,
    }


def compare_candidates_under_uncertainty(
    candidates: list[VentureCandidate],
    *,
    available_capital: float,
    monthly_demand: float,
    margin_share: float,
    seed_key: str,
    unit_price: float = 1.0,
    variable_cost_per_unit: float | None = None,
    minimum_monthly_income: float = 0,
    scenario_count: int = 512,
) -> dict:
    draws = triangular_scenarios(seed_key, scenario_count)
    analyses = [
        analyze_candidate_scenarios(
            candidate,
            available_capital=available_capital,
            monthly_demand=monthly_demand,
            margin_share=margin_share,
            unit_price=unit_price,
            variable_cost_per_unit=variable_cost_per_unit,
            draws=draws,
            minimum_monthly_income=minimum_monthly_income,
        )
        for candidate in candidates
    ]
    scenario_values = {
        draw.scenario_id: {
            analysis["candidate_id"]: analysis["outcomes"][index]["cumulative_cash"]
            for analysis in analyses
        }
        for index, draw in enumerate(draws)
    }
    minimax = select_minimum_regret(scenario_values)
    expected = max(
        analyses,
        key=lambda item: (
            sum(x["cumulative_cash"] for x in item["outcomes"]) / item["scenario_count"]
        ),
    )
    survival = max(
        analyses,
        key=lambda item: (
            item["scenario_survival_rate"],
            item["minimum_cash_p10"],
            -next(
                candidate.investment
                for candidate in candidates
                if candidate.candidate_id == item["candidate_id"]
            ),
        ),
    )
    cvar = min(analyses, key=lambda item: item["cvar95_loss"])
    return {
        "method_version": "triangular-scenario-robust-v1",
        "calibration_status": "PLANNING_SCENARIOS_NOT_EMPIRICALLY_CALIBRATED",
        "scenario_count": scenario_count,
        "candidate_summaries": [
            {key: value for key, value in item.items() if key != "outcomes"} for item in analyses
        ],
        "expected_value_winner": expected["candidate_id"],
        "survival_first_winner": survival["candidate_id"],
        "cvar_aware_winner": cvar["candidate_id"],
        "minimax_regret_winner": minimax.selected_candidate_id,
        "minimax_maximum_regret": minimax.maximum_regret,
        "pareto_frontier": _pareto_frontier(candidates, analyses),
    }


def failure_boundaries(
    candidate: VentureCandidate,
    *,
    available_capital: float,
    monthly_demand: float,
    margin_share: float,
    unit_price: float = 1.0,
    variable_cost_per_unit: float | None = None,
) -> list[dict]:
    variable_cost = (
        max(0.0, unit_price - margin_share)
        if variable_cost_per_unit is None
        else variable_cost_per_unit
    )

    def survives(
        demand_factor: float,
        price_factor: float,
        cost_factor: float,
        fixed_cost_factor: float = 1,
        opening_cash: float | None = None,
    ) -> bool:
        twin = project_monthly_cashflow(
            opening_cash=(
                max(available_capital - candidate.investment, 0)
                if opening_cash is None
                else opening_cash
            ),
            monthly_demand=monthly_demand * demand_factor,
            capacity=float(candidate.total_capacity),
            unit_price=unit_price * price_factor,
            variable_cost_per_unit=variable_cost * cost_factor,
            fixed_monthly_cost=float(candidate.monthly_opex) * fixed_cost_factor,
            growth_rate=0.003,
            ramp_months=6,
            initial_investment=float(candidate.investment),
            owner_capital=float(candidate.investment),
        )
        return twin.default_month is None

    demand_factor, demand_tested = _adaptive_lower_boundary(lambda value: survives(value, 1, 1), 0)
    price_factor, price_tested = _adaptive_lower_boundary(lambda value: survives(1, value, 1), 0)
    cost_factor, cost_tested = _adaptive_upper_boundary(
        lambda value: survives(1, 1, value), maximum=10
    )
    fixed_factor, fixed_tested = _adaptive_upper_boundary(
        lambda value: survives(1, 1, 1, value), maximum=10
    )
    cash_buffer = _minimum_surviving_value(
        lambda value: survives(1, 1, 1, opening_cash=value),
        initial_upper=max(available_capital, candidate.investment, 1),
    )
    return [
        {
            "variable": "monthly_demand",
            "threshold": monthly_demand * demand_factor if demand_factor is not None else None,
            "unit": "planning revenue units/month",
            "tested_bound": demand_tested,
            "interpretation": _lower_boundary_note(
                demand_factor,
                demand_tested,
                "demand",
            ),
        },
        {
            "variable": "selling_price_factor",
            "threshold": price_factor,
            "unit": "share of central planning price",
            "tested_bound": price_tested,
            "interpretation": _lower_boundary_note(
                price_factor,
                price_tested,
                "selling price",
            ),
        },
        {
            "variable": "variable_cost_factor",
            "threshold": cost_factor,
            "unit": "multiple of central variable cost",
            "tested_bound": cost_tested,
            "interpretation": _upper_boundary_note(
                cost_factor,
                cost_tested,
                "variable cost",
            ),
        },
        {
            "variable": "fixed_opex_factor",
            "threshold": fixed_factor,
            "unit": "multiple of central fixed OPEX",
            "tested_bound": fixed_tested,
            "interpretation": _upper_boundary_note(
                fixed_factor,
                fixed_tested,
                "fixed OPEX",
            ),
        },
        {
            "variable": "minimum_cash_buffer",
            "threshold": cash_buffer,
            "unit": "INR opening cash after startup investment",
            "tested_bound": max(available_capital, candidate.investment, 1),
            "interpretation": (
                f"Approximately INR {cash_buffer:,.0f} opening cash is required to remain "
                "non-negative in the central 36-month model."
                if cash_buffer is not None
                else "No finite cash buffer was found within the adaptive tested bound."
            ),
        },
    ]


def sensitivity_analysis(
    candidate: VentureCandidate,
    *,
    available_capital: float,
    monthly_demand: float,
    margin_share: float,
    unit_price: float = 1.0,
    variable_cost_per_unit: float | None = None,
    perturbation: float = 0.05,
) -> list[dict]:
    if not 0 < perturbation < 0.5:
        raise ValueError("perturbation must be between zero and 0.5")
    variable_cost = (
        max(0.0, unit_price - margin_share)
        if variable_cost_per_unit is None
        else variable_cost_per_unit
    )

    def profit(demand: float, price: float, cost: float, fixed: float) -> float:
        twin = project_monthly_cashflow(
            opening_cash=max(available_capital - candidate.investment, 0),
            monthly_demand=monthly_demand * demand,
            capacity=float(candidate.total_capacity),
            unit_price=unit_price * price,
            variable_cost_per_unit=variable_cost * cost,
            fixed_monthly_cost=float(candidate.monthly_opex) * fixed,
            growth_rate=0.003,
            ramp_months=6,
            initial_investment=float(candidate.investment),
            owner_capital=float(candidate.investment),
        )
        return twin.months[11].operating_cash_flow

    central = profit(1, 1, 1, 1)
    variables = {
        "demand": lambda value: profit(value, 1, 1, 1),
        "selling_price": lambda value: profit(1, value, 1, 1),
        "variable_cost": lambda value: profit(1, 1, value, 1),
        "fixed_opex": lambda value: profit(1, 1, 1, value),
    }
    rows = []
    for name, evaluate in variables.items():
        low = evaluate(1 - perturbation)
        high = evaluate(1 + perturbation)
        derivative = (high - low) / (2 * perturbation)
        elasticity = derivative / central if central else None
        rows.append(
            {
                "variable": name,
                "perturbation": perturbation,
                "profit_low": low,
                "profit_central": central,
                "profit_high": high,
                "derivative_per_factor_unit": derivative,
                "elasticity": elasticity,
                "method": "symmetric controlled perturbation around central planning case",
            }
        )
    return sorted(rows, key=lambda row: -abs(row["elasticity"] or 0))


def _adaptive_lower_boundary(evaluate, minimum: float) -> tuple[float | None, float]:
    if evaluate(minimum):
        return None, minimum
    lower = minimum
    upper = 1.0
    for _ in range(40):
        middle = (lower + upper) / 2
        if evaluate(middle):
            upper = middle
        else:
            lower = middle
    return upper, minimum


def _adaptive_upper_boundary(evaluate, *, maximum: float) -> tuple[float | None, float]:
    lower = 1.0
    upper = 1.25
    while upper < maximum and evaluate(upper):
        lower = upper
        upper = min(maximum, 1 + (upper - 1) * 2)
    if evaluate(upper):
        return None, upper
    for _ in range(40):
        middle = (lower + upper) / 2
        if evaluate(middle):
            lower = middle
        else:
            upper = middle
    return upper, upper


def _minimum_surviving_value(evaluate, *, initial_upper: float) -> float | None:
    if evaluate(0):
        return 0.0
    upper = initial_upper
    maximum = max(initial_upper * 8, 1)
    while upper < maximum and not evaluate(upper):
        upper = min(maximum, upper * 2)
    if not evaluate(upper):
        return None
    lower = 0.0
    for _ in range(40):
        middle = (lower + upper) / 2
        if evaluate(middle):
            upper = middle
        else:
            lower = middle
    return upper


def _lower_boundary_note(value: float | None, tested: float, variable: str) -> str:
    if value is None:
        deterioration = (1 - tested) * 100
        return f"No cash failure up to {deterioration:.0f}% {variable} deterioration."
    return f"Plan becomes cash-negative below approximately {value:.3f}x central {variable}."


def _upper_boundary_note(value: float | None, tested: float, variable: str) -> str:
    if value is None:
        deterioration = (tested - 1) * 100
        return f"No cash failure up to {deterioration:.0f}% {variable} increase."
    return f"Plan becomes cash-negative above approximately {value:.3f}x central {variable}."


def _quantile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = probability * (len(ordered) - 1)
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    weight = position - low
    return ordered[low] * (1 - weight) + ordered[high] * weight


def _pareto_frontier(candidates: list[VentureCandidate], analyses: list[dict]) -> list[str]:
    points = {
        candidate.candidate_id: (
            float(candidate.investment),
            next(
                item["scenario_survival_rate"]
                for item in analyses
                if item["candidate_id"] == candidate.candidate_id
            ),
            next(
                item["cumulative_cash_median"]
                for item in analyses
                if item["candidate_id"] == candidate.candidate_id
            ),
        )
        for candidate in candidates
    }
    frontier = []
    for candidate, point in points.items():
        dominated = any(
            other != candidate
            and other_point[0] <= point[0]
            and other_point[1] >= point[1]
            and other_point[2] >= point[2]
            and (
                other_point[0] < point[0] or other_point[1] > point[1] or other_point[2] > point[2]
            )
            for other, other_point in points.items()
        )
        if not dominated:
            frontier.append(candidate)
    return sorted(frontier)

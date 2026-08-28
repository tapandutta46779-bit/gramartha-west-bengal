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
    minimum_monthly_income: float = 0,
) -> dict:
    outcomes = []
    variable_cost = min(0.92, max(0.05, 1 - margin_share))
    for draw in draws:
        twin = project_monthly_cashflow(
            opening_cash=max(available_capital - candidate.investment, 0),
            monthly_demand=monthly_demand * draw.demand_factor,
            capacity=float(candidate.total_capacity),
            unit_price=draw.price_factor,
            variable_cost_per_unit=min(0.99, variable_cost * draw.variable_cost_factor),
            fixed_monthly_cost=float(candidate.monthly_opex) * 0.15 * draw.fixed_cost_factor,
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
) -> list[dict]:
    variable_cost = min(0.92, max(0.05, 1 - margin_share))

    def survives(demand_factor: float, price_factor: float, cost_factor: float) -> bool:
        twin = project_monthly_cashflow(
            opening_cash=max(available_capital - candidate.investment, 0),
            monthly_demand=monthly_demand * demand_factor,
            capacity=float(candidate.total_capacity),
            unit_price=price_factor,
            variable_cost_per_unit=min(0.999, variable_cost * cost_factor),
            fixed_monthly_cost=float(candidate.monthly_opex) * 0.15,
            growth_rate=0.003,
            ramp_months=6,
            initial_investment=float(candidate.investment),
            owner_capital=float(candidate.investment),
        )
        return twin.default_month is None

    demand_factor = _boundary(lambda value: survives(value, 1, 1), 0, 1, seek_low=True)
    price_factor = _boundary(lambda value: survives(1, value, 1), 0, 1, seek_low=True)
    cost_factor = _boundary(lambda value: survives(1, 1, value), 1, 2.5, seek_low=False)
    return [
        {
            "variable": "monthly_demand",
            "threshold": monthly_demand * demand_factor if demand_factor is not None else None,
            "unit": "planning revenue units/month",
            "interpretation": _boundary_note(demand_factor, "below this demand"),
        },
        {
            "variable": "selling_price_factor",
            "threshold": price_factor,
            "unit": "share of central planning price",
            "interpretation": _boundary_note(price_factor, "below this price factor"),
        },
        {
            "variable": "variable_cost_factor",
            "threshold": cost_factor,
            "unit": "multiple of central variable cost",
            "interpretation": _boundary_note(cost_factor, "above this cost factor"),
        },
    ]


def _boundary(evaluate, lower: float, upper: float, *, seek_low: bool) -> float | None:
    if seek_low and evaluate(lower):
        return None
    if not seek_low and evaluate(upper):
        return None
    for _ in range(40):
        middle = (lower + upper) / 2
        if evaluate(middle) == seek_low:
            upper = middle
        else:
            lower = middle
    return upper


def _boundary_note(value: float | None, failure_condition: str) -> str:
    if value is None:
        return "No cash failure occurred within the tested 36-month range."
    return f"Plan becomes cash-negative approximately {failure_condition}."


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

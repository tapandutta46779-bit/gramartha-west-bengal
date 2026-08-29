from __future__ import annotations

from backend.models.economic_graph import EconomicGraph
from backend.models.profile import EntrepreneurProfile
from backend.models.venture import MVVResult, VentureCandidate

from .counterfactual import evaluate_candidate


def select_minimum_viable_venture(
    graph: EconomicGraph,
    profile: EntrepreneurProfile,
    candidates: list[VentureCandidate],
    minimum_newly_served: float,
    contribution_margin_per_unit: float,
) -> MVVResult:
    """Exhaustive exact oracle for a finite candidate list."""
    feasible = []
    rejected = []
    metrics = []
    target_income = float(profile.minimum_monthly_income or 0)
    debt_ceiling = float(profile.acceptable_debt or 0)
    funding_ceiling = float(profile.available_capital) + debt_ceiling
    for candidate in candidates:
        reasons = []
        debt_required = max(float(candidate.investment) - float(profile.available_capital), 0)
        if candidate.investment > funding_ceiling:
            reasons.append("FUNDING_LIMIT")
        if debt_required > debt_ceiling:
            reasons.append("DEBT_CEILING")
        service_radius = max(
            (
                float(primitive.service_radius_km)
                for primitive in candidate.primitives
                if primitive.service_radius_km is not None
            ),
            default=0,
        )
        if profile.mobility_km is not None and service_radius > float(profile.mobility_km):
            reasons.append("MOBILITY_LIMIT")
        if (
            profile.time_availability_hours_week is not None
            and float(profile.time_availability_hours_week) < 20
            and any(primitive.staff <= 1 for primitive in candidate.primitives)
        ):
            reasons.append("TIME_AVAILABILITY_LIMIT")
        counterfactual = evaluate_candidate(graph, candidate)
        if counterfactual.newly_served_demand < minimum_newly_served:
            reasons.append("INSUFFICIENT_NEW_DEMAND_SERVED")
        monthly_margin = (
            counterfactual.added_venture_flow * contribution_margin_per_unit
            - candidate.monthly_opex
        )
        if monthly_margin < target_income:
            reasons.append("MINIMUM_INCOME_NOT_MET")
        metrics.append(
            {
                "candidate_id": candidate.candidate_id,
                "investment": float(candidate.investment),
                "own_capital_required": min(
                    float(candidate.investment), float(profile.available_capital)
                ),
                "debt_required": debt_required,
                "owner_income_monthly": monthly_margin,
                "newly_served_demand": counterfactual.newly_served_demand,
                "reasons": reasons,
            }
        )
        if reasons:
            rejected.append({"candidate_id": candidate.candidate_id, "reasons": reasons})
        else:
            feasible.append((candidate, counterfactual, monthly_margin))
    if not feasible:
        binding = sorted({reason for item in rejected for reason in item["reasons"]})
        return MVVResult(
            status="NO_FEASIBLE_CANDIDATE",
            rejected=rejected,
            evaluated_count=len(candidates),
            binding_constraints=binding,
            inverse_analysis=_inverse_analysis(metrics, profile),
            constraint_relaxation=_constraint_relaxation(metrics, profile),
            candidate_metrics=metrics,
        )
    candidate, counterfactual, _ = min(
        feasible,
        key=lambda item: (item[0].investment, -item[1].newly_served_demand, item[0].candidate_id),
    )
    return MVVResult(
        status="OPTIMAL_OVER_ENUMERATED_CANDIDATES",
        selected=candidate,
        counterfactual=counterfactual,
        rejected=rejected,
        evaluated_count=len(candidates),
        inverse_analysis=_inverse_analysis(metrics, profile),
        constraint_relaxation=_constraint_relaxation(metrics, profile),
        candidate_metrics=metrics,
    )


def _inverse_analysis(metrics: list[dict], profile: EntrepreneurProfile) -> dict:
    debt_ceiling = float(profile.acceptable_debt or 0)
    funding_ceiling = float(profile.available_capital) + debt_ceiling
    funding_feasible = [item for item in metrics if item["investment"] <= funding_ceiling]
    income_max = max(
        (item["owner_income_monthly"] for item in funding_feasible),
        default=None,
    )
    target = float(profile.minimum_monthly_income or 0)
    target_candidates = [item for item in metrics if item["owner_income_monthly"] >= target]
    minimum_capital = min(
        (max(item["investment"] - debt_ceiling, 0) for item in target_candidates),
        default=None,
    )
    minimum_debt = min(
        (
            max(item["investment"] - float(profile.available_capital), 0)
            for item in target_candidates
        ),
        default=None,
    )
    return {
        "maximum_owner_income_with_current_funding": income_max,
        "minimum_own_capital_for_income_target": minimum_capital,
        "minimum_debt_for_income_target": minimum_debt,
        "scope": "exact over enumerated configurations",
    }


def _constraint_relaxation(metrics: list[dict], profile: EntrepreneurProfile) -> dict:
    if not metrics:
        return {}
    target = float(profile.minimum_monthly_income or 0)
    debt_ceiling = float(profile.acceptable_debt or 0)
    funding_ceiling = float(profile.available_capital) + debt_ceiling
    within_funding = [item for item in metrics if item["investment"] <= funding_ceiling]
    best_current = max(
        within_funding,
        key=lambda item: item["owner_income_monthly"],
        default=None,
    )
    target_candidates = [item for item in metrics if item["owner_income_monthly"] >= target]
    nearest_target = min(
        target_candidates,
        key=lambda item: (
            max(item["investment"] - funding_ceiling, 0),
            item["investment"],
        ),
        default=None,
    )
    return {
        "requested_income": target,
        "best_income_with_current_limits": (
            best_current["owner_income_monthly"] if best_current else None
        ),
        "income_shortfall": (
            max(target - best_current["owner_income_monthly"], 0) if best_current else target
        ),
        "additional_own_capital_needed": (
            max(nearest_target["investment"] - funding_ceiling, 0) if nearest_target else None
        ),
        "additional_debt_ceiling_needed": (
            max(nearest_target["debt_required"] - debt_ceiling, 0) if nearest_target else None
        ),
        "nearest_candidate_id": nearest_target["candidate_id"] if nearest_target else None,
        "scope": "minimum relaxation over enumerated configurations",
    }

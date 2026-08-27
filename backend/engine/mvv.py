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
    for candidate in candidates:
        reasons = []
        if candidate.investment > profile.available_capital:
            reasons.append("CAPITAL_LIMIT")
        counterfactual = evaluate_candidate(graph, candidate)
        if counterfactual.newly_served_demand < minimum_newly_served:
            reasons.append("INSUFFICIENT_NEW_DEMAND_SERVED")
        monthly_margin = (
            counterfactual.added_venture_flow * contribution_margin_per_unit
            - candidate.monthly_opex
        )
        if monthly_margin < profile.minimum_monthly_income:
            reasons.append("MINIMUM_INCOME_NOT_MET")
        if reasons:
            rejected.append({"candidate_id": candidate.candidate_id, "reasons": reasons})
        else:
            feasible.append((candidate, counterfactual, monthly_margin))
    if not feasible:
        return MVVResult(
            status="NO_FEASIBLE_CANDIDATE",
            rejected=rejected,
            evaluated_count=len(candidates),
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
    )

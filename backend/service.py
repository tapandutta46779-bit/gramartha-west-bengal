from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from backend.api.contracts import AnalyzeRequest
from backend.engine.bottleneck import rank_capacity_bottlenecks
from backend.engine.flow_engine import solve_min_cost_flow
from backend.engine.mvv import select_minimum_viable_venture
from backend.evidence.store import EvidenceStore
from backend.finance.calculator import amortized_loan
from backend.finance.digital_twin import project_monthly_cashflow
from backend.models.decision import (
    DecisionExplanation,
    DecisionStatus,
    VentureDecision,
)
from backend.models.evidence import ConfidenceLevel, EvidenceType


def analyze(request: AnalyzeRequest, store: EvidenceStore) -> VentureDecision:
    analysis_id = str(uuid4())
    now = datetime.now(UTC)
    geography = store.get_geography(request.geo_id)
    evidence = request.evidence or store.get_evidence(request.geo_id)
    gaps = []
    if geography is None:
        gaps.append("No verified geographic crosswalk record for geo_id.")
    if not evidence:
        gaps.append("No source-linked locality evidence was supplied or found.")
    if request.graph is None:
        gaps.append("No evidence-backed economic graph was supplied.")
    else:
        evidence_ids = {item.id for item in evidence}
        for node in request.graph.nodes:
            if (node.demand > 0 or node.supply > 0) and not node.evidence_ids:
                gaps.append(f"Economic node {node.node_id} has no evidence reference.")
            elif any(item not in evidence_ids for item in node.evidence_ids):
                gaps.append(f"Economic node {node.node_id} cites unavailable evidence.")
        for edge in request.graph.edges:
            if not edge.evidence_ids:
                gaps.append(f"Economic edge {edge.edge_id} has no evidence reference.")
            elif any(item not in evidence_ids for item in edge.evidence_ids):
                gaps.append(f"Economic edge {edge.edge_id} cites unavailable evidence.")
    if gaps:
        decision = VentureDecision(
            analysis_id=analysis_id,
            created_at=now,
            status=DecisionStatus.INSUFFICIENT_EVIDENCE,
            methodology_version="decision-v1",
            geography=geography,
            entrepreneur=request.entrepreneur,
            confidence=ConfidenceLevel.INSUFFICIENT,
            evidence=evidence,
            evidence_gaps=gaps,
            explanation=DecisionExplanation(
                summary="A venture recommendation was not produced.",
                evidence_statement=(
                    "The required locality evidence and network model are incomplete."
                ),
                caveats=gaps,
            ),
        )
        store.put_analysis(decision)
        return decision

    baseline = solve_min_cost_flow(request.graph)
    bottlenecks = rank_capacity_bottlenecks(request.graph, baseline)
    mvv = select_minimum_viable_venture(
        request.graph,
        request.entrepreneur,
        request.candidates,
        float(request.minimum_newly_served),
        request.contribution_margin_per_unit,
    )
    loan_terms = None
    twin = None
    if request.loan:
        loan_terms = amortized_loan(
            float(request.loan.principal),
            float(request.loan.annual_interest_rate),
            request.loan.tenure_months,
            request.loan.rule,
            request.loan.real_decision,
        )
    if request.operating_assumptions:
        twin = project_monthly_cashflow(
            **request.operating_assumptions.model_dump(),
            loan=loan_terms,
        )
    synthetic_only = all(item.evidence_type == EvidenceType.SYNTHETIC for item in evidence)
    viable = mvv.selected is not None and (twin is None or twin.default_month is None)
    status = DecisionStatus.CONDITIONAL if viable else DecisionStatus.NOT_FEASIBLE
    confidence = ConfidenceLevel.LOW if synthetic_only else ConfidenceLevel.MEDIUM
    caveats = []
    if synthetic_only:
        caveats.append("Controlled synthetic evidence cannot justify a real-world recommendation.")
    if request.loan and not (loan_terms and loan_terms.verified_for_real_decision):
        caveats.append("Finance terms are illustrative, not a verified current scheme entitlement.")
    selected = mvv.selected
    decision = VentureDecision(
        analysis_id=analysis_id,
        created_at=now,
        status=status,
        methodology_version="decision-v1",
        geography=geography,
        entrepreneur=request.entrepreneur,
        confidence=confidence,
        evidence=evidence,
        evidence_gaps=caveats,
        baseline_flow=baseline,
        bottlenecks=bottlenecks,
        selected_venture=selected,
        counterfactual=mvv.counterfactual,
        mvv=mvv,
        loan_terms=loan_terms,
        digital_twin=twin,
        staged_plan=(
            [
                "Validate local price and throughput assumptions before committing capital.",
                "Pilot at the smallest enumerated feasible capacity.",
                "Expand only after measured demand, cash, and service triggers are met.",
            ]
            if selected
            else []
        ),
        explanation=DecisionExplanation(
            summary=(
                f"{selected.candidate_id} is feasible only under supplied model assumptions."
                if selected
                else "No enumerated venture meets the configured feasibility constraints."
            ),
            evidence_statement=(
                "All numeric outputs are copied from the canonical deterministic decision object."
            ),
            caveats=caveats,
        ),
        calculation_trace={
            "flow_solver": baseline.solver,
            "mvv_objective": mvv.objective,
            "mvv_exact_scope": "enumerated candidate set",
        },
    )
    store.put_analysis(decision)
    return decision

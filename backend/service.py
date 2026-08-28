from __future__ import annotations

import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from backend.api.contracts import AnalyzeRequest
from backend.engine.bottleneck import rank_capacity_bottlenecks
from backend.engine.flow_engine import solve_min_cost_flow
from backend.engine.mvv import select_minimum_viable_venture
from backend.engine.uncertainty import compare_candidates_under_uncertainty, failure_boundaries
from backend.evidence.geography_resolver import resolve_locality
from backend.evidence.store import EvidenceStore
from backend.explanation import deterministic_explanation
from backend.finance.calculator import (
    amortized_loan,
    break_even_volume,
    internal_rate_of_return,
    net_present_value,
)
from backend.finance.digital_twin import project_monthly_cashflow
from backend.finance.rules import screen_ahidf, screen_pmmy
from backend.models.decision import (
    DecisionStatus,
    EvidenceGapCode,
    EvidenceGate,
    VentureDecision,
)
from backend.models.evidence import ConfidenceLevel, EvidenceType
from backend.models.geography import GeographicResolution, ResolutionMethod
from backend.models.profile import EntrepreneurProfile
from backend.pipeline.automatic import build_automatic_inputs
from backend.spatial.osm_store import OsmEntity, OsmSpatialStore, haversine_km


def analyze(request: AnalyzeRequest, store: EvidenceStore) -> VentureDecision:
    analysis_id = str(uuid4())
    now = datetime.now(UTC)
    resolution, geography = _resolve_request_geography(request, store)
    location_gates = _location_gates(resolution)
    if geography is None:
        return _refusal(
            analysis_id=analysis_id,
            now=now,
            request=request,
            store=store,
            resolution=resolution,
            gates=location_gates,
        )

    entrepreneur = _entrepreneur(request, geography.geo_id)
    sector = entrepreneur.business_category
    local_evidence = request.evidence or store.get_evidence(geography.geo_id)
    survey_sector = "2" if geography.locality_type in {"TOWN", "WARD"} else "1"
    evidence = [*local_evidence, *store.get_regional_priors(geography.district, survey_sector)]
    automatic = build_automatic_inputs(
        geo_id=geography.geo_id,
        sector=sector,
        evidence=evidence,
        profile=entrepreneur,
    )
    spatial = _spatial_context(geography, request.catchment_radius_km, sector)
    graph = request.graph or automatic.graph
    candidates = request.candidates or automatic.candidates
    gates = [*location_gates, *automatic.gates]
    if request.graph is not None:
        gates.extend(_advanced_graph_gates(request, evidence))
    if request.loan and request.loan.rule and request.loan.rule.status == "VERIFIED":
        gates = [gate for gate in gates if gate.code != EvidenceGapCode.NO_CURRENT_FINANCE_RULE]

    baseline = solve_min_cost_flow(graph) if graph else None
    bottlenecks = rank_capacity_bottlenecks(graph, baseline) if graph and baseline else []
    automatic_margin = (
        float(automatic.price.central)
        if automatic.price.unit == "gross margin share" and automatic.price.central is not None
        else request.contribution_margin_per_unit
    )
    mvv = None
    if graph and candidates:
        mvv = select_minimum_viable_venture(
            graph,
            entrepreneur,
            candidates,
            float(request.minimum_newly_served),
            automatic_margin,
        )
    selected = mvv.selected if mvv else None
    loan_terms = None
    if request.loan:
        loan_terms = amortized_loan(
            float(request.loan.principal),
            float(request.loan.annual_interest_rate),
            request.loan.tenure_months,
            request.loan.rule,
            request.loan.real_decision,
        )
    twin = None
    if request.operating_assumptions:
        twin = project_monthly_cashflow(
            **request.operating_assumptions.model_dump(), loan=loan_terms
        )
    elif selected and automatic.demand.central and automatic_margin > 0:
        twin = project_monthly_cashflow(
            opening_cash=max(float(entrepreneur.available_capital) - selected.investment, 0),
            monthly_demand=float(automatic.demand.central),
            capacity=float(selected.total_capacity),
            unit_price=1.0,
            variable_cost_per_unit=min(0.92, max(0.05, 1 - automatic_margin)),
            fixed_monthly_cost=float(selected.monthly_opex) * 0.15,
            growth_rate=0.003,
            ramp_months=6,
            initial_investment=float(selected.investment),
            owner_capital=float(selected.investment),
        )
    requested_finance = float(request.loan.principal) if request.loan else None
    financial_metrics = {}
    if selected and twin:
        month_12 = twin.months[min(11, len(twin.months) - 1)]
        contribution = max(
            0.0,
            twin.assumptions["unit_price"] - twin.assumptions["variable_cost_per_unit"],
        )
        cash_flows = [
            -float(selected.investment),
            *(month.operating_cash_flow for month in twin.months),
        ]
        financial_metrics = {
            "gross_margin": (
                (month_12.revenue - month_12.variable_cost) / month_12.revenue
                if month_12.revenue
                else None
            ),
            "operating_margin": (
                month_12.operating_cash_flow / month_12.revenue if month_12.revenue else None
            ),
            "contribution_margin_per_unit": contribution,
            "break_even_volume_month": (
                break_even_volume(
                    twin.assumptions["unit_price"],
                    twin.assumptions["variable_cost_per_unit"],
                    twin.assumptions["fixed_monthly_cost"],
                )
                if contribution > 0
                else None
            ),
            "npv_36_month_at_12pct": net_present_value(cash_flows, 0.12),
            "irr_annualized": internal_rate_of_return(cash_flows),
            "confidence_note": (
                "NPV/IRR are planning outputs from benchmark-adjusted assumptions, not "
                "investment guarantees."
            ),
        }
    robust_analysis = {}
    computed_boundaries = []
    if (
        request.analysis_mode == "deep"
        and selected
        and candidates
        and automatic.demand.central
        and automatic.price.unit == "gross margin share"
    ):
        robust_analysis = compare_candidates_under_uncertainty(
            candidates,
            available_capital=float(entrepreneur.available_capital),
            monthly_demand=float(automatic.demand.central),
            margin_share=automatic_margin,
            seed_key=f"{geography.geo_id}:{sector}:deep-v1",
            minimum_monthly_income=float(entrepreneur.minimum_monthly_income),
        )
        computed_boundaries = failure_boundaries(
            selected,
            available_capital=float(entrepreneur.available_capital),
            monthly_demand=float(automatic.demand.central),
            margin_share=automatic_margin,
        )
    finance_screen = screen_pmmy(
        sector=sector,
        requested_amount=requested_finance,
        previously_repaid_tarun=bool(request.profile.get("previously_repaid_tarun", False)),
    )
    ahidf_screen = screen_ahidf(
        sector=sector,
        requested_amount=requested_finance,
        organization_type=request.profile.get("organization_type"),
    )

    blocking = [gate for gate in gates if gate.blocking]
    viable = selected is not None and (twin is None or twin.default_month is None)
    if blocking:
        status = DecisionStatus.INSUFFICIENT_EVIDENCE
    elif viable:
        status = DecisionStatus.CONDITIONAL
    else:
        status = DecisionStatus.NOT_FEASIBLE
    synthetic_only = bool(evidence) and all(
        item.evidence_type == EvidenceType.SYNTHETIC for item in evidence
    )
    confidence = _decision_confidence(resolution, evidence, blocking, synthetic_only)
    limitations = [gate.message for gate in gates]
    swot = _derive_swot(evidence, spatial, baseline, bottlenecks, gates)
    decision = VentureDecision(
        analysis_id=analysis_id,
        created_at=now,
        status=status,
        methodology_version="decision-v5",
        geography=geography,
        geo_resolution=resolution,
        entrepreneur=entrepreneur,
        sector=sector,
        confidence=confidence,
        evidence=evidence,
        evidence_gaps=[gate.code for gate in gates],
        evidence_gates=gates,
        data_quality={
            "evidence_record_count": len(evidence),
            "synthetic_only": synthetic_only,
            "geo_confidence": resolution.confidence,
            "official_geo_code_available": bool(geography.lgd_code or geography.census_code),
            "osm_spatial_context_available": bool(spatial["catchment"]),
        },
        demand=automatic.demand,
        supply=automatic.supply,
        price=automatic.price,
        competition=spatial["competition"],
        catchment=spatial["catchment"],
        generated_graph=graph if request.graph is None else None,
        economic_graph_summary=(
            automatic.graph_summary
            if request.graph is None
            else {
                "node_count": len(graph.nodes) if graph else 0,
                "edge_count": len(graph.edges) if graph else 0,
                "builder": "CALLER_SUPPLIED_ADVANCED_MODE",
            }
        ),
        baseline_flow=baseline,
        bottlenecks=bottlenecks,
        selected_venture=selected,
        counterfactual=mvv.counterfactual if mvv else None,
        mvv=mvv,
        loan_terms=loan_terms,
        official_finance=[finance_screen, ahidf_screen],
        prudent_financing=(
            {
                "estimated_project_cost": selected.investment,
                "available_own_capital": float(entrepreneur.available_capital),
                "illustrative_financing_requirement": max(
                    selected.investment - float(entrepreneur.available_capital), 0
                ),
                "wording": "Potentially eligible / illustrative structure; not lender approval.",
                "financial_metrics": financial_metrics,
            }
            if selected
            else {}
        ),
        digital_twin=twin,
        operating_break_even=twin.operating_break_even_month if twin else None,
        investment_payback=twin.investment_payback_month if twin else None,
        alternatives=[candidate for candidate in candidates if candidate != selected],
        candidate_ventures=candidates,
        failure_boundaries=computed_boundaries,
        robust_comparison=(
            {
                "best_base_case": selected.candidate_id,
                "lowest_capital": min(candidates, key=lambda item: item.investment).candidate_id,
                "second_best": next(
                    (item.candidate_id for item in candidates if item != selected), None
                ),
                "scope": "enumerated benchmark-adjusted configurations",
                **robust_analysis,
            }
            if selected and candidates
            else {}
        ),
        staged_plan=(
            [
                "Stage 1: start the selected minimum-capital configuration and preserve the "
                "modelled cash buffer.",
                "Stage 2 trigger: expand after three consecutive months above 70% capacity "
                "with non-negative closing cash.",
                "Stage 3 trigger: consider owned assets after reserves cover three months of "
                "operating cost.",
            ]
            if selected
            else []
        ),
        swot=swot,
        explanation=deterministic_explanation(
            request.language, gates=gates, has_selection=bool(selected and not blocking)
        ),
        calculation_trace={
            "flow_solver": baseline.solver if baseline else None,
            "mvv_objective": mvv.objective if mvv else None,
            "mvv_exact_scope": "enumerated candidate set" if mvv else None,
            "automatic_graph_attempted": request.graph is None,
            "analysis_mode": request.analysis_mode,
            "uncertainty_scenarios": robust_analysis.get("scenario_count", 0),
            "evidence_gate_codes": [gate.code for gate in gates],
        },
        limitations=[*limitations, *spatial["limitations"]],
        sources=sorted(
            {
                *(str(item.source_url) for item in evidence),
                *(item.source_url for item in (finance_screen, ahidf_screen)),
                *spatial["sources"],
            }
        ),
        model_versions=automatic.model_versions,
        data_versions={**_data_versions(evidence), **spatial["data_versions"]},
        software_git_commit=_git_commit(),
    )
    store.put_analysis(decision)
    return decision


def _resolve_request_geography(request: AnalyzeRequest, store: EvidenceStore):
    if request.geo_id:
        geography = store.get_geography(request.geo_id)
        resolution = GeographicResolution(
            query_state=request.state,
            query_district=request.district,
            query_locality=request.locality or request.geo_id,
            resolved_geo_id=geography.geo_id if geography else None,
            resolution_method=(
                ResolutionMethod.EXACT_GEO_ID if geography else ResolutionMethod.NOT_FOUND
            ),
            confidence=1.0 if geography else 0.0,
            source_ids=geography.source_ids if geography else [],
            matched_ids={"internal_geo_id": geography.geo_id} if geography else {},
            candidates=[geography] if geography else [],
            ambiguity_flags=[] if geography else ["UNKNOWN_GEO_ID"],
        )
        return resolution, geography
    resolution = resolve_locality(
        store,
        locality=request.locality or "",
        district=request.district,
        state=request.state,
        parent=request.parent_locality,
        allow_fuzzy=request.allow_fuzzy_location,
    )
    geography = (
        store.get_geography(resolution.resolved_geo_id) if resolution.resolved_geo_id else None
    )
    return resolution, geography


def _location_gates(resolution: GeographicResolution) -> list[EvidenceGate]:
    if resolution.resolution_method == ResolutionMethod.AMBIGUOUS:
        return [
            EvidenceGate(
                code=EvidenceGapCode.AMBIGUOUS_LOCATION,
                message="Multiple localities match; district/parent disambiguation is required.",
            )
        ]
    if resolution.resolution_method == ResolutionMethod.NOT_FOUND:
        return [
            EvidenceGate(
                code=EvidenceGapCode.LOCATION_NOT_FOUND,
                message="No supported West Bengal locality record matches the request.",
            )
        ]
    if resolution.confidence < 0.9:
        return [
            EvidenceGate(
                code=EvidenceGapCode.LOW_GEO_CONFIDENCE,
                message="Locality resolution confidence is below the production threshold.",
            )
        ]
    return []


def _entrepreneur(request: AnalyzeRequest, geo_id: str) -> EntrepreneurProfile:
    if request.entrepreneur:
        return request.entrepreneur.model_copy(update={"geo_id": geo_id})
    values = dict(request.profile)
    values.pop("geo_id", None)
    values.pop("available_capital", None)
    values.pop("business_category", None)
    return EntrepreneurProfile(
        geo_id=geo_id,
        available_capital=float(request.capital or 0),
        business_category=request.business_category or "",
        **values,
    )


def _advanced_graph_gates(request: AnalyzeRequest, evidence) -> list[EvidenceGate]:
    if request.graph is None:
        return []
    evidence_ids = {item.id for item in evidence}
    messages = []
    for node in request.graph.nodes:
        if (node.demand > 0 or node.supply > 0) and (
            not node.evidence_ids or any(item not in evidence_ids for item in node.evidence_ids)
        ):
            messages.append(f"node {node.node_id}")
    for edge in request.graph.edges:
        if not edge.evidence_ids or any(item not in evidence_ids for item in edge.evidence_ids):
            messages.append(f"edge {edge.edge_id}")
    return (
        [
            EvidenceGate(
                code=EvidenceGapCode.NO_CAPACITY_EVIDENCE,
                message="Advanced graph has missing/unavailable evidence references: "
                + ", ".join(messages),
            )
        ]
        if messages
        else []
    )


def _refusal(
    *,
    analysis_id: str,
    now: datetime,
    request: AnalyzeRequest,
    store: EvidenceStore,
    resolution: GeographicResolution,
    gates: list[EvidenceGate],
) -> VentureDecision:
    decision = VentureDecision(
        analysis_id=analysis_id,
        created_at=now,
        status=DecisionStatus.INSUFFICIENT_EVIDENCE,
        methodology_version="decision-v5",
        geo_resolution=resolution,
        sector=request.business_category,
        confidence=ConfidenceLevel.INSUFFICIENT,
        evidence_gaps=[gate.code for gate in gates],
        evidence_gates=gates,
        explanation=deterministic_explanation(request.language, gates=gates, has_selection=False),
        limitations=[gate.message for gate in gates],
        software_git_commit=_git_commit(),
    )
    store.put_analysis(decision)
    return decision


def _decision_confidence(resolution, evidence, blocking, synthetic_only):
    if blocking or not evidence:
        return ConfidenceLevel.INSUFFICIENT
    if synthetic_only or resolution.confidence < 0.95:
        return ConfidenceLevel.LOW
    return ConfidenceLevel.MEDIUM


def _data_versions(evidence) -> dict[str, str]:
    versions = {}
    for item in evidence:
        version = item.attributes.get("dataset_version")
        if version:
            versions[item.source_id] = str(version)
    return versions


def _spatial_context(geography, radius_km: float, sector: str) -> dict:
    empty = {
        "catchment": {},
        "competition": {},
        "limitations": [],
        "sources": set(),
        "data_versions": {},
    }
    if geography.latitude is None or geography.longitude is None:
        empty["limitations"] = [
            "No verified/proxy coordinate is attached, so spatial catchment was not computed."
        ]
        return empty
    path = os.environ.get("SIH26091_OSM_SQLITE_PATH")
    if not path or not Path(path).is_file():
        empty["limitations"] = [
            "An OSM coordinate exists, but the indexed OSM database is not configured."
        ]
        return empty
    store = OsmSpatialStore(path)
    radial = store.radial_catchment(
        geography.latitude,
        geography.longitude,
        radius_km,
        limit=50_000,
    )
    competitors = _sector_competitors(radial.entities, sector)
    institutions = [
        item
        for item in radial.entities
        if item.category
        in {
            "SCHOOL",
            "COLLEGE",
            "HOSPITAL",
            "CLINIC",
            "RESTAURANT",
            "TEA_OR_SWEET_SHOP",
        }
    ]
    markets = [item for item in radial.entities if item.category == "MARKET"]
    nearest_market = _nearest_entity(geography.latitude, geography.longitude, markets)
    route = None
    if nearest_market:
        route = store.route(
            geography.latitude,
            geography.longitude,
            nearest_market.latitude,
            nearest_market.longitude,
            corridor_km=max(2.0, radius_km / 4),
        )
    metadata = store.metadata()
    return {
        "catchment": {
            "center": {
                "latitude": geography.latitude,
                "longitude": geography.longitude,
                "coordinate_quality": "OSM_PLACE_PROXY",
            },
            "radius_km": radius_km,
            "method": radial.methodology,
            "category_counts": radial.category_counts,
            "entity_count": len(radial.entities),
            "institution_count": len(institutions),
            "nearest_market": _entity_summary(
                geography.latitude, geography.longitude, nearest_market
            ),
            "nearest_market_route": route.__dict__ if route else None,
            "caveat": radial.caveat,
        },
        "competition": {
            "sector": sector,
            "osm_proxy_count": len(competitors),
            "categories": sorted({item.category for item in competitors}),
            "capacity": None,
            "capacity_confidence": "UNKNOWN",
            "caveat": ("OSM count is an incomplete proxy; it is not incumbent capacity or sales."),
        },
        "limitations": [radial.caveat],
        "sources": {"https://geo2day.com/asia/india/west_bengal.pbf"},
        "data_versions": {
            "DS071-OSM": metadata.get("source_sha256", "UNKNOWN"),
            "osm_extractor": metadata.get("extractor_version", "UNKNOWN"),
        },
    }


def _sector_competitors(entities: list[OsmEntity], sector: str) -> list[OsmEntity]:
    sector = sector.casefold()
    if sector in {"dairy", "milk"}:
        categories = {"DAIRY", "FOOD_SHOP", "SUPERMARKET", "GENERAL_SHOP"}
    else:
        categories = {"GENERAL_SHOP", "MARKET"}
    return [entity for entity in entities if entity.category in categories]


def _nearest_entity(latitude: float, longitude: float, entities: list[OsmEntity]):
    return min(
        entities,
        key=lambda item: haversine_km(latitude, longitude, item.latitude, item.longitude),
        default=None,
    )


def _entity_summary(latitude: float, longitude: float, entity: OsmEntity | None):
    if entity is None:
        return None
    return {
        "osm_id": f"{entity.osm_type}/{entity.osm_id}",
        "name": entity.name,
        "category": entity.category,
        "latitude": entity.latitude,
        "longitude": entity.longitude,
        "straight_line_distance_km": haversine_km(
            latitude, longitude, entity.latitude, entity.longitude
        ),
    }


def _derive_swot(evidence, spatial, baseline, bottlenecks, gates):
    strengths = []
    weaknesses = [gate.message for gate in gates if gate.blocking]
    opportunities = []
    threats = []
    observed = [item for item in evidence if item.evidence_type == EvidenceType.OBSERVED]
    if observed:
        strengths.append(f"{len(observed)} source-linked observed records are attached.")
    if spatial["catchment"]:
        strengths.append(
            f"Indexed OSM catchment contains {spatial['catchment']['entity_count']} proxy entities."
        )
        if spatial["competition"].get("capacity") is None:
            threats.append("Competitor capacity is unknown; OSM count cannot replace it.")
    if baseline and baseline.unserved_demand > 0:
        opportunities.append(
            f"The exact flow model measures {baseline.unserved_demand:g} units of unserved demand."
        )
    if bottlenecks:
        opportunities.append(
            f"{len(bottlenecks)} source-linked marginal capacity repairs were evaluated."
        )
    return {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "opportunities": opportunities,
        "threats": threats,
    }


def _git_commit() -> str:
    configured = os.environ.get("SIH26091_GIT_COMMIT")
    if configured:
        return configured
    try:
        root = Path(__file__).resolve().parents[1]
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
            timeout=2,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "UNKNOWN"

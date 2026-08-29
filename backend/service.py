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
from backend.engine.uncertainty import (
    compare_candidates_under_uncertainty,
    failure_boundaries,
    sensitivity_analysis,
)
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
from backend.pipeline.sector_factors import sector_factors
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
        float(automatic.contribution_margin_per_unit)
        if automatic.contribution_margin_per_unit is not None
        else request.contribution_margin_per_unit
    )
    automatic_unit_price = float(automatic.unit_price or 1.0)
    automatic_variable_cost = max(0.0, automatic_unit_price - automatic_margin)
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
            unit_price=automatic_unit_price,
            variable_cost_per_unit=automatic_variable_cost,
            fixed_monthly_cost=float(selected.monthly_opex),
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
    computed_sensitivities = []
    if (
        request.analysis_mode == "deep"
        and selected
        and candidates
        and automatic.demand.central
        and automatic_margin > 0
    ):
        robust_analysis = compare_candidates_under_uncertainty(
            candidates,
            available_capital=float(entrepreneur.available_capital),
            monthly_demand=float(automatic.demand.central),
            margin_share=automatic_margin,
            seed_key=f"{geography.geo_id}:{sector}:deep-v1",
            unit_price=automatic_unit_price,
            variable_cost_per_unit=automatic_variable_cost,
            minimum_monthly_income=float(entrepreneur.minimum_monthly_income or 0),
        )
        computed_boundaries = failure_boundaries(
            selected,
            available_capital=float(entrepreneur.available_capital),
            monthly_demand=float(automatic.demand.central),
            margin_share=automatic_margin,
            unit_price=automatic_unit_price,
            variable_cost_per_unit=automatic_variable_cost,
        )
        computed_sensitivities = sensitivity_analysis(
            selected,
            available_capital=float(entrepreneur.available_capital),
            monthly_demand=float(automatic.demand.central),
            margin_share=automatic_margin,
            unit_price=automatic_unit_price,
            variable_cost_per_unit=automatic_variable_cost,
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
    intelligence = _sector_intelligence(sector, spatial, selected)
    entry_difficulty = _entry_difficulty(selected, entrepreneur, confidence, intelligence)
    premortem = _premortem(
        selected,
        twin,
        computed_sensitivities,
        spatial["competition"],
        automatic.demand,
    )
    swot = _derive_swot(
        selected,
        twin,
        automatic,
        spatial,
        baseline,
        bottlenecks,
        computed_sensitivities,
        gates,
    )
    action_plan = _action_plan(selected, automatic, computed_boundaries, premortem)
    decision = VentureDecision(
        analysis_id=analysis_id,
        created_at=now,
        status=status,
        methodology_version="decision-v6",
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
        sector_intelligence=intelligence,
        entry_difficulty=entry_difficulty,
        premortem=premortem,
        action_plan=action_plan,
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
        constraint_analysis=(
            {
                "binding_constraints": mvv.binding_constraints,
                "inverse_analysis": mvv.inverse_analysis,
                "minimum_relaxation": mvv.constraint_relaxation,
                "interpretation": (
                    "Exact only over the generated candidate configurations; debt is a ceiling, "
                    "not a target."
                ),
            }
            if mvv
            else {}
        ),
        loan_terms=loan_terms,
        official_finance=[finance_screen, ahidf_screen],
        prudent_financing=(
            {
                "estimated_project_cost": selected.investment,
                "available_own_capital": float(entrepreneur.available_capital),
                "own_capital_deployed": min(
                    selected.investment, float(entrepreneur.available_capital)
                ),
                "capital_preserved_as_reserve": max(
                    float(entrepreneur.available_capital) - selected.investment, 0
                ),
                "illustrative_financing_requirement": max(
                    selected.investment - float(entrepreneur.available_capital), 0
                ),
                "maximum_acceptable_debt": entrepreneur.acceptable_debt,
                "wording": "Potentially eligible / illustrative structure; not lender approval.",
                "financial_metrics": financial_metrics,
                **_cost_breakdowns(selected, twin, sector),
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
        sensitivity_analysis=computed_sensitivities,
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
        staged_plan=_staged_plan(selected, twin, computed_boundaries),
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
        methodology_version="decision-v6",
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
    direct_competitors, indirect_competitors = _sector_competitors(radial.entities, sector)
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
    nearest_institutions = sorted(
        institutions,
        key=lambda item: haversine_km(
            geography.latitude, geography.longitude, item.latitude, item.longitude
        ),
    )[:10]
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
            "osm_proxy_count": len(direct_competitors) + len(indirect_competitors),
            "direct_count": len(direct_competitors),
            "indirect_count": len(indirect_competitors),
            "categories": sorted(
                {item.category for item in [*direct_competitors, *indirect_competitors]}
            ),
            "likely_direct_competitors": [
                _entity_summary(geography.latitude, geography.longitude, item)
                for item in _nearest_entities(
                    geography.latitude,
                    geography.longitude,
                    direct_competitors,
                    12,
                )
            ],
            "likely_indirect_competitors": [
                _entity_summary(geography.latitude, geography.longitude, item)
                for item in _nearest_entities(
                    geography.latitude,
                    geography.longitude,
                    indirect_competitors,
                    12,
                )
            ],
            "capacity": None,
            "capacity_confidence": "UNKNOWN",
            "competition_intensity": _competition_intensity(len(direct_competitors), radius_km),
            "intensity_confidence": "LOW_OSM_PROXY",
            "hhi": None,
            "caveat": (
                "OSM candidates are deduplicated direct/indirect proxies; capacity, sales and "
                "market shares remain unknown, so HHI is not calculated."
            ),
        },
        "limitations": [radial.caveat],
        "sources": {"https://geo2day.com/asia/india/west_bengal.pbf"},
        "data_versions": {
            "DS071-OSM": metadata.get("source_sha256", "UNKNOWN"),
            "osm_extractor": metadata.get("extractor_version", "UNKNOWN"),
        },
        "institutions": [
            _entity_summary(geography.latitude, geography.longitude, item)
            for item in nearest_institutions
        ],
        "markets": [
            _entity_summary(geography.latitude, geography.longitude, item)
            for item in _nearest_entities(geography.latitude, geography.longitude, markets, 10)
        ],
    }


def _sector_competitors(
    entities: list[OsmEntity], sector: str
) -> tuple[list[OsmEntity], list[OsmEntity]]:
    factors = sector_factors(sector)
    direct_categories = factors.direct_osm_categories if factors else frozenset()
    indirect_categories = factors.indirect_osm_categories if factors else frozenset()
    direct = [entity for entity in entities if entity.category in direct_categories]
    indirect = [
        entity
        for entity in entities
        if entity.category in indirect_categories and entity.category not in direct_categories
    ]
    return direct, indirect


def _nearest_entities(
    latitude: float,
    longitude: float,
    entities: list[OsmEntity],
    limit: int,
) -> list[OsmEntity]:
    return sorted(
        entities,
        key=lambda item: haversine_km(latitude, longitude, item.latitude, item.longitude),
    )[:limit]


def _competition_intensity(direct_count: int, radius_km: float) -> str:
    density = direct_count / max(3.14159 * radius_km * radius_km, 1)
    if direct_count == 0:
        return "NO_OSM_DIRECT_CANDIDATE_FOUND"
    if density < 0.03:
        return "LOW_PROXY_DENSITY"
    if density < 0.12:
        return "MEDIUM_PROXY_DENSITY"
    return "HIGH_PROXY_DENSITY"


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


def _sector_intelligence(sector: str, spatial: dict, selected) -> dict:
    factors = sector_factors(sector)
    if factors is None:
        return {}
    channels = []
    for index, channel in enumerate(factors.channels):
        channels.append(
            {
                "channel": channel,
                "rank": index + 1,
                "role": "PRIMARY" if index == 0 else "SECONDARY",
                "score_basis": (
                    "sector-logic comparison of reach, margin, working capital, reliability "
                    "and operating complexity; no local channel transaction data"
                ),
                "confidence": "LOW_ASSUMPTION_BASED",
            }
        )
    return {
        "factor_registry_version": "sector-factor-registry-v1",
        "customer_segments": list(factors.customer_segments),
        "supplier_types": list(factors.supplier_types),
        "distribution_channels": channels,
        "operational_factors": list(factors.operational_factors),
        "weather_factors": list(factors.weather_factors),
        "insurance_options": list(factors.insurance),
        "nearest_markets": spatial.get("markets", []),
        "institutional_buyer_candidates": spatial.get("institutions", []),
        "selected_equipment": selected.primitives[0].equipment if selected else [],
        "segmentation_caveat": (
            "Segments are defensible sector groups, not measured local percentage shares."
        ),
    }


def _entry_difficulty(selected, profile, confidence, intelligence: dict) -> dict:
    if selected is None:
        return {}
    primitive = selected.primitives[0]
    score = 0
    reasons = []
    capital_ratio = selected.investment / max(float(profile.available_capital), 1)
    if capital_ratio > 1:
        score += 2
        reasons.append("requires financing above own capital")
    elif capital_ratio > 0.65:
        score += 1
        reasons.append("uses a large share of available capital")
    if primitive.cash_conversion_cycle_days > 25:
        score += 2
        reasons.append("long cash-conversion cycle")
    elif primitive.cash_conversion_cycle_days > 14:
        score += 1
        reasons.append("moderate inventory/receivable cycle")
    if len(primitive.licence_assumptions) >= 2:
        score += 1
        reasons.append("multiple approvals must be verified")
    if primitive.staff > 2:
        score += 1
        reasons.append("multi-person operating requirement")
    if confidence != ConfidenceLevel.HIGH:
        score += 1
        reasons.append("important locality inputs remain benchmark-adjusted")
    label = "LOW" if score <= 2 else "MEDIUM" if score <= 5 else "HIGH"
    return {
        "label": label,
        "score": score,
        "scale": "0-8 rule-based planning score",
        "reasons": reasons,
        "confidence": "MEDIUM_RULE_BASED" if intelligence else "LOW",
    }


def _premortem(selected, twin, sensitivities, competition, demand) -> list[dict]:
    if selected is None:
        return []
    causes = []
    prevention = {
        "demand": "Pilot weekly sales before fixed-asset purchase and stop below the sales floor.",
        "selling_price": "Validate current customer prices and negotiate supplier terms first.",
        "variable_cost": "Obtain two supplier quotes and cap procurement cost per unit.",
        "fixed_opex": "Avoid a long lease until three months of demand are demonstrated.",
    }
    for item in sensitivities[:3]:
        variable = item["variable"]
        causes.append(
            {
                "rank": len(causes) + 1,
                "cause": f"Adverse {variable.replace('_', ' ')} moved cash below plan.",
                "evidence": (
                    f"Controlled +/-{item['perturbation'] * 100:.0f}% perturbation; "
                    f"elasticity {item['elasticity']:.2f}."
                    if item["elasticity"] is not None
                    else "Controlled perturbation around the central planning case."
                ),
                "prevention": prevention[variable],
            }
        )
    if competition.get("direct_count", 0) > 0:
        causes.append(
            {
                "rank": len(causes) + 1,
                "cause": "Customer acquisition was slower because nearby alternatives existed.",
                "evidence": (
                    f"{competition['direct_count']} direct OSM proxy candidates in the catchment; "
                    "capacity remains unknown."
                ),
                "prevention": (
                    "Interview customers and differentiate channel/service before launch."
                ),
            }
        )
    if demand.status == "MODELLED_BENCHMARK":
        causes.append(
            {
                "rank": len(causes) + 1,
                "cause": "The regional benchmark did not translate into real locality sales.",
                "evidence": (
                    "Demand is modelled from a regional survey prior, not transaction data."
                ),
                "prevention": (
                    "Run a small paid pilot and replace the benchmark with observed sales."
                ),
            }
        )
    return causes[:5]


def _derive_swot(
    selected,
    twin,
    automatic,
    spatial,
    baseline,
    bottlenecks,
    sensitivities,
    gates,
):
    strengths = []
    weaknesses = []
    opportunities = []
    threats = []
    if selected and twin:
        primitive = selected.primitives[0]
        if twin.investment_payback_month and twin.investment_payback_month <= 24:
            strengths.append(f"Central planning payback is {twin.investment_payback_month} months.")
        if primitive.cash_conversion_cycle_days <= 14:
            strengths.append(
                f"The modelled cash-conversion cycle is short at "
                f"{primitive.cash_conversion_cycle_days:g} days."
            )
        if twin.months[11].operating_cash_flow > 0:
            strengths.append("Month-12 operating cash flow is positive in the central model.")
        if selected.investment > 0 and primitive.working_capital / selected.investment > 0.5:
            weaknesses.append("More than half of project cost is tied up in working capital.")
        if primitive.staff > 2:
            weaknesses.append(f"The starting configuration coordinates {primitive.staff} people.")
    if automatic.demand.status == "MODELLED_BENCHMARK":
        weaknesses.append("Local demand is a regional benchmark, not observed locality sales.")
    if baseline and baseline.unserved_demand > 0:
        opportunities.append(
            f"The planning graph contains {baseline.unserved_demand:g} units of unserved flow."
        )
    factors = sector_factors(selected.primitives[0].sector_compatibility[0]) if selected else None
    if factors and len(factors.channels) > 1:
        opportunities.append(
            f"A secondary {factors.channels[1]} channel can diversify the primary route."
        )
    if bottlenecks:
        opportunities.append(f"{len(bottlenecks)} marginal capacity repair options were evaluated.")
    if sensitivities:
        top = sensitivities[0]
        label = top["variable"].replace("_", " ").title()
        elasticity = top.get("elasticity")
        if elasticity is None:
            threats.append(f"{label} is the strongest tested cash driver.")
        else:
            threats.append(
                f"{label} is the strongest tested cash driver (elasticity {elasticity:.2f})."
            )
    if spatial["competition"].get("capacity") is None:
        threats.append("Competitor capacity and market shares remain unknown.")
    threats.extend(gate.message for gate in gates if gate.blocking)
    return {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "opportunities": opportunities,
        "threats": threats,
    }


def _cost_breakdowns(selected, twin, sector: str) -> dict:
    if selected is None:
        return {}
    primitive = selected.primitives[0]
    factors = sector_factors(sector)
    capex = float(primitive.capex)
    capex_breakdown = {
        "equipment_and_fixtures": capex * 0.70,
        "installation_and_setup": capex * 0.15,
        "premises_deposit_and_basic_fitout": capex * 0.10,
        "licensing_and_contingency": capex * 0.05,
    }
    fixed_total = float(primitive.monthly_opex)
    variable_total = twin.months[11].variable_cost if twin else None
    fixed_breakdown = (
        {name: fixed_total * share for name, share in factors.fixed_cost_shares}
        if factors
        else {"fixed_overhead": fixed_total}
    )
    variable_breakdown = (
        {name: variable_total * share for name, share in factors.variable_cost_shares}
        if factors and variable_total is not None
        else {}
    )
    return {
        "capex_breakdown": capex_breakdown,
        "monthly_opex_breakdown": {
            "fixed": fixed_breakdown,
            "variable_month_12": variable_breakdown,
            "note": (
                "Benchmark-adjusted allocation of ASUSE-derived cost totals; obtain current "
                "local quotes before spending."
            ),
        },
        "working_capital": {
            "minimum_modelled": float(primitive.working_capital),
            "recommended_with_15pct_buffer": float(primitive.working_capital) * 1.15,
            "cash_conversion_cycle_days": primitive.cash_conversion_cycle_days,
        },
        "cost_basis": {
            "status": "BENCHMARK_ADJUSTED",
            "source": "ASUSE calendar-2025 district/sector/NIC2 prior",
            "confidence": "LOW",
            "current_quote_required": True,
        },
    }


def _action_plan(selected, automatic, boundaries, premortem) -> dict[str, list[str]]:
    if selected is None:
        return {}
    primitive = selected.primitives[0]
    demand_boundary = next(
        (item for item in boundaries if item["variable"] == "monthly_demand"), None
    )
    return {
        "before_starting": [
            "Validate at least two current supplier quotations and one customer selling price.",
            "Confirm premises, power/water/internet needs and every listed licence with authority.",
            f"Ring-fence at least INR {primitive.working_capital:,.0f} as working capital.",
        ],
        "day_1_7": [
            "Interview at least ten target customers and record purchase frequency and price.",
            "Run a paid micro-pilot before buying the full equipment configuration.",
        ],
        "first_30_days": [
            (
                "Track daily sales, contribution margin, inventory days, cash and "
                "rejected/wasted stock."
            ),
            "Reconcile supplier invoices and customer receipts weekly.",
        ],
        "months_2_3": [
            "Continue only if contribution margin and closing cash remain non-negative.",
            "Add the secondary channel only after the primary channel repeats reliably.",
        ],
        "months_4_6": [
            "Compare realized sales with the model interval and recalibrate before expansion.",
            "Build at least two active suppliers and avoid single-buyer dependence.",
        ],
        "stop_or_reconsider": [
            (
                f"Reconsider if monthly sales remain below {demand_boundary['threshold']:,.0f}."
                if demand_boundary and demand_boundary["threshold"] is not None
                else "Use the tested demand-deterioration statement as the sales stop rule."
            ),
            *(item["prevention"] for item in premortem[:2]),
        ],
    }


def _staged_plan(selected, twin, boundaries) -> list[str]:
    if selected is None or twin is None:
        return []
    primitive = selected.primitives[0]
    reserve_target = max(float(primitive.monthly_opex) * 3, float(primitive.working_capital) * 0.25)
    stable_month = next(
        (
            month.month
            for month in twin.months
            if month.closing_cash >= reserve_target
            and month.sales_volume >= float(selected.total_capacity) * 0.70
        ),
        None,
    )
    boundary_note = next(
        (item["interpretation"] for item in boundaries if item["variable"] == "monthly_demand"),
        "Demand boundary was not computed in Quick mode.",
    )
    return [
        "Stage 0: validate prices, suppliers and paid demand using shared/rented assets.",
        (
            "Stage 1: deploy the selected configuration and preserve "
            f"INR {reserve_target:,.0f} reserve."
        ),
        (
            f"Stage 2: the central model first supports a 70% utilization plus reserve trigger "
            f"in month {stable_month}."
            if stable_month
            else "Stage 2: do not expand within 36 months because the reserve/utilization trigger "
            "is not reached."
        ),
        f"Stop-rule context: {boundary_note}",
    ]


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

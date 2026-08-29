from __future__ import annotations

from pydantic import BaseModel, Field

from backend.models.decision import EvidenceGapCode, EvidenceGate
from backend.models.economic_graph import EconomicEdge, EconomicGraph, EconomicNode, NodeType
from backend.models.evidence import (
    ConfidenceLevel,
    EstimateInterval,
    EvidenceRecord,
    FreshnessStatus,
)
from backend.models.profile import EntrepreneurProfile
from backend.models.venture import PrimitiveType, VentureCandidate, VenturePrimitive
from backend.pipeline.sector_factors import sector_factors
from backend.pipeline.sector_library import SectorAdapter, resolve_adapter


class AutomaticBuildResult(BaseModel):
    demand: EstimateInterval
    supply: EstimateInterval
    price: EstimateInterval
    graph: EconomicGraph | None = None
    candidates: list[VentureCandidate] = Field(default_factory=list)
    gates: list[EvidenceGate] = Field(default_factory=list)
    graph_summary: dict = Field(default_factory=dict)
    model_versions: dict[str, str] = Field(default_factory=dict)
    unit_price: float | None = None
    contribution_margin_per_unit: float | None = None


def build_automatic_inputs(
    *,
    geo_id: str,
    sector: str,
    evidence: list[EvidenceRecord],
    profile: EntrepreneurProfile,
) -> AutomaticBuildResult:
    normalized_sector = sector.casefold().strip()
    if normalized_sector not in {"dairy", "milk"}:
        adapter = resolve_adapter(sector)
        if adapter is not None:
            return _build_benchmark_adapter(geo_id, adapter, evidence, profile)
        insufficient = EstimateInterval.insufficient(
            "unknown", "sector-adapter-v2", f"No production adapter for {sector}."
        )
        return AutomaticBuildResult(
            demand=insufficient,
            supply=insufficient,
            price=insufficient,
            gates=[
                EvidenceGate(
                    code=EvidenceGapCode.UNSUPPORTED_SECTOR,
                    message=f"Sector adapter is not implemented for {sector}.",
                )
            ],
            model_versions={"sector_adapter": "registry-v2"},
        )
    return _build_dairy(geo_id, evidence, profile)


def _numeric(
    evidence: list[EvidenceRecord],
    variable: str,
    allowed_freshness: set[FreshnessStatus] | None = None,
) -> EvidenceRecord | None:
    matches = [
        item
        for item in evidence
        if item.variable == variable
        and isinstance(item.value, (int, float))
        and not isinstance(item.value, bool)
        and (allowed_freshness is None or item.freshness_status in allowed_freshness)
    ]
    return matches[0] if len(matches) == 1 else None


def _interval(
    evidence: list[EvidenceRecord],
    variable: str,
    unit: str,
    method: str,
    allowed_freshness: set[FreshnessStatus] | None = None,
) -> EstimateInterval:
    record = _numeric(evidence, variable, allowed_freshness)
    if record is None:
        return EstimateInterval.insufficient(unit, method, f"Missing {variable}.")
    value = float(record.value)
    lower = float(record.attributes.get("lower", value))
    upper = float(record.attributes.get("upper", value))
    return EstimateInterval(
        central=value,
        lower=lower,
        upper=upper,
        unit=unit,
        confidence=record.confidence,
        evidence_ids=[record.id],
        method_version=method,
        status="EVIDENCE_DERIVED",
    )


def _demand_interval(evidence: list[EvidenceRecord]) -> EstimateInterval:
    direct = _interval(
        evidence,
        "monthly_dairy_demand_litres",
        "litres/month",
        "dairy-demand-direct-v1",
        {FreshnessStatus.CURRENT, FreshnessStatus.RECENT, FreshnessStatus.PROJECTED},
    )
    if direct.status != "INSUFFICIENT_EVIDENCE":
        return direct
    rate = _numeric(
        evidence,
        "monthly_liquid_milk_litres_per_capita_prior",
        {FreshnessStatus.RECENT, FreshnessStatus.CURRENT},
    )
    if rate is None:
        return EstimateInterval.insufficient(
            "litres/month", "hces-direct-weighted-district-sector-v1", "Missing HCES rate prior."
        )
    population = _numeric(evidence, "population_projected_2026") or _numeric(
        evidence, "population_current"
    )
    if population is not None:
        status = "PROJECTED" if population.variable == "population_projected_2026" else "ESTIMATED"
        return _multiply_rate_population(rate, population, status=status)
    historical = _numeric(evidence, "population_observed_2011")
    if historical is not None:
        projected = _project_population_2026(historical)
        return EstimateInterval(
            central=float(rate.value) * projected["central"],
            lower=float(rate.attributes.get("lower", rate.value)) * projected["lower"],
            upper=float(rate.attributes.get("upper", rate.value)) * projected["upper"],
            unit="litres/month",
            confidence=ConfidenceLevel.LOW,
            evidence_ids=[rate.id, historical.id],
            method_version="hces-rate-times-census-growth-scenario-v1",
            status="PROJECTED",
            notes=[
                "Census 2011 is the structural population anchor, not a current observation.",
                "Population is projected to 2026 with explicit rural/urban compound-growth "
                "scenarios; no boundary-change adjustment is available.",
                f"Population projection: {projected['lower']:.0f}–{projected['upper']:.0f} "
                f"(central {projected['central']:.0f}).",
            ],
        )
    return EstimateInterval.insufficient(
        "litres/month",
        "hces-direct-weighted-district-sector-v1",
        "HCES rate exists, but no locality population baseline or current projection is linked.",
    )


def _multiply_rate_population(
    rate: EvidenceRecord, population: EvidenceRecord, *, status: str
) -> EstimateInterval:
    rate_value = float(rate.value)  # type: ignore[arg-type]
    population_value = float(population.value)  # type: ignore[arg-type]
    rate_lower = float(rate.attributes.get("lower", rate_value))
    rate_upper = float(rate.attributes.get("upper", rate_value))
    population_lower = float(population.attributes.get("lower", population_value))
    population_upper = float(population.attributes.get("upper", population_value))
    return EstimateInterval(
        central=rate_value * population_value,
        lower=rate_lower * population_lower,
        upper=rate_upper * population_upper,
        unit="litres/month",
        confidence=_lower_confidence(rate.confidence, population.confidence),
        evidence_ids=[rate.id, population.id],
        method_version="hces-rate-times-population-v1",
        status=status,
    )


def _project_population_2026(record: EvidenceRecord) -> dict[str, float]:
    rural = str(record.attributes.get("rural_urban", "RURAL")).casefold() == "rural"
    rates = (0.006, 0.011, 0.016) if rural else (0.010, 0.017, 0.024)
    base = float(record.value)  # type: ignore[arg-type]
    years = 15
    return {
        "lower": base * ((1 + rates[0]) ** years),
        "central": base * ((1 + rates[1]) ** years),
        "upper": base * ((1 + rates[2]) ** years),
    }


def _build_dairy(
    geo_id: str, evidence: list[EvidenceRecord], profile: EntrepreneurProfile
) -> AutomaticBuildResult:
    demand = _demand_interval(evidence)
    supply = _dairy_supply_interval(evidence)
    price, contribution_margin = _dairy_price_and_margin(evidence)
    gates = []
    if demand.status not in {"EVIDENCE_DERIVED", "ESTIMATED", "PROJECTED"}:
        gates.append(
            EvidenceGate(
                code=EvidenceGapCode.NO_DEMAND_EVIDENCE,
                message=(
                    "No current defensible locality dairy-demand estimate is available. HCES may "
                    "supply a district/sector rate, but a current or explicitly projected locality "
                    "population is still required."
                ),
                required_variables=[
                    "monthly_liquid_milk_litres_per_capita_prior",
                    "population_projected_2026",
                ],
            )
        )
    if supply.status == "INSUFFICIENT_EVIDENCE":
        gates.append(
            EvidenceGate(
                code=EvidenceGapCode.NO_SUPPLY_EVIDENCE,
                message=(
                    "No official productive milk-output estimate is linked. Total livestock "
                    "stock is intentionally not treated as milk supply."
                ),
                required_variables=["district_annual_milk_production_kg"],
            )
        )
    if price.status == "INSUFFICIENT_EVIDENCE":
        gates.append(
            EvidenceGate(
                code=EvidenceGapCode.NO_PRICE_EVIDENCE,
                message="No current local milk price or defensible enterprise-margin prior exists.",
                required_variables=["milk_price_inr_per_litre"],
            )
        )
    gates.extend(
        [
            EvidenceGate(
                code=EvidenceGapCode.NO_PRICE_EVIDENCE,
                message=(
                    "Current farmgate, procurement, wholesale and retail prices are not linked "
                    "at this locality. The cash model uses an ASUSE enterprise-margin benchmark; "
                    "validate current prices before spending."
                ),
                blocking=False,
                required_variables=["current_local_milk_prices"],
            ),
            EvidenceGate(
                code=EvidenceGapCode.NO_ROUTE_COST_EVIDENCE,
                message=(
                    "Current route cost, travel time and chilling availability are unknown; "
                    "validate the selected route and spoilage controls in a paid pilot."
                ),
                blocking=False,
                required_variables=["transport_cost_inr_per_litre", "route_time_minutes"],
            ),
        ]
    )

    graph = None
    graph_summary = {}
    graph_ready = demand.central is not None and supply.central is not None
    if graph_ready:
        demand_id = demand.evidence_ids[0]
        supply_id = supply.evidence_ids[0]
        graph = EconomicGraph(
            graph_id=f"auto:{geo_id}:dairy:v2",
            commodity="milk",
            unit="litres/month",
            nodes=[
                EconomicNode(
                    node_id="local-producers",
                    node_type=NodeType.PRODUCER_CLUSTER,
                    geo_id=geo_id,
                    commodity="milk",
                    supply=float(supply.upper or supply.central or 0),
                    confidence=_confidence_value(supply.confidence),
                    evidence_ids=[supply_id],
                ),
                EconomicNode(
                    node_id="local-demand",
                    node_type=NodeType.CUSTOMER_CLUSTER,
                    geo_id=geo_id,
                    commodity="milk",
                    demand=float(demand.central or 0),
                    confidence=_confidence_value(demand.confidence),
                    evidence_ids=[demand_id],
                ),
            ],
            edges=[
                EconomicEdge(
                    edge_id="incumbent-local-service",
                    source="local-producers",
                    target="local-demand",
                    commodity="milk",
                    capacity=float(supply.central),
                    unit_cost=0,
                    confidence=_confidence_value(supply.confidence),
                    evidence_ids=list(supply.evidence_ids),
                )
            ],
            methodology_version="automatic-dairy-graph-v2",
        )
        graph_summary = {
            "node_count": len(graph.nodes),
            "edge_count": len(graph.edges),
            "commodity": graph.commodity,
            "unit": graph.unit,
            "builder": graph.methodology_version,
            "interpretation": (
                "HCES consumption demand versus official 2024-25 district productive output, "
                "scaled to locality population and marketed/accessibility scenarios."
            ),
        }

    candidates = _dairy_candidates(geo_id, evidence, profile, graph, demand, supply)
    if graph is not None and not candidates:
        gates.append(
            EvidenceGate(
                code=EvidenceGapCode.NO_VENTURE_COST_EVIDENCE,
                message="No source-versioned venture cost/capacity configuration is available.",
                required_variables=[
                    "asuse_nic46_total_fixed_assets_owned_prior",
                    "asuse_nic46_annual_input_inr_prior",
                ],
            )
        )
    gates.append(
        EvidenceGate(
            code=EvidenceGapCode.NO_CURRENT_FINANCE_RULE,
            message=(
                "Current PMMY category screening is available, but lender-specific verified "
                "interest/tenure and underwriting are absent for a real financing decision."
            ),
            blocking=False,
        )
    )
    return AutomaticBuildResult(
        demand=demand,
        supply=supply,
        price=price,
        graph=graph,
        candidates=candidates,
        gates=gates,
        graph_summary=graph_summary,
        model_versions={
            "sector_adapter": "dairy-v2",
            "demand": demand.method_version,
            "supply": supply.method_version,
            "price": price.method_version,
            "graph_builder": "automatic-dairy-graph-v2",
            "cost_library": "asuse-nic46-benchmark-dairy-v1",
        },
        unit_price=float(price.central) if price.central is not None else None,
        contribution_margin_per_unit=contribution_margin,
    )


def _dairy_supply_interval(evidence: list[EvidenceRecord]) -> EstimateInterval:
    direct = _interval(
        evidence,
        "reachable_milk_supply_litres_month",
        "litres/month",
        "dairy-supply-direct-v1",
        {FreshnessStatus.CURRENT, FreshnessStatus.RECENT, FreshnessStatus.PROJECTED},
    )
    if direct.status != "INSUFFICIENT_EVIDENCE":
        return direct
    production = _numeric(
        evidence,
        "district_annual_milk_production_kg",
        {FreshnessStatus.CURRENT, FreshnessStatus.RECENT},
    )
    population = _numeric(evidence, "population_projected_2026") or _numeric(
        evidence, "population_current"
    )
    if population is None:
        historical = _numeric(evidence, "population_observed_2011")
        if historical is None:
            return EstimateInterval.insufficient(
                "litres/month",
                "wb-ard-production-market-access-v1",
                "Official district production exists but locality population is unavailable.",
            )
        projected = _project_population_2026(historical)
        locality_population = projected["central"]
        population_id = historical.id
    else:
        locality_population = float(population.value)
        population_id = population.id
    if production is None:
        return EstimateInterval.insufficient(
            "litres/month",
            "wb-ard-production-market-access-v1",
            "Missing official district productive milk-output estimate.",
        )
    attributes = production.attributes
    district_anchor = attributes.get("district_population_observed_2011")
    if district_anchor:
        district_population = float(district_anchor) * (1.011**14)
        annual_output = float(production.value)
        anchor_note = "district production divided by linked district population anchor"
    else:
        district_population = float(attributes["state_population_observed_2011"]) * (1.011**14)
        annual_output = float(attributes["state_total_kg"])
        anchor_note = (
            "state per-capita fallback because the current-district crosswalk is incomplete"
        )
    gross_monthly_equivalent = annual_output / district_population * locality_population / 12
    # Official production is productive output. These scenarios apply marketed-surplus and
    # physical-accessibility factors; total livestock counts never enter the supply equation.
    lower = gross_monthly_equivalent * 0.08
    central = gross_monthly_equivalent * 0.16
    upper = gross_monthly_equivalent * 0.30
    return EstimateInterval(
        central=central,
        lower=lower,
        upper=upper,
        unit="litres/month",
        confidence=ConfidenceLevel.LOW,
        evidence_ids=[production.id, population_id],
        method_version="wb-ard-production-market-access-v1",
        status="MODELLED_ACCESSIBLE_SUPPLY",
        notes=[
            "Official 2024-25 productive milk output is used; livestock stock is not supply.",
            (
                "Reachable marketed supply applies a central 16% and 8%–30% combined "
                "marketed-surplus/accessibility scenario."
            ),
            f"Population allocation uses {anchor_note}.",
            "No locality collection-route or chilling-capacity observation is available.",
        ],
    )


def _dairy_price_and_margin(
    evidence: list[EvidenceRecord],
) -> tuple[EstimateInterval, float | None]:
    output = _numeric(evidence, "asuse_nic46_annual_output_inr_prior")
    inputs = _numeric(evidence, "asuse_nic46_annual_input_inr_prior")
    expenditure = _numeric(evidence, "monthly_liquid_milk_expenditure_inr_per_capita_prior")
    quantity = _numeric(evidence, "monthly_liquid_milk_litres_per_capita_prior")
    if (
        output is None
        or inputs is None
        or expenditure is None
        or quantity is None
        or float(output.value) <= 0
        or float(quantity.value) <= 0
    ):
        return (
            EstimateInterval.insufficient(
                "INR/litre",
                "hces-price-asuse-margin-v1",
                "HCES milk unit value or ASUSE NIC46 margin prior is unavailable.",
            ),
            None,
        )
    margin = max(0.08, min(0.35, (float(output.value) - float(inputs.value)) / float(output.value)))
    unit_value = float(expenditure.value) / float(quantity.value)
    return (
        EstimateInterval(
            central=unit_value,
            lower=unit_value * 0.80,
            upper=unit_value * 1.20,
            unit="INR/litre",
            confidence=ConfidenceLevel.LOW,
            evidence_ids=[expenditure.id, quantity.id, output.id, inputs.id],
            method_version="hces-price-asuse-margin-v1",
            status="RECENT_SURVEY_UNIT_VALUE",
            notes=[
                "HCES 2023-24 expenditure divided by quantity; not a current locality quote.",
                "Contribution per litre combines this unit value with an ASUSE NIC46 margin prior.",
            ],
        ),
        unit_value * margin,
    )


def _dairy_candidates(
    geo_id: str,
    evidence: list[EvidenceRecord],
    profile: EntrepreneurProfile,
    graph: EconomicGraph | None,
    demand: EstimateInterval,
    supply: EstimateInterval,
) -> list[VentureCandidate]:
    if graph is None:
        return []
    direct_variables = {
        name: _numeric(evidence, name, {FreshnessStatus.CURRENT, FreshnessStatus.RECENT})
        for name in (
            "venture_transport_capex_inr",
            "venture_transport_opex_inr_month",
            "venture_transport_capacity_litres_month",
            "venture_working_capital_inr",
        )
    }
    if all(direct_variables.values()):
        direct_ids = [item.id for item in direct_variables.values() if item is not None]
        capex = float(direct_variables["venture_transport_capex_inr"].value)  # type: ignore[union-attr]
        opex = float(direct_variables["venture_transport_opex_inr_month"].value)  # type: ignore[union-attr]
        capacity = float(
            direct_variables["venture_transport_capacity_litres_month"].value  # type: ignore[union-attr]
        )
        working_capital = float(
            direct_variables["venture_working_capital_inr"].value  # type: ignore[union-attr]
        )
        primitive = VenturePrimitive(
            primitive_id="dairy-source-linked-transport-v2",
            primitive_type=PrimitiveType.TRANSPORT,
            sector_compatibility=["dairy"],
            capex=capex,
            monthly_opex=opex,
            working_capital=working_capital,
            capacity=capacity,
            assumption_labels=["SOURCE_LINKED_CONFIGURATION"],
            evidence_ids=direct_ids,
            added_edges=[
                EconomicEdge(
                    edge_id="venture-dairy-source-linked-transport",
                    source="local-producers",
                    target="local-demand",
                    commodity="milk",
                    capacity=capacity,
                    unit_cost=opex / max(capacity, 1),
                    confidence=0.7,
                    evidence_ids=direct_ids,
                    added_by_venture=True,
                )
            ],
        )
        return [
            VentureCandidate(
                candidate_id=f"{geo_id}:dairy:source-linked-transport-v2",
                primitives=[primitive],
                investment=primitive.investment,
                monthly_opex=opex,
                total_capacity=capacity,
            )
        ]
    output = _numeric(evidence, "asuse_nic46_annual_output_inr_prior")
    inputs = _numeric(evidence, "asuse_nic46_annual_input_inr_prior")
    assets = _numeric(evidence, "asuse_nic46_total_fixed_assets_owned_prior")
    workers = _numeric(evidence, "asuse_nic46_workers_prior")
    if not all((output, inputs, assets, workers)):
        return []
    evidence_ids = [output.id, inputs.id, assets.id, workers.id]
    gap = max(float(demand.central or 0) - float(supply.central or 0), 1.0)
    factors = sector_factors("dairy")
    configurations = (
        ("micro-collection", PrimitiveType.AGGREGATION, 0.35, 0.12),
        ("rented-delivery", PrimitiveType.DELIVERY, 0.50, 0.20),
        ("route-distribution", PrimitiveType.DISTRIBUTION, 0.70, 0.34),
        ("collection-chilling", PrimitiveType.STORAGE, 0.95, 0.52),
        ("institutional-supply", PrimitiveType.PROCESSING, 1.20, 0.70),
    )
    funding_reference = max(
        float(profile.available_capital) + float(profile.acceptable_debt or 0), 25_000
    )
    asset_reference = min(float(assets.value) * 0.16, funding_reference * 1.5)
    candidates = []
    for name, primitive_type, cost_scale, capacity_share in configurations:
        project_cost = max(15_000, asset_reference * cost_scale)
        working_capital = project_cost * (0.32 if primitive_type == PrimitiveType.STORAGE else 0.42)
        capex = project_cost - working_capital
        capacity = min(gap, max(gap * capacity_share, 30.0))
        # Variable procurement is already represented by the per-litre contribution margin.
        # This is a bounded fixed-overhead planning allowance, not a current local quote.
        monthly_opex = project_cost * 0.015
        primitive = VenturePrimitive(
            primitive_id=f"dairy-{name}-v2",
            primitive_type=primitive_type,
            sector_compatibility=["dairy"],
            capex=capex,
            monthly_opex=monthly_opex,
            working_capital=working_capital,
            capacity=capacity,
            staff=max(1, round(float(workers.value) * cost_scale)),
            service_radius_km=3 + 9 * cost_scale,
            space_sqft=80 + 180 * cost_scale,
            inventory_days=2,
            receivable_days=5,
            payable_days=3,
            lifetime_months=60,
            residual_value=capex * 0.15,
            licence_assumptions=["FSSAI registration", "local trade registration"],
            equipment=list(factors.equipment) if factors else [],
            supplier_types=list(factors.supplier_types) if factors else [],
            customer_types=list(factors.customer_segments) if factors else [],
            quality_controls=list(factors.quality_controls) if factors else [],
            insurance_options=list(factors.insurance) if factors else [],
            operational_factors=list(factors.operational_factors) if factors else [],
            weather_factors=list(factors.weather_factors) if factors else [],
            required_skills=["milk quality checks", "cold-chain and route discipline"],
            assumption_labels=[
                "OFFICIAL_PRODUCTIVE_OUTPUT_SCALED_TO_LOCALITY",
                "ASUSE_NIC46_COST_BENCHMARK",
                "CURRENT_LOCAL_PRICE_AND_ROUTE_QUOTE_REQUIRED",
            ],
            evidence_ids=evidence_ids,
            added_edges=[
                EconomicEdge(
                    edge_id=f"venture-dairy-{name}",
                    source="local-producers",
                    target="local-demand",
                    commodity="milk",
                    capacity=capacity,
                    unit_cost=monthly_opex / max(capacity, 1),
                    confidence=0.30,
                    evidence_ids=evidence_ids,
                    added_by_venture=True,
                )
            ],
        )
        candidates.append(
            VentureCandidate(
                candidate_id=f"{geo_id}:dairy:{name}-v2",
                primitives=[primitive],
                investment=primitive.investment,
                monthly_opex=monthly_opex,
                total_capacity=capacity,
            )
        )
    return candidates


def _confidence_value(level: ConfidenceLevel) -> float:
    return {
        ConfidenceLevel.HIGH: 0.9,
        ConfidenceLevel.MEDIUM: 0.7,
        ConfidenceLevel.LOW: 0.4,
        ConfidenceLevel.INSUFFICIENT: 0.0,
    }[level]


def _lower_confidence(*levels: ConfidenceLevel) -> ConfidenceLevel:
    return min(levels, key=_confidence_value)


def _build_benchmark_adapter(
    geo_id: str,
    adapter: SectorAdapter,
    evidence: list[EvidenceRecord],
    profile: EntrepreneurProfile,
) -> AutomaticBuildResult:
    """Build a bounded planning case from query-time ASUSE district/sector priors.

    ASUSE values are sampled enterprise benchmarks, not locality totals. The adapter therefore
    uses them only to size a small configuration and labels every output MODELLED_BENCHMARK.
    """
    prefix = f"asuse_nic{adapter.nic2}_"
    factors = sector_factors(adapter.key)
    output = _numeric(evidence, f"{prefix}annual_output_inr_prior")
    inputs = _numeric(evidence, f"{prefix}annual_input_inr_prior")
    assets = _numeric(evidence, f"{prefix}total_fixed_assets_owned_prior")
    workers = _numeric(evidence, f"{prefix}workers_prior")
    if not all((output, inputs, assets, workers)):
        missing = EstimateInterval.insufficient(
            adapter.unit,
            f"{adapter.key}-asuse-adapter-v1",
            "District/sector ASUSE benchmark is unavailable.",
        )
        return AutomaticBuildResult(
            demand=missing,
            supply=missing,
            price=missing,
            gates=[
                EvidenceGate(
                    code=EvidenceGapCode.NO_DEMAND_EVIDENCE,
                    message=(
                        "A district/sector enterprise benchmark is required for this "
                        "planning estimate."
                    ),
                )
            ],
            model_versions={"sector_adapter": f"{adapter.key}-v1"},
        )

    annual_output = max(float(output.value), 1.0)
    annual_input = max(float(inputs.value), 0.0)
    monthly_output = annual_output / 12
    monthly_input = annual_input / 12
    demand_central = monthly_output * adapter.demand_factor
    incumbent = monthly_output * adapter.incumbent_factor
    demand = _benchmark_interval(
        demand_central,
        adapter.unit,
        output,
        f"{adapter.key}-demand-benchmark-v1",
        (
            "Modelled opportunity envelope from a weighted ASUSE district/sector "
            "enterprise-output benchmark; not measured locality demand."
        ),
    )
    supply = _benchmark_interval(
        incumbent,
        adapter.unit,
        output,
        f"{adapter.key}-incumbent-benchmark-v1",
        "Modelled incumbent service envelope; not a census of local businesses.",
    )
    margin_ratio = max(0.08, min(0.45, (annual_output - annual_input) / annual_output))
    price = EstimateInterval(
        central=margin_ratio,
        lower=max(0.03, margin_ratio * 0.75),
        upper=min(0.60, margin_ratio * 1.25),
        unit="gross margin share",
        confidence=ConfidenceLevel.LOW,
        evidence_ids=[output.id, inputs.id],
        method_version=f"{adapter.key}-margin-benchmark-v1",
        status="MODELLED_BENCHMARK",
        notes=[
            "Weighted ASUSE output/input benchmark; not a current local selling-price observation."
        ],
    )

    gap = max(demand_central - incumbent, monthly_output * 0.08)
    graph = EconomicGraph(
        graph_id=f"auto:{geo_id}:{adapter.key}:v1",
        commodity=adapter.commodity,
        unit=adapter.unit,
        nodes=[
            EconomicNode(
                node_id="local-suppliers",
                node_type=NodeType.PRODUCER_CLUSTER,
                geo_id=geo_id,
                commodity=adapter.commodity,
                supply=demand_central,
                confidence=0.4,
                evidence_ids=[output.id],
            ),
            EconomicNode(
                node_id="local-demand",
                node_type=NodeType.CUSTOMER_CLUSTER,
                geo_id=geo_id,
                commodity=adapter.commodity,
                demand=demand_central,
                confidence=0.4,
                evidence_ids=[output.id],
            ),
        ],
        edges=[
            EconomicEdge(
                edge_id="modelled-incumbent-service",
                source="local-suppliers",
                target="local-demand",
                commodity=adapter.commodity,
                capacity=incumbent,
                unit_cost=0,
                confidence=0.35,
                evidence_ids=[output.id],
            )
        ],
        methodology_version=f"automatic-{adapter.key}-graph-v1",
    )

    candidate_scales = (
        ("micro", 0.40),
        ("starter", 0.55),
        ("balanced", 0.75),
        ("growth", 1.0),
        ("expanded", 1.25),
    )
    asset_benchmark = max(float(assets.value), 20_000)
    debt_ceiling = float(profile.acceptable_debt or 0)
    funding_reference = max(float(profile.available_capital) + debt_ceiling, 25_000)
    reference_total = min(
        asset_benchmark * adapter.cost_factor,
        funding_reference * 1.5,
    )
    candidates = []
    for name, scale in candidate_scales:
        target_total = max(reference_total * scale, 12_000)
        working_capital = target_total * adapter.working_capital_share
        capex = target_total - working_capital
        monthly_cost_factor = 1.0
        asset_labels = []
        owned_assets = {item.casefold() for item in profile.assets}
        if "shop" in owned_assets and adapter.primitive in {
            PrimitiveType.RETAIL,
            PrimitiveType.PROCESSING,
        }:
            capex *= 0.92
            monthly_cost_factor *= 0.88
            asset_labels.append("EXISTING_SHOP_REDUCES_SETUP_AND_PREMISES_BENCHMARK")
        if "vehicle" in owned_assets and adapter.primitive in {
            PrimitiveType.AGGREGATION,
            PrimitiveType.DELIVERY,
            PrimitiveType.DISTRIBUTION,
            PrimitiveType.TRANSPORT,
        }:
            capex *= 0.82
            asset_labels.append("EXISTING_VEHICLE_REDUCES_TRANSPORT_SETUP_BENCHMARK")
        capacity = min(gap, monthly_output * adapter.capacity_factor * scale)
        # Variable procurement is represented by the output/input margin interval in the
        # digital twin. Candidate monthly_opex is the fixed-overhead component only, avoiding
        # double counting the same ASUSE input benchmark in MVV feasibility and cash flow.
        monthly_opex = monthly_input * adapter.capacity_factor * scale * 0.10 * monthly_cost_factor
        primitive = VenturePrimitive(
            primitive_id=f"{adapter.key}-{name}-v1",
            primitive_type=adapter.primitive,
            sector_compatibility=[adapter.key],
            capex=capex,
            monthly_opex=monthly_opex,
            working_capital=working_capital,
            capacity=capacity,
            staff=max(1, round(float(workers.value) * scale)),
            service_radius_km=5 + (10 * scale),
            space_sqft=adapter.space_sqft * scale,
            inventory_days=adapter.inventory_days,
            receivable_days=adapter.receivable_days,
            payable_days=adapter.payable_days,
            lifetime_months=60,
            residual_value=capex * 0.15,
            licence_assumptions=list(adapter.licenses),
            equipment=list(factors.equipment) if factors else [],
            supplier_types=list(factors.supplier_types) if factors else [],
            customer_types=list(factors.customer_segments) if factors else [],
            quality_controls=list(factors.quality_controls) if factors else [],
            insurance_options=list(factors.insurance) if factors else [],
            operational_factors=list(factors.operational_factors) if factors else [],
            weather_factors=list(factors.weather_factors) if factors else [],
            required_skills=["basic bookkeeping", "supplier and customer coordination"],
            required_assets=list(adapter.licenses),
            assumption_labels=[
                "ASUSE_WEIGHTED_BENCHMARK",
                "MODELLED_LOCAL_CONFIGURATION",
                *asset_labels,
            ],
            evidence_ids=[output.id, inputs.id, assets.id, workers.id],
            added_edges=[
                EconomicEdge(
                    edge_id=f"venture-{adapter.key}-{name}",
                    source="local-suppliers",
                    target="local-demand",
                    commodity=adapter.commodity,
                    capacity=capacity,
                    unit_cost=monthly_opex / max(capacity, 1),
                    confidence=0.35,
                    evidence_ids=[output.id, inputs.id],
                    added_by_venture=True,
                )
            ],
        )
        candidates.append(
            VentureCandidate(
                candidate_id=f"{geo_id}:{adapter.key}:{name}-v1",
                primitives=[primitive],
                investment=primitive.investment,
                monthly_opex=monthly_opex,
                total_capacity=capacity,
            )
        )

    return AutomaticBuildResult(
        demand=demand,
        supply=supply,
        price=price,
        graph=graph,
        candidates=candidates,
        gates=[
            EvidenceGate(
                code=EvidenceGapCode.NO_CURRENT_FINANCE_RULE,
                message=(
                    "Scheme category screening is current; actual rate, sanction and lender "
                    "underwriting still require a lender quote."
                ),
                blocking=False,
            )
        ],
        graph_summary={
            "node_count": 2,
            "edge_count": 1,
            "commodity": adapter.commodity,
            "unit": adapter.unit,
            "builder": graph.methodology_version,
            "interpretation": (
                "benchmark-adjusted planning network, not a locality enterprise census"
            ),
        },
        model_versions={
            "sector_adapter": f"{adapter.key}-v1",
            "demand": demand.method_version,
            "supply": supply.method_version,
            "margin": price.method_version,
            "cost_library": "sector-cost-library-v1",
        },
        unit_price=1.0,
        contribution_margin_per_unit=margin_ratio,
    )


def _benchmark_interval(
    value: float, unit: str, evidence: EvidenceRecord, method: str, note: str
) -> EstimateInterval:
    return EstimateInterval(
        central=value,
        lower=value * 0.70,
        upper=value * 1.30,
        unit=unit,
        confidence=ConfidenceLevel.LOW,
        evidence_ids=[evidence.id],
        method_version=method,
        status="MODELLED_BENCHMARK",
        notes=[note],
    )

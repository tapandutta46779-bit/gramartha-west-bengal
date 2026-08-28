from __future__ import annotations

from pydantic import BaseModel, Field

from backend.models.decision import EvidenceGapCode, EvidenceGate
from backend.models.economic_graph import EconomicEdge, EconomicGraph, EconomicNode, NodeType
from backend.models.evidence import ConfidenceLevel, EstimateInterval, EvidenceRecord
from backend.models.profile import EntrepreneurProfile
from backend.models.venture import PrimitiveType, VentureCandidate, VenturePrimitive


class AutomaticBuildResult(BaseModel):
    demand: EstimateInterval
    supply: EstimateInterval
    price: EstimateInterval
    graph: EconomicGraph | None = None
    candidates: list[VentureCandidate] = Field(default_factory=list)
    gates: list[EvidenceGate] = Field(default_factory=list)
    graph_summary: dict = Field(default_factory=dict)
    model_versions: dict[str, str] = Field(default_factory=dict)


def build_automatic_inputs(
    *,
    geo_id: str,
    sector: str,
    evidence: list[EvidenceRecord],
    profile: EntrepreneurProfile,
) -> AutomaticBuildResult:
    normalized_sector = sector.casefold().strip()
    if normalized_sector not in {"dairy", "milk"}:
        insufficient = EstimateInterval.insufficient(
            "unknown", "sector-adapter-v1", f"No production adapter for {sector}."
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
            model_versions={"sector_adapter": "registry-v1"},
        )
    return _build_dairy(geo_id, evidence, profile)


def _numeric(evidence: list[EvidenceRecord], variable: str) -> EvidenceRecord | None:
    matches = [
        item
        for item in evidence
        if item.variable == variable
        and isinstance(item.value, (int, float))
        and not isinstance(item.value, bool)
    ]
    return matches[0] if len(matches) == 1 else None


def _interval(
    evidence: list[EvidenceRecord], variable: str, unit: str, method: str
) -> EstimateInterval:
    record = _numeric(evidence, variable)
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


def _build_dairy(
    geo_id: str, evidence: list[EvidenceRecord], profile: EntrepreneurProfile
) -> AutomaticBuildResult:
    demand = _interval(evidence, "monthly_dairy_demand_litres", "litres/month", "dairy-demand-v1")
    supply = _interval(
        evidence,
        "reachable_milk_supply_litres_month",
        "litres/month",
        "dairy-supply-v1",
    )
    price = _interval(evidence, "milk_price_inr_per_litre", "INR/litre", "dairy-price-v1")
    capacity_record = _numeric(evidence, "incumbent_capacity_litres_month")
    route_cost_record = _numeric(evidence, "transport_cost_inr_per_litre")
    gates = []
    if demand.status == "INSUFFICIENT_EVIDENCE":
        gates.append(
            EvidenceGate(
                code=EvidenceGapCode.NO_DEMAND_EVIDENCE,
                message="No defensible locality dairy-demand estimate is available.",
                required_variables=["monthly_dairy_demand_litres"],
            )
        )
    if supply.status == "INSUFFICIENT_EVIDENCE":
        gates.append(
            EvidenceGate(
                code=EvidenceGapCode.NO_SUPPLY_EVIDENCE,
                message=(
                    "Livestock stock exists, but productive fraction and milk yield are absent; "
                    "stock is not treated as milk supply."
                ),
                required_variables=["reachable_milk_supply_litres_month"],
            )
        )
    if price.status == "INSUFFICIENT_EVIDENCE":
        gates.append(
            EvidenceGate(
                code=EvidenceGapCode.NO_PRICE_EVIDENCE,
                message="No source-linked local milk price distribution is available.",
                required_variables=["milk_price_inr_per_litre"],
            )
        )
    if capacity_record is None:
        gates.append(
            EvidenceGate(
                code=EvidenceGapCode.NO_CAPACITY_EVIDENCE,
                message="Competitor count cannot substitute for incumbent service capacity.",
                required_variables=["incumbent_capacity_litres_month"],
            )
        )
    if route_cost_record is None:
        gates.append(
            EvidenceGate(
                code=EvidenceGapCode.NO_ROUTE_COST_EVIDENCE,
                message="No evidence-backed transport cost per litre is available.",
                required_variables=["transport_cost_inr_per_litre"],
            )
        )

    graph = None
    graph_summary = {}
    graph_ready = all(item.status != "INSUFFICIENT_EVIDENCE" for item in (demand, supply)) and all(
        item is not None for item in (capacity_record, route_cost_record)
    )
    if graph_ready:
        demand_id = demand.evidence_ids[0]
        supply_id = supply.evidence_ids[0]
        graph = EconomicGraph(
            graph_id=f"auto:{geo_id}:dairy:v1",
            commodity="milk",
            unit="litres/month",
            nodes=[
                EconomicNode(
                    node_id="local-producers",
                    node_type=NodeType.PRODUCER_CLUSTER,
                    geo_id=geo_id,
                    commodity="milk",
                    supply=float(supply.central or 0),
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
                    capacity=float(capacity_record.value),
                    unit_cost=float(route_cost_record.value),
                    confidence=min(
                        _confidence_value(capacity_record.confidence),
                        _confidence_value(route_cost_record.confidence),
                    ),
                    evidence_ids=[capacity_record.id, route_cost_record.id],
                )
            ],
            methodology_version="automatic-dairy-graph-v1",
        )
        graph_summary = {
            "node_count": len(graph.nodes),
            "edge_count": len(graph.edges),
            "commodity": graph.commodity,
            "unit": graph.unit,
            "builder": graph.methodology_version,
        }

    candidates = _dairy_candidates(geo_id, evidence, profile, graph)
    if graph is not None and not candidates:
        gates.append(
            EvidenceGate(
                code=EvidenceGapCode.NO_VENTURE_COST_EVIDENCE,
                message="No source-versioned venture cost/capacity configuration is available.",
                required_variables=[
                    "venture_transport_capex_inr",
                    "venture_transport_opex_inr_month",
                    "venture_transport_capacity_litres_month",
                    "venture_working_capital_inr",
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
            "sector_adapter": "dairy-v1",
            "demand": demand.method_version,
            "supply": supply.method_version,
            "price": price.method_version,
            "graph_builder": "automatic-dairy-graph-v1",
        },
    )


def _dairy_candidates(
    geo_id: str,
    evidence: list[EvidenceRecord],
    profile: EntrepreneurProfile,
    graph: EconomicGraph | None,
) -> list[VentureCandidate]:
    if graph is None:
        return []
    variables = {
        name: _numeric(evidence, name)
        for name in (
            "venture_transport_capex_inr",
            "venture_transport_opex_inr_month",
            "venture_transport_capacity_litres_month",
            "venture_working_capital_inr",
        )
    }
    if any(item is None for item in variables.values()):
        return []
    capex = float(variables["venture_transport_capex_inr"].value)  # type: ignore[union-attr]
    opex = float(variables["venture_transport_opex_inr_month"].value)  # type: ignore[union-attr]
    capacity = float(
        variables["venture_transport_capacity_litres_month"].value  # type: ignore[union-attr]
    )
    working_capital = float(
        variables["venture_working_capital_inr"].value  # type: ignore[union-attr]
    )
    if capex + working_capital > profile.available_capital:
        return []
    evidence_ids = [item.id for item in variables.values() if item is not None]
    primitive = VenturePrimitive(
        primitive_id="dairy-rented-transport-v1",
        primitive_type=PrimitiveType.TRANSPORT,
        sector_compatibility=["dairy"],
        capex=capex,
        monthly_opex=opex,
        working_capital=working_capital,
        capacity=capacity,
        added_edges=[
            EconomicEdge(
                edge_id="venture-transport-service",
                source="local-producers",
                target="local-demand",
                commodity="milk",
                capacity=capacity,
                unit_cost=float(
                    _numeric(evidence, "transport_cost_inr_per_litre").value  # type: ignore[union-attr]
                ),
                evidence_ids=evidence_ids,
                added_by_venture=True,
            )
        ],
        assumption_labels=["SOURCE_LINKED_CONFIGURATION"],
        evidence_ids=evidence_ids,
    )
    return [
        VentureCandidate(
            candidate_id=f"{geo_id}:dairy:rented-transport-v1",
            primitives=[primitive],
            investment=primitive.investment,
            monthly_opex=opex,
            total_capacity=capacity,
        )
    ]


def _confidence_value(level: ConfidenceLevel) -> float:
    return {
        ConfidenceLevel.HIGH: 0.9,
        ConfidenceLevel.MEDIUM: 0.7,
        ConfidenceLevel.LOW: 0.4,
        ConfidenceLevel.INSUFFICIENT: 0.0,
    }[level]

from __future__ import annotations

from copy import deepcopy

from backend.models.economic_graph import EconomicGraph
from backend.models.flow import Bottleneck, FlowResult

from .flow_engine import solve_min_cost_flow


def rank_capacity_bottlenecks(
    graph: EconomicGraph,
    baseline: FlowResult | None = None,
    relaxation: float = 1.0,
    repair_costs: dict[str, float] | None = None,
) -> list[Bottleneck]:
    if relaxation <= 0:
        raise ValueError("relaxation must be positive")
    baseline = baseline or solve_min_cost_flow(graph)
    repair_costs = repair_costs or {}
    ranked: list[Bottleneck] = []
    for position, edge in enumerate(graph.edges):
        modified = deepcopy(graph)
        modified.edges[position].capacity = float(edge.capacity) + relaxation
        result = solve_min_cost_flow(modified)
        gain = max(0.0, result.served_demand - baseline.served_demand)
        if gain <= 1e-9:
            continue
        repair_cost = repair_costs.get(edge.edge_id, 0.0)
        score = gain / repair_cost if repair_cost > 0 else gain
        ranked.append(
            Bottleneck(
                bottleneck_type="EDGE_CAPACITY",
                element_id=edge.edge_id,
                affected_demand=baseline.unserved_demand,
                marginal_gain=gain,
                estimated_repair_cost=repair_cost,
                score=score,
                confidence=edge.confidence,
                evidence_ids=edge.evidence_ids,
            )
        )
    return sorted(ranked, key=lambda item: (-item.score, item.element_id))

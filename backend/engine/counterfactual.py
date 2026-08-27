from __future__ import annotations

from copy import deepcopy

from backend.models.economic_graph import EconomicGraph
from backend.models.venture import CounterfactualResult, VentureCandidate

from .flow_engine import solve_min_cost_flow


def apply_candidate(graph: EconomicGraph, candidate: VentureCandidate) -> EconomicGraph:
    modified = deepcopy(graph)
    for primitive in candidate.primitives:
        modified.nodes.extend(deepcopy(primitive.added_nodes))
        for edge in deepcopy(primitive.added_edges):
            edge.added_by_venture = True
            modified.edges.append(edge)
    modified.graph_id = f"{graph.graph_id}:{candidate.candidate_id}"
    modified.validate_references()
    return modified


def evaluate_candidate(graph: EconomicGraph, candidate: VentureCandidate) -> CounterfactualResult:
    baseline = solve_min_cost_flow(graph)
    modified = apply_candidate(graph, candidate)
    counterfactual = solve_min_cost_flow(modified)
    added_ids = {
        edge.edge_id for primitive in candidate.primitives for edge in primitive.added_edges
    }
    added_edge_amounts = [
        flow.amount for flow in counterfactual.edge_flows if flow.edge_id in added_ids
    ]
    # A multi-edge venture path carries the same units through each serial edge; summing would
    # double count throughput. The maximum is a conservative path-throughput proxy until explicit
    # venture entry/exit edge roles are introduced.
    added_flow = max(added_edge_amounts, default=0.0)
    newly_served = max(0.0, counterfactual.served_demand - baseline.served_demand)
    return CounterfactualResult(
        candidate_id=candidate.candidate_id,
        baseline_served=baseline.served_demand,
        counterfactual_served=counterfactual.served_demand,
        newly_served_demand=newly_served,
        added_venture_flow=added_flow,
        cannibalized_existing_flow=max(0.0, added_flow - newly_served),
        economic_cost_change=counterfactual.economic_cost - baseline.economic_cost,
        affected_entities=sorted(
            {edge.target for primitive in candidate.primitives for edge in primitive.added_edges}
        ),
    )

from __future__ import annotations

from dataclasses import dataclass
from math import inf

from backend.models.economic_graph import EconomicGraph
from backend.models.flow import EdgeFlow, FlowResult

EPSILON = 1e-9


@dataclass
class _Arc:
    to: int
    reverse: int
    capacity: float
    cost: float
    original_capacity: float
    edge_id: str | None = None


def solve_min_cost_flow(graph: EconomicGraph) -> FlowResult:
    """Solve maximum served demand, then minimum economic cost, exactly under the model."""
    graph.validate_references()
    ids = [node.node_id for node in graph.nodes]
    index = {node_id: position for position, node_id in enumerate(ids)}
    source = len(ids)
    sink = source + 1
    residual: list[list[_Arc]] = [[] for _ in range(len(ids) + 2)]
    tracked: dict[str, tuple[int, int]] = {}

    def add_arc(start: int, end: int, capacity: float, cost: float, edge_id: str | None = None):
        forward_index = len(residual[start])
        residual[start].append(
            _Arc(end, len(residual[end]), capacity, cost, capacity, edge_id=edge_id)
        )
        residual[end].append(_Arc(start, forward_index, 0.0, -cost, 0.0))
        if edge_id is not None:
            tracked[edge_id] = (start, forward_index)

    demand_arcs: dict[str, tuple[int, int]] = {}
    for node in graph.nodes:
        if node.supply > 0:
            add_arc(source, index[node.node_id], float(node.supply), 0.0)
        if node.demand > 0:
            demand_arcs[node.node_id] = (index[node.node_id], len(residual[index[node.node_id]]))
            add_arc(index[node.node_id], sink, float(node.demand), 0.0)
    for edge in graph.edges:
        add_arc(
            index[edge.source],
            index[edge.target],
            float(edge.capacity),
            float(edge.unit_cost),
            edge.edge_id,
        )

    total_flow = 0.0
    total_cost = 0.0
    while True:
        distance = [inf] * len(residual)
        parent: list[tuple[int, int] | None] = [None] * len(residual)
        distance[source] = 0.0
        for _ in range(len(residual) - 1):
            changed = False
            for start, arcs in enumerate(residual):
                if distance[start] == inf:
                    continue
                for arc_index, arc in enumerate(arcs):
                    candidate = distance[start] + arc.cost
                    if arc.capacity > EPSILON and candidate < distance[arc.to] - EPSILON:
                        distance[arc.to] = candidate
                        parent[arc.to] = (start, arc_index)
                        changed = True
            if not changed:
                break
        if parent[sink] is None:
            break
        augmentation = inf
        cursor = sink
        while cursor != source:
            start, arc_index = parent[cursor]  # type: ignore[misc]
            augmentation = min(augmentation, residual[start][arc_index].capacity)
            cursor = start
        cursor = sink
        while cursor != source:
            start, arc_index = parent[cursor]  # type: ignore[misc]
            arc = residual[start][arc_index]
            arc.capacity -= augmentation
            residual[cursor][arc.reverse].capacity += augmentation
            total_cost += augmentation * arc.cost
            cursor = start
        total_flow += augmentation

    flows = []
    for edge in graph.edges:
        start, arc_index = tracked[edge.edge_id]
        arc = residual[start][arc_index]
        amount = arc.original_capacity - arc.capacity
        if amount > EPSILON:
            flows.append(EdgeFlow(edge_id=edge.edge_id, amount=amount, unit_cost=edge.unit_cost))
    served_by_node = {}
    for node_id, (start, arc_index) in demand_arcs.items():
        arc = residual[start][arc_index]
        served_by_node[node_id] = arc.original_capacity - arc.capacity

    reachable_supply = _reachable_supply(graph)
    nominal_demand = sum(float(node.demand) for node in graph.nodes)
    return FlowResult(
        graph_id=graph.graph_id,
        commodity=graph.commodity,
        unit=graph.unit,
        nominal_demand=nominal_demand,
        reachable_supply=reachable_supply,
        served_demand=total_flow,
        unserved_demand=max(0.0, nominal_demand - total_flow),
        economic_cost=total_cost,
        edge_flows=flows,
        demand_served_by_node=served_by_node,
    )


def _reachable_supply(graph: EconomicGraph) -> float:
    adjacency: dict[str, list[str]] = {node.node_id: [] for node in graph.nodes}
    for edge in graph.edges:
        if edge.capacity > EPSILON:
            adjacency[edge.source].append(edge.target)
    demand_nodes = {node.node_id for node in graph.nodes if node.demand > EPSILON}
    total = 0.0
    for node in graph.nodes:
        if node.supply <= EPSILON:
            continue
        frontier = [node.node_id]
        seen = set(frontier)
        reachable = False
        while frontier:
            current = frontier.pop()
            if current in demand_nodes:
                reachable = True
                break
            for following in adjacency[current]:
                if following not in seen:
                    seen.add(following)
                    frontier.append(following)
        if reachable:
            total += float(node.supply)
    return total

from __future__ import annotations

import json
import resource
import time
from pathlib import Path

from backend.engine.bottleneck import rank_capacity_bottlenecks
from backend.engine.flow_engine import solve_min_cost_flow
from backend.models.economic_graph import EconomicEdge, EconomicGraph, EconomicNode, NodeType


def chain_graph(size: int) -> EconomicGraph:
    nodes = [
        EconomicNode(
            node_id=f"n{index}",
            node_type=(
                NodeType.PRODUCER_CLUSTER
                if index == 0
                else NodeType.CUSTOMER_CLUSTER
                if index == size - 1
                else NodeType.TRANSPORT_HUB
            ),
            geo_id="benchmark",
            commodity="milk",
            supply=100 if index == 0 else 0,
            demand=100 if index == size - 1 else 0,
        )
        for index in range(size)
    ]
    edges = [
        EconomicEdge(
            edge_id=f"e{index}",
            source=f"n{index}",
            target=f"n{index + 1}",
            commodity="milk",
            capacity=100,
            unit_cost=1,
        )
        for index in range(size - 1)
    ]
    return EconomicGraph(
        graph_id=f"chain-{size}", commodity="milk", unit="litres", nodes=nodes, edges=edges
    )


def benchmark() -> dict:
    rows = []
    for size in (10, 50, 100, 500, 1000):
        graph = chain_graph(size)
        start = time.perf_counter()
        result = solve_min_cost_flow(graph)
        flow_seconds = time.perf_counter() - start
        bottleneck_seconds = None
        if size <= 100:
            start = time.perf_counter()
            rank_capacity_bottlenecks(graph, result, relaxation=1)
            bottleneck_seconds = time.perf_counter() - start
        rows.append(
            {
                "nodes": size,
                "edges": size - 1,
                "flow_seconds": flow_seconds,
                "bottleneck_seconds": bottleneck_seconds,
                "served": result.served_demand,
            }
        )
    return {
        "methodology": "single-commodity chain graph; one augmentation",
        "rows": rows,
        "max_resident_set_size_platform_units": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "limitations": [
            "Chain graphs do not represent worst-case multi-customer augmentation counts.",
            "Bottleneck reruns are omitted above 100 nodes to avoid unbounded demo runtime.",
        ],
    }


def main() -> None:
    result = benchmark()
    destination = Path("outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS/FLOW_PERFORMANCE.json")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

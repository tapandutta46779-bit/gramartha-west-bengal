from __future__ import annotations

from backend.models.economic_graph import EconomicEdge, EconomicGraph, EconomicNode, NodeType
from backend.models.venture import PrimitiveType, VentureCandidate, VenturePrimitive


def basic_graph(edge_capacity: float = 4, demand: float = 10) -> EconomicGraph:
    return EconomicGraph(
        graph_id="controlled",
        commodity="milk",
        unit="litre/month",
        nodes=[
            EconomicNode(
                node_id="producer",
                node_type=NodeType.PRODUCER_CLUSTER,
                geo_id="SYNTHETIC:producer",
                commodity="milk",
                supply=10,
                incumbent=False,
            ),
            EconomicNode(
                node_id="market",
                node_type=NodeType.MARKET,
                geo_id="SYNTHETIC:market",
                commodity="milk",
                demand=demand,
            ),
        ],
        edges=[
            EconomicEdge(
                edge_id="route",
                source="producer",
                target="market",
                commodity="milk",
                capacity=edge_capacity,
                unit_cost=2,
            )
        ],
    )


def connector_candidate(candidate_id: str, capacity: float, investment: float = 100):
    primitive = VenturePrimitive(
        primitive_id=f"{candidate_id}:transport",
        primitive_type=PrimitiveType.TRANSPORT,
        sector_compatibility=["milk"],
        capex=investment,
        monthly_opex=0,
        working_capital=0,
        capacity=capacity,
        added_edges=[
            EconomicEdge(
                edge_id=f"{candidate_id}:route",
                source="producer",
                target="market",
                commodity="milk",
                capacity=capacity,
                unit_cost=3,
                added_by_venture=True,
            )
        ],
    )
    return VentureCandidate(
        candidate_id=candidate_id,
        primitives=[primitive],
        investment=investment,
        monthly_opex=0,
        total_capacity=capacity,
    )

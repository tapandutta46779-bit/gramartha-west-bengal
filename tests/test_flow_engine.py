from backend.engine.bottleneck import rank_capacity_bottlenecks
from backend.engine.flow_engine import solve_min_cost_flow
from backend.models.economic_graph import EconomicEdge

from .conftest import basic_graph


def test_capacity_constrained_flow_and_bottleneck():
    graph = basic_graph(edge_capacity=4, demand=10)
    result = solve_min_cost_flow(graph)
    assert result.nominal_demand == 10
    assert result.reachable_supply == 10
    assert result.served_demand == 4
    assert result.unserved_demand == 6
    assert result.economic_cost == 8
    bottleneck = rank_capacity_bottlenecks(graph, result, relaxation=1)[0]
    assert bottleneck.element_id == "route"
    assert bottleneck.marginal_gain == 1


def test_hidden_connector_beats_direct_expensive_route():
    graph = basic_graph(edge_capacity=10, demand=5)
    graph.nodes.append(
        graph.nodes[1].model_copy(
            update={"node_id": "hub", "node_type": "TRANSPORT_HUB", "demand": 0}
        )
    )
    graph.edges.extend(
        [
            EconomicEdge(
                edge_id="producer-hub",
                source="producer",
                target="hub",
                commodity="milk",
                capacity=5,
                unit_cost=0.5,
            ),
            EconomicEdge(
                edge_id="hub-market",
                source="hub",
                target="market",
                commodity="milk",
                capacity=5,
                unit_cost=0.5,
            ),
        ]
    )
    result = solve_min_cost_flow(graph)
    assert result.served_demand == 5
    assert result.economic_cost == 5
    assert {flow.edge_id for flow in result.edge_flows} == {"producer-hub", "hub-market"}


def test_zero_demand_and_zero_competitor_case():
    result = solve_min_cost_flow(basic_graph(edge_capacity=0, demand=0))
    assert result.served_demand == 0
    assert result.unserved_demand == 0
    assert result.economic_cost == 0

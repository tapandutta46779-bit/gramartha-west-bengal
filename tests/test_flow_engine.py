from backend.engine.bottleneck import rank_capacity_bottlenecks
from backend.engine.flow_engine import solve_min_cost_flow
from backend.models.economic_graph import EconomicEdge, EconomicGraph, EconomicNode, NodeType

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


def test_multiple_producers_consumers_and_expensive_route_lexicographic_objective():
    graph = EconomicGraph(
        graph_id="multi",
        commodity="milk",
        unit="litres",
        nodes=[
            EconomicNode(
                node_id="p1",
                node_type=NodeType.PRODUCER_CLUSTER,
                geo_id="g",
                commodity="milk",
                supply=4,
            ),
            EconomicNode(
                node_id="p2",
                node_type=NodeType.PRODUCER_CLUSTER,
                geo_id="g",
                commodity="milk",
                supply=6,
            ),
            EconomicNode(
                node_id="c1",
                node_type=NodeType.CUSTOMER_CLUSTER,
                geo_id="g",
                commodity="milk",
                demand=5,
            ),
            EconomicNode(
                node_id="c2",
                node_type=NodeType.CUSTOMER_CLUSTER,
                geo_id="g",
                commodity="milk",
                demand=5,
            ),
        ],
        edges=[
            EconomicEdge(
                edge_id="cheap-1",
                source="p1",
                target="c1",
                commodity="milk",
                capacity=4,
                unit_cost=1,
            ),
            EconomicEdge(
                edge_id="cheap-2",
                source="p2",
                target="c2",
                commodity="milk",
                capacity=5,
                unit_cost=1,
            ),
            EconomicEdge(
                edge_id="expensive",
                source="p2",
                target="c1",
                commodity="milk",
                capacity=1,
                unit_cost=10,
            ),
        ],
    )
    result = solve_min_cost_flow(graph)
    assert result.served_demand == 10
    assert result.unserved_demand == 0
    assert result.economic_cost == 19


def test_unreachable_consumer_remains_unserved():
    graph = basic_graph(edge_capacity=10, demand=4)
    graph.nodes.append(
        EconomicNode(
            node_id="isolated",
            node_type=NodeType.CUSTOMER_CLUSTER,
            geo_id="g",
            commodity="milk",
            demand=3,
        )
    )
    result = solve_min_cost_flow(graph)
    assert result.served_demand == 4
    assert result.unserved_demand == 3
    assert result.demand_served_by_node["isolated"] == 0


def test_equal_cost_optima_preserve_conservation():
    graph = basic_graph(edge_capacity=3, demand=6)
    graph.edges.append(
        EconomicEdge(
            edge_id="equal-route",
            source="producer",
            target="market",
            commodity="milk",
            capacity=3,
            unit_cost=2,
        )
    )
    result = solve_min_cost_flow(graph)
    assert result.served_demand == sum(flow.amount for flow in result.edge_flows)
    assert result.served_demand == 6
    assert result.economic_cost == 12

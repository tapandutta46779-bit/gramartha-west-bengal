from backend.engine.counterfactual import evaluate_candidate
from backend.engine.mvv import select_minimum_viable_venture
from backend.models.profile import EntrepreneurProfile

from .conftest import basic_graph, connector_candidate


def test_counterfactual_separates_new_demand_and_cannibalization():
    graph = basic_graph(edge_capacity=10, demand=5)
    candidate = connector_candidate("cheaper", 5)
    candidate.primitives[0].added_edges[0].unit_cost = 1
    result = evaluate_candidate(graph, candidate)
    assert result.newly_served_demand == 0
    assert result.added_venture_flow == 5
    assert result.cannibalized_existing_flow == 5


def test_mvv_selects_smallest_feasible_enumerated_candidate():
    graph = basic_graph(edge_capacity=3, demand=10)
    candidates = [
        connector_candidate("large", 7, 700),
        connector_candidate("small", 3, 300),
        connector_candidate("too-small", 1, 100),
    ]
    profile = EntrepreneurProfile(
        geo_id="SYNTHETIC:test",
        available_capital=1000,
        business_category="milk",
        minimum_monthly_income=0,
    )
    result = select_minimum_viable_venture(graph, profile, candidates, 2, 1)
    assert result.status == "OPTIMAL_OVER_ENUMERATED_CANDIDATES"
    assert result.selected is not None
    assert result.selected.candidate_id == "small"
    assert result.exact is True


def test_debt_is_a_ceiling_and_inverse_relaxation_is_reported():
    graph = basic_graph(edge_capacity=0, demand=20)
    candidates = [
        connector_candidate("own-cash", 5, 900),
        connector_candidate("small-debt", 10, 1300),
        connector_candidate("too-much-debt", 15, 1800),
    ]
    profile = EntrepreneurProfile(
        geo_id="SYNTHETIC:test",
        available_capital=1000,
        acceptable_debt=350,
        business_category="milk",
        minimum_monthly_income=8,
    )
    result = select_minimum_viable_venture(graph, profile, candidates, 1, 1)
    assert result.selected is not None
    assert result.selected.candidate_id == "small-debt"
    selected_metrics = next(
        item for item in result.candidate_metrics if item["candidate_id"] == "small-debt"
    )
    assert selected_metrics["debt_required"] == 300
    assert (
        "DEBT_CEILING"
        in next(
            item for item in result.candidate_metrics if item["candidate_id"] == "too-much-debt"
        )["reasons"]
    )
    assert result.inverse_analysis["minimum_debt_for_income_target"] == 300


def test_infeasible_income_returns_binding_constraint_and_smallest_relaxation():
    graph = basic_graph(edge_capacity=0, demand=20)
    candidates = [
        connector_candidate("small", 5, 500),
        connector_candidate("large", 10, 1000),
    ]
    profile = EntrepreneurProfile(
        geo_id="SYNTHETIC:test",
        available_capital=600,
        acceptable_debt=0,
        business_category="milk",
        minimum_monthly_income=9,
    )
    result = select_minimum_viable_venture(graph, profile, candidates, 1, 1)
    assert result.selected is None
    assert set(result.binding_constraints) == {
        "DEBT_CEILING",
        "FUNDING_LIMIT",
        "MINIMUM_INCOME_NOT_MET",
    }
    assert result.constraint_relaxation["best_income_with_current_limits"] == 5
    assert result.constraint_relaxation["additional_own_capital_needed"] == 400
    assert result.constraint_relaxation["additional_debt_ceiling_needed"] == 400

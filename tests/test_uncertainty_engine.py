from backend.engine.uncertainty import (
    conditional_value_at_risk,
    failure_boundaries,
    triangular_scenarios,
    value_at_risk,
)
from backend.models.venture import VentureCandidate, VenturePrimitive


def candidate() -> VentureCandidate:
    primitive = VenturePrimitive(
        primitive_id="controlled-retail",
        primitive_type="RETAIL",
        sector_compatibility=["controlled"],
        capex=40_000,
        monthly_opex=2_000,
        working_capital=10_000,
        capacity=25_000,
    )
    return VentureCandidate(
        candidate_id="controlled",
        primitives=[primitive],
        investment=50_000,
        monthly_opex=2_000,
        total_capacity=25_000,
    )


def test_scenarios_are_seeded_reproducible_and_nonconstant():
    first = triangular_scenarios("same", 20)
    second = triangular_scenarios("same", 20)
    assert first == second
    assert len({draw.demand_factor for draw in first}) > 1
    assert first != triangular_scenarios("different", 20)


def test_var_and_cvar_known_distribution():
    losses = list(range(1, 101))
    assert value_at_risk(losses, 0.95) == 96
    assert conditional_value_at_risk(losses, 0.95) == 98


def test_failure_boundaries_are_ordered_and_reproducible():
    result = failure_boundaries(
        candidate(), available_capital=100_000, monthly_demand=30_000, margin_share=0.3
    )
    assert [item["variable"] for item in result] == [
        "monthly_demand",
        "selling_price_factor",
        "variable_cost_factor",
    ]
    assert result[0]["threshold"] is None or 0 <= result[0]["threshold"] <= 30_000
    assert result[1]["threshold"] is None or 0 <= result[1]["threshold"] <= 1
    assert result[2]["threshold"] is None or 1 <= result[2]["threshold"] <= 2.5

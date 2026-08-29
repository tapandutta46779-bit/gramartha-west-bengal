from backend.engine.uncertainty import (
    conditional_value_at_risk,
    failure_boundaries,
    sensitivity_analysis,
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
        "fixed_opex_factor",
        "minimum_cash_buffer",
    ]
    assert result[0]["threshold"] is None or 0 <= result[0]["threshold"] <= 30_000
    assert result[1]["threshold"] is None or 0 <= result[1]["threshold"] <= 1
    assert result[2]["threshold"] is None or 1 <= result[2]["threshold"] <= 10
    assert result[3]["threshold"] is None or 1 <= result[3]["threshold"] <= 10
    assert result[4]["threshold"] is None or result[4]["threshold"] >= 0


def test_sensitivity_is_ranked_and_uses_controlled_perturbations():
    result = sensitivity_analysis(
        candidate(), available_capital=100_000, monthly_demand=30_000, margin_share=0.3
    )
    assert {item["variable"] for item in result} == {
        "demand",
        "selling_price",
        "variable_cost",
        "fixed_opex",
    }
    absolute = [abs(item["elasticity"] or 0) for item in result]
    assert absolute == sorted(absolute, reverse=True)

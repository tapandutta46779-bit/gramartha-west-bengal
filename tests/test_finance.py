import pytest

from backend.finance.calculator import amortized_loan
from backend.finance.digital_twin import project_monthly_cashflow
from backend.finance.stress import find_failure_boundary
from backend.models.finance import FinanceRule, FinanceRuleStatus


def test_zero_interest_amortization_hand_case():
    loan = amortized_loan(1200, 0, 12)
    assert loan.monthly_payment == 100
    assert loan.total_interest == 0


def test_real_decision_rejects_unverified_finance_rule():
    rule = FinanceRule(
        rule_id="illustrative",
        scheme_name="Illustrative only",
        effective_from="2026-01-01",
        status=FinanceRuleStatus.UNVERIFIED,
        source_url="https://example.invalid",
        source_version="test",
        maximum_principal=10000,
        annual_interest_rate=0.12,
        maximum_tenure_months=12,
    )
    with pytest.raises(ValueError, match="source-verified"):
        amortized_loan(1000, 0.12, 12, rule, real_decision=True)


def test_digital_twin_hand_calculation_and_failure_boundary():
    twin = project_monthly_cashflow(
        months=3,
        opening_cash=50,
        monthly_demand=10,
        capacity=10,
        unit_price=5,
        variable_cost_per_unit=2,
        fixed_monthly_cost=20,
    )
    assert [month.operating_cash_flow for month in twin.months] == [10, 10, 10]
    assert twin.minimum_cash == 60
    assert twin.default_month is None

    boundary = find_failure_boundary(
        "monthly_demand", 10, "DOWN", 1, lambda value: value >= 7, maximum_points=10
    )
    assert boundary.first_failure_value == 6

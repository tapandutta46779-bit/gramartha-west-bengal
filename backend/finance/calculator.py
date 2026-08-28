from __future__ import annotations

from backend.models.finance import FinanceRule, FinanceRuleStatus, LoanTerms


def break_even_volume(unit_price: float, variable_cost_per_unit: float, fixed_cost: float) -> float:
    contribution = unit_price - variable_cost_per_unit
    if fixed_cost < 0 or unit_price < 0 or variable_cost_per_unit < 0:
        raise ValueError("cost and price inputs cannot be negative")
    if contribution <= 0:
        raise ValueError("positive contribution margin is required")
    return fixed_cost / contribution


def net_present_value(cash_flows: list[float], annual_discount_rate: float) -> float:
    if not cash_flows or annual_discount_rate <= -1:
        raise ValueError("cash flows are required and discount rate must exceed -100%")
    monthly_rate = (1 + annual_discount_rate) ** (1 / 12) - 1
    return sum(value / ((1 + monthly_rate) ** month) for month, value in enumerate(cash_flows))


def internal_rate_of_return(cash_flows: list[float]) -> float | None:
    if (
        not cash_flows
        or not any(value < 0 for value in cash_flows)
        or not any(value > 0 for value in cash_flows)
    ):
        return None

    def npv(monthly_rate: float) -> float:
        return sum(value / ((1 + monthly_rate) ** month) for month, value in enumerate(cash_flows))

    lower, upper = -0.99, 10.0
    if npv(lower) * npv(upper) > 0:
        return None
    for _ in range(100):
        middle = (lower + upper) / 2
        if npv(lower) * npv(middle) <= 0:
            upper = middle
        else:
            lower = middle
    monthly = (lower + upper) / 2
    return (1 + monthly) ** 12 - 1


def amortized_loan(
    principal: float,
    annual_interest_rate: float,
    tenure_months: int,
    rule: FinanceRule | None = None,
    real_decision: bool = False,
) -> LoanTerms:
    if principal < 0 or annual_interest_rate < 0 or tenure_months <= 0:
        raise ValueError("invalid loan parameters")
    if real_decision and (rule is None or rule.status != FinanceRuleStatus.VERIFIED):
        raise ValueError("real decisions require a current, source-verified finance rule")
    if rule is not None:
        if principal > rule.maximum_principal:
            raise ValueError("principal exceeds verified scheme maximum")
        if tenure_months > rule.maximum_tenure_months:
            raise ValueError("tenure exceeds verified scheme maximum")
        if abs(annual_interest_rate - rule.annual_interest_rate) > 1e-9:
            raise ValueError("interest rate does not match supplied rule")
    monthly_rate = annual_interest_rate / 12.0
    if principal == 0:
        payment = 0.0
    elif monthly_rate == 0:
        payment = principal / tenure_months
    else:
        factor = (1 + monthly_rate) ** tenure_months
        payment = principal * monthly_rate * factor / (factor - 1)
    return LoanTerms(
        principal=principal,
        annual_interest_rate=annual_interest_rate,
        tenure_months=tenure_months,
        monthly_payment=payment,
        total_interest=payment * tenure_months - principal,
        rule_id=rule.rule_id if rule else None,
        verified_for_real_decision=bool(rule and rule.status == FinanceRuleStatus.VERIFIED),
    )

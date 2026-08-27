from __future__ import annotations

from backend.models.finance import FinanceRule, FinanceRuleStatus, LoanTerms


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

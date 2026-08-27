from __future__ import annotations

from backend.models.finance import DigitalTwinResult, LoanTerms, MonthProjection


def project_monthly_cashflow(
    *,
    months: int = 36,
    opening_cash: float,
    monthly_demand: float,
    capacity: float,
    unit_price: float,
    variable_cost_per_unit: float,
    fixed_monthly_cost: float,
    growth_rate: float = 0.0,
    ramp_months: int = 1,
    loan: LoanTerms | None = None,
) -> DigitalTwinResult:
    if months <= 0 or ramp_months <= 0:
        raise ValueError("months and ramp_months must be positive")
    if min(monthly_demand, capacity, unit_price, variable_cost_per_unit, fixed_monthly_cost) < 0:
        raise ValueError("operating inputs cannot be negative")
    cash = opening_cash
    projections = []
    break_even_month = None
    default_month = None
    cumulative_operating = 0.0
    for month in range(1, months + 1):
        demand = monthly_demand * ((1 + growth_rate) ** (month - 1))
        ramp = min(1.0, month / ramp_months)
        sales = min(demand, capacity * ramp)
        revenue = sales * unit_price
        variable_cost = sales * variable_cost_per_unit
        debt_payment = loan.monthly_payment if loan and month <= loan.tenure_months else 0.0
        operating_cash_flow = revenue - variable_cost - fixed_monthly_cost - debt_payment
        cash += operating_cash_flow
        cumulative_operating += operating_cash_flow
        contribution_before_debt = revenue - variable_cost - fixed_monthly_cost
        dscr = contribution_before_debt / debt_payment if debt_payment > 0 else None
        projections.append(
            MonthProjection(
                month=month,
                demand=demand,
                sales_volume=sales,
                revenue=revenue,
                variable_cost=variable_cost,
                fixed_cost=fixed_monthly_cost,
                debt_payment=debt_payment,
                operating_cash_flow=operating_cash_flow,
                closing_cash=cash,
                debt_service_coverage_ratio=dscr,
            )
        )
        if break_even_month is None and cumulative_operating >= 0:
            break_even_month = month
        if default_month is None and cash < 0:
            default_month = month
    return DigitalTwinResult(
        months=projections,
        minimum_cash=min(item.closing_cash for item in projections),
        cumulative_cash_flow=cumulative_operating,
        break_even_month=break_even_month,
        default_month=default_month,
        assumptions={
            "opening_cash": opening_cash,
            "monthly_demand": monthly_demand,
            "capacity": capacity,
            "unit_price": unit_price,
            "variable_cost_per_unit": variable_cost_per_unit,
            "fixed_monthly_cost": fixed_monthly_cost,
            "growth_rate": growth_rate,
            "ramp_months": float(ramp_months),
        },
    )

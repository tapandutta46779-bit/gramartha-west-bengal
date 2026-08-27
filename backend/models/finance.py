from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, NonNegativeFloat


class FinanceRuleStatus(StrEnum):
    VERIFIED = "VERIFIED"
    EXPIRED = "EXPIRED"
    UNVERIFIED = "UNVERIFIED"


class FinanceRule(BaseModel):
    rule_id: str
    scheme_name: str
    effective_from: str
    effective_to: str | None = None
    status: FinanceRuleStatus
    source_url: str
    source_version: str
    maximum_principal: NonNegativeFloat
    annual_interest_rate: NonNegativeFloat
    maximum_tenure_months: int = Field(gt=0)
    subsidy_rate: float = Field(default=0, ge=0, le=1)
    borrower_contribution_rate: float = Field(default=0, ge=0, le=1)
    notes: list[str] = Field(default_factory=list)


class LoanTerms(BaseModel):
    principal: NonNegativeFloat
    annual_interest_rate: NonNegativeFloat
    tenure_months: int = Field(gt=0)
    monthly_payment: NonNegativeFloat
    total_interest: NonNegativeFloat
    rule_id: str | None = None
    verified_for_real_decision: bool = False


class MonthProjection(BaseModel):
    month: int = Field(gt=0)
    demand: NonNegativeFloat
    sales_volume: NonNegativeFloat
    revenue: float
    variable_cost: float
    fixed_cost: float
    debt_payment: float
    operating_cash_flow: float
    closing_cash: float
    debt_service_coverage_ratio: float | None


class DigitalTwinResult(BaseModel):
    months: list[MonthProjection]
    minimum_cash: float
    cumulative_cash_flow: float
    break_even_month: int | None
    default_month: int | None
    assumptions: dict[str, float] = Field(default_factory=dict)
    method_version: str = "digital-twin-v1"


class FailureBoundary(BaseModel):
    variable: str
    baseline_value: float
    first_failure_value: float | None
    direction: str
    step: float
    criterion: str
    tested_points: int


class StressResult(BaseModel):
    scenario_id: str
    survives: bool
    minimum_cash: float
    default_month: int | None
    boundaries: list[FailureBoundary] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

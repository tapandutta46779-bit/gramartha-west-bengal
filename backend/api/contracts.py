from __future__ import annotations

from pydantic import BaseModel, Field, NonNegativeFloat

from backend.models.economic_graph import EconomicGraph
from backend.models.evidence import EvidenceRecord
from backend.models.finance import FinanceRule
from backend.models.profile import EntrepreneurProfile
from backend.models.venture import VentureCandidate


class OperatingAssumptions(BaseModel):
    opening_cash: NonNegativeFloat
    monthly_demand: NonNegativeFloat
    capacity: NonNegativeFloat
    unit_price: NonNegativeFloat
    variable_cost_per_unit: NonNegativeFloat
    fixed_monthly_cost: NonNegativeFloat
    growth_rate: float = Field(default=0, gt=-1)
    ramp_months: int = Field(default=1, gt=0)


class LoanRequest(BaseModel):
    principal: NonNegativeFloat
    annual_interest_rate: NonNegativeFloat
    tenure_months: int = Field(gt=0)
    rule: FinanceRule | None = None
    real_decision: bool = False


class AnalyzeRequest(BaseModel):
    geo_id: str
    entrepreneur: EntrepreneurProfile
    graph: EconomicGraph | None = None
    candidates: list[VentureCandidate] = Field(default_factory=list)
    evidence: list[EvidenceRecord] = Field(default_factory=list)
    minimum_newly_served: NonNegativeFloat = 0
    contribution_margin_per_unit: float = 0
    operating_assumptions: OperatingAssumptions | None = None
    loan: LoanRequest | None = None


class CompareRequest(AnalyzeRequest):
    pass


class StressRequest(BaseModel):
    analysis_id: str
    demand_step: float = Field(default=1, gt=0)
    maximum_points: int = Field(default=100, gt=0, le=1000)

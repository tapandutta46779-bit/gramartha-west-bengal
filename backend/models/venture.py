from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, NonNegativeFloat

from .economic_graph import EconomicEdge, EconomicNode


class PrimitiveType(StrEnum):
    RETAIL = "RETAIL"
    AGGREGATION = "AGGREGATION"
    TRANSPORT = "TRANSPORT"
    STORAGE = "STORAGE"
    PROCESSING = "PROCESSING"
    DELIVERY = "DELIVERY"
    REPAIR = "REPAIR"
    DISTRIBUTION = "DISTRIBUTION"


class VenturePrimitive(BaseModel):
    primitive_id: str
    primitive_type: PrimitiveType
    sector_compatibility: list[str]
    capex: NonNegativeFloat
    monthly_opex: NonNegativeFloat
    working_capital: NonNegativeFloat
    capacity: NonNegativeFloat
    required_skills: list[str] = Field(default_factory=list)
    required_assets: list[str] = Field(default_factory=list)
    staff: int = Field(default=0, ge=0)
    service_radius_km: NonNegativeFloat | None = None
    space_sqft: NonNegativeFloat | None = None
    operating_days_per_month: int = Field(default=26, ge=1, le=31)
    inventory_days: NonNegativeFloat = 0
    receivable_days: NonNegativeFloat = 0
    payable_days: NonNegativeFloat = 0
    lifetime_months: int | None = Field(default=None, gt=0)
    residual_value: NonNegativeFloat = 0
    licence_assumptions: list[str] = Field(default_factory=list)
    added_nodes: list[EconomicNode] = Field(default_factory=list)
    added_edges: list[EconomicEdge] = Field(default_factory=list)
    assumption_labels: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)

    @property
    def investment(self) -> float:
        return float(self.capex + self.working_capital)

    @property
    def cash_conversion_cycle_days(self) -> float:
        return float(self.inventory_days + self.receivable_days - self.payable_days)


class VentureCandidate(BaseModel):
    candidate_id: str
    primitives: list[VenturePrimitive]
    investment: float
    monthly_opex: float
    total_capacity: float


class CounterfactualResult(BaseModel):
    candidate_id: str
    baseline_served: float
    counterfactual_served: float
    newly_served_demand: float
    added_venture_flow: float
    cannibalized_existing_flow: float
    economic_cost_change: float
    affected_entities: list[str]


class MVVResult(BaseModel):
    status: str
    selected: VentureCandidate | None = None
    counterfactual: CounterfactualResult | None = None
    rejected: list[dict] = Field(default_factory=list)
    exact: bool = True
    evaluated_count: int = 0
    objective: str = "minimum investment subject to configured feasibility constraints"

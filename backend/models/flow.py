from __future__ import annotations

from pydantic import BaseModel, Field


class EdgeFlow(BaseModel):
    edge_id: str
    amount: float
    unit_cost: float


class FlowResult(BaseModel):
    graph_id: str
    commodity: str
    unit: str
    nominal_demand: float
    reachable_supply: float
    served_demand: float
    unserved_demand: float
    economic_cost: float
    edge_flows: list[EdgeFlow] = Field(default_factory=list)
    demand_served_by_node: dict[str, float] = Field(default_factory=dict)
    solver: str = "successive-shortest-path-v1"
    exact_under_model: bool = True


class Bottleneck(BaseModel):
    bottleneck_type: str
    element_id: str
    affected_demand: float
    marginal_gain: float
    estimated_repair_cost: float
    score: float
    confidence: float
    evidence_ids: list[str] = Field(default_factory=list)

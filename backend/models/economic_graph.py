from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, NonNegativeFloat


class NodeType(StrEnum):
    CUSTOMER_CLUSTER = "CUSTOMER_CLUSTER"
    PRODUCER_CLUSTER = "PRODUCER_CLUSTER"
    BUSINESS = "BUSINESS"
    MARKET = "MARKET"
    COLLECTION_POINT = "COLLECTION_POINT"
    STORAGE = "STORAGE"
    PROCESSOR = "PROCESSOR"
    SUPPLIER = "SUPPLIER"
    TRANSPORT_HUB = "TRANSPORT_HUB"
    INSTITUTION = "INSTITUTION"


class EconomicNode(BaseModel):
    node_id: str
    node_type: NodeType
    geo_id: str
    commodity: str
    demand: NonNegativeFloat = 0
    supply: NonNegativeFloat = 0
    confidence: float = Field(default=1.0, ge=0, le=1)
    evidence_ids: list[str] = Field(default_factory=list)
    incumbent: bool = True


class EconomicEdge(BaseModel):
    edge_id: str
    source: str
    target: str
    commodity: str
    capacity: NonNegativeFloat
    unit_cost: NonNegativeFloat
    travel_time_hours: NonNegativeFloat = 0
    distance_km: NonNegativeFloat = 0
    reliability: float = Field(default=1.0, ge=0, le=1)
    confidence: float = Field(default=1.0, ge=0, le=1)
    evidence_ids: list[str] = Field(default_factory=list)
    added_by_venture: bool = False


class EconomicGraph(BaseModel):
    graph_id: str
    commodity: str
    unit: str
    nodes: list[EconomicNode]
    edges: list[EconomicEdge]
    methodology_version: str = "graph-v1"

    def validate_references(self) -> None:
        node_ids = {node.node_id for node in self.nodes}
        if len(node_ids) != len(self.nodes):
            raise ValueError("duplicate node_id")
        for edge in self.edges:
            if edge.source not in node_ids or edge.target not in node_ids:
                raise ValueError(f"edge {edge.edge_id} references unknown node")
            if edge.commodity != self.commodity:
                raise ValueError(f"edge {edge.edge_id} commodity mismatch")

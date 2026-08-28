from __future__ import annotations

from dataclasses import dataclass

from backend.models.venture import PrimitiveType


@dataclass(frozen=True)
class SectorAdapter:
    key: str
    label: str
    aliases: tuple[str, ...]
    nic2: str
    commodity: str
    unit: str
    primitive: PrimitiveType
    demand_factor: float
    incumbent_factor: float
    capacity_factor: float
    cost_factor: float
    working_capital_share: float
    licenses: tuple[str, ...]
    stress_variables: tuple[str, ...]


ADAPTERS = (
    SectorAdapter(
        "kirana",
        "Kirana / grocery",
        ("kirana", "grocery", "retail"),
        "47",
        "local retail basket",
        "INR/month",
        PrimitiveType.RETAIL,
        1.25,
        0.78,
        0.24,
        0.18,
        0.55,
        ("local trade registration", "food registration where applicable"),
        ("demand", "input_cost", "rent"),
    ),
    SectorAdapter(
        "poultry",
        "Poultry input and egg aggregation",
        ("poultry", "eggs", "egg"),
        "46",
        "poultry and egg distribution",
        "INR/month",
        PrimitiveType.AGGREGATION,
        1.18,
        0.76,
        0.22,
        0.16,
        0.48,
        ("local trade registration", "food handling compliance"),
        ("selling_price", "feed_cost", "spoilage"),
    ),
    SectorAdapter(
        "fishery",
        "Fish collection and distribution",
        ("fishery", "fisheries", "fish"),
        "46",
        "fish collection and distribution",
        "INR/month",
        PrimitiveType.DISTRIBUTION,
        1.20,
        0.74,
        0.21,
        0.18,
        0.46,
        ("local trade registration", "food handling compliance"),
        ("selling_price", "fuel", "spoilage"),
    ),
    SectorAdapter(
        "food_processing",
        "Small food processing",
        ("food processing", "processing", "mill"),
        "10",
        "processed food",
        "INR/month",
        PrimitiveType.PROCESSING,
        1.16,
        0.80,
        0.18,
        0.20,
        0.32,
        ("FSSAI registration", "local trade registration"),
        ("input_cost", "electricity", "demand"),
    ),
    SectorAdapter(
        "rural_distribution",
        "Rural distribution",
        ("transport", "aggregation", "distribution", "rural distribution"),
        "46",
        "rural distribution service",
        "INR/month",
        PrimitiveType.DISTRIBUTION,
        1.22,
        0.75,
        0.20,
        0.17,
        0.40,
        ("commercial vehicle and trade compliance as applicable",),
        ("fuel", "route_disruption", "demand"),
    ),
)


def resolve_adapter(sector: str) -> SectorAdapter | None:
    normalized = sector.casefold().strip()
    return next(
        (item for item in ADAPTERS if normalized == item.key or normalized in item.aliases), None
    )

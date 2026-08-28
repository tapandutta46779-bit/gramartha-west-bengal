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
    inventory_days: int
    receivable_days: int
    payable_days: int
    space_sqft: int


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
        21,
        2,
        10,
        180,
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
        7,
        5,
        7,
        140,
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
        2,
        3,
        3,
        120,
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
        14,
        7,
        10,
        250,
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
        5,
        10,
        7,
        100,
    ),
    SectorAdapter(
        key="flour_mill",
        label="Flour mill",
        aliases=("flour mill", "flour"),
        nic2="10",
        commodity="milled flour",
        unit="INR/month",
        primitive=PrimitiveType.PROCESSING,
        demand_factor=1.14,
        incumbent_factor=0.80,
        capacity_factor=0.18,
        cost_factor=0.20,
        working_capital_share=0.28,
        licenses=("FSSAI registration", "local trade registration"),
        stress_variables=("grain_input_cost", "electricity", "utilization"),
        inventory_days=12,
        receivable_days=5,
        payable_days=8,
        space_sqft=280,
    ),
    SectorAdapter(
        key="spice_processing",
        label="Spice processing",
        aliases=("spice processing", "spice"),
        nic2="10",
        commodity="processed spices",
        unit="INR/month",
        primitive=PrimitiveType.PROCESSING,
        demand_factor=1.18,
        incumbent_factor=0.79,
        capacity_factor=0.16,
        cost_factor=0.17,
        working_capital_share=0.34,
        licenses=("FSSAI registration", "local trade registration"),
        stress_variables=("spice_input_cost", "packaging", "demand"),
        inventory_days=18,
        receivable_days=6,
        payable_days=10,
        space_sqft=220,
    ),
    SectorAdapter(
        key="mustard_oil",
        label="Mustard oil extraction",
        aliases=("mustard oil", "oil extraction"),
        nic2="10",
        commodity="mustard oil",
        unit="INR/month",
        primitive=PrimitiveType.PROCESSING,
        demand_factor=1.20,
        incumbent_factor=0.81,
        capacity_factor=0.15,
        cost_factor=0.24,
        working_capital_share=0.38,
        licenses=(
            "FSSAI registration",
            "local trade registration",
            "pollution consent if applicable",
        ),
        stress_variables=("seed_input_cost", "oil_price", "utilization"),
        inventory_days=21,
        receivable_days=7,
        payable_days=12,
        space_sqft=350,
    ),
    SectorAdapter(
        key="electronics_mobile",
        label="Electronics / mobile retail",
        aliases=("electronics", "mobile retail", "electronics mobile"),
        nic2="47",
        commodity="electronics retail basket",
        unit="INR/month",
        primitive=PrimitiveType.RETAIL,
        demand_factor=1.12,
        incumbent_factor=0.82,
        capacity_factor=0.15,
        cost_factor=0.16,
        working_capital_share=0.62,
        licenses=("local trade registration", "GST registration when applicable"),
        stress_variables=("inventory_obsolescence", "margin", "demand"),
        inventory_days=30,
        receivable_days=2,
        payable_days=14,
        space_sqft=150,
    ),
    SectorAdapter(
        key="household_distribution",
        label="Household-goods distribution",
        aliases=("household goods", "household distribution"),
        nic2="46",
        commodity="household-goods distribution",
        unit="INR/month",
        primitive=PrimitiveType.DISTRIBUTION,
        demand_factor=1.17,
        incumbent_factor=0.78,
        capacity_factor=0.18,
        cost_factor=0.16,
        working_capital_share=0.50,
        licenses=("local trade registration",),
        stress_variables=("fuel", "inventory", "receivables"),
        inventory_days=18,
        receivable_days=12,
        payable_days=10,
        space_sqft=180,
    ),
)


def resolve_adapter(sector: str) -> SectorAdapter | None:
    normalized = sector.casefold().strip()
    return next(
        (item for item in ADAPTERS if normalized == item.key or normalized in item.aliases), None
    )

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SectorFactors:
    key: str
    customer_segments: tuple[str, ...]
    supplier_types: tuple[str, ...]
    direct_osm_categories: frozenset[str]
    indirect_osm_categories: frozenset[str]
    channels: tuple[str, ...]
    equipment: tuple[str, ...]
    quality_controls: tuple[str, ...]
    operational_factors: tuple[str, ...]
    weather_factors: tuple[str, ...]
    insurance: tuple[str, ...]
    variable_cost_shares: tuple[tuple[str, float], ...]
    fixed_cost_shares: tuple[tuple[str, float], ...]


COMMON_RETAIL_DIRECT = frozenset({"GENERAL_SHOP", "SUPERMARKET", "FOOD_SHOP", "TEA_OR_SWEET_SHOP"})
COMMON_MARKET_INDIRECT = frozenset({"MARKET", "RESTAURANT"})

REGISTRY = {
    "kirana": SectorFactors(
        "kirana",
        ("nearby households", "high-frequency buyers", "price-sensitive households"),
        ("FMCG distributors", "wholesale markets", "local produce suppliers"),
        COMMON_RETAIL_DIRECT,
        COMMON_MARKET_INDIRECT,
        ("walk-in retail", "local delivery", "phone/digital ordering"),
        ("shelving", "counter and weighing equipment", "basic billing device"),
        ("expiry rotation", "daily stockout log", "supplier invoice reconciliation"),
        ("footfall", "rent", "supplier credit", "inventory turnover", "stockouts"),
        (),
        ("inventory/fire protection where economical",),
        (("inventory procurement", 0.88), ("shrinkage/stockout buffer", 0.07), ("delivery", 0.05)),
        (
            ("premises/rent", 0.45),
            ("electricity/digital", 0.20),
            ("maintenance", 0.15),
            ("other overhead", 0.20),
        ),
    ),
    "poultry": SectorFactors(
        "poultry",
        ("households", "small retailers", "restaurants and tea shops"),
        ("egg/poultry producers", "feed/input dealers", "wholesale traders"),
        frozenset({"FOOD_SHOP", "MARKET", "GENERAL_SHOP", "AGRI_INPUT_SHOP"}),
        frozenset({"RESTAURANT", "SUPERMARKET", "TEA_OR_SWEET_SHOP"}),
        ("retailer supply", "market aggregation", "institutional/restaurant supply"),
        ("stackable crates", "weighing scale", "clean handling table"),
        ("breakage log", "batch/source trace", "cleaning and biosecurity checklist"),
        ("feed cost", "mortality", "biosecurity", "temperature", "selling price"),
        ("heat stress", "flood/route disruption"),
        ("stock/transit cover where available",),
        (("egg/bird procurement", 0.84), ("breakage/mortality", 0.08), ("transport", 0.08)),
        (
            ("labour", 0.35),
            ("premises", 0.25),
            ("cleaning/electricity", 0.20),
            ("maintenance", 0.20),
        ),
    ),
    "fishery": SectorFactors(
        "fishery",
        ("households", "fish retailers", "restaurants and institutions"),
        ("fishers/pond operators", "landing/wholesale markets", "ice suppliers"),
        frozenset({"MARKET", "FOOD_SHOP"}),
        frozenset({"RESTAURANT", "SUPERMARKET", "TEA_OR_SWEET_SHOP"}),
        ("market retail", "retailer supply", "restaurant/institution supply"),
        ("insulated boxes", "weighing scale", "washable handling table"),
        ("temperature/time log", "ice-use log", "spoilage and rejection log"),
        ("water/landing supply", "feed", "disease", "cold chain", "transport"),
        ("temperature", "heavy rainfall", "flood/route disruption"),
        ("transit/stock protection where available",),
        (("fish procurement", 0.78), ("ice/spoilage", 0.12), ("fuel/transport", 0.10)),
        (("labour", 0.35), ("premises", 0.20), ("electricity/water", 0.20), ("maintenance", 0.25)),
    ),
    "food_processing": SectorFactors(
        "food_processing",
        ("households", "retailers", "restaurants and institutions"),
        ("farm/wholesale raw-material suppliers", "packaging suppliers"),
        frozenset({"FOOD_SHOP", "MARKET", "TEA_OR_SWEET_SHOP"}),
        frozenset({"SUPERMARKET", "RESTAURANT", "GENERAL_SHOP"}),
        ("retailer distribution", "direct retail", "institutional supply"),
        ("processing machine", "weighing equipment", "sealing/packaging equipment"),
        ("batch records", "cleaning schedule", "weight/yield check", "label compliance"),
        ("raw materials", "electricity", "machine utilization", "conversion yield", "packaging"),
        ("humidity/storage risk", "flood/route disruption"),
        ("machine and stock protection",),
        (("raw materials", 0.74), ("packaging", 0.14), ("power", 0.07), ("wastage", 0.05)),
        (("labour", 0.35), ("premises", 0.25), ("maintenance", 0.25), ("licensing/other", 0.15)),
    ),
    "flour_mill": SectorFactors(
        "flour_mill",
        ("households", "small retailers", "food businesses"),
        ("grain wholesalers", "farmer groups", "packaging suppliers"),
        frozenset({"FOOD_SHOP", "MARKET"}),
        frozenset({"SUPERMARKET", "GENERAL_SHOP"}),
        ("walk-in milling", "packaged retail", "retailer supply"),
        ("flour mill", "weighing scale", "sieves and dust control"),
        ("moisture check", "cleaning log", "yield/weight reconciliation"),
        ("grain input cost", "electricity", "utilization", "conversion yield"),
        ("humidity/storage risk",),
        ("machine and fire protection",),
        (("grain", 0.80), ("power", 0.10), ("packaging", 0.06), ("loss", 0.04)),
        (("labour", 0.35), ("premises", 0.25), ("maintenance", 0.30), ("other", 0.10)),
    ),
    "spice_processing": SectorFactors(
        "spice_processing",
        ("households", "retailers", "restaurants"),
        ("spice wholesalers/farmers", "packaging suppliers"),
        frozenset({"FOOD_SHOP", "MARKET", "TEA_OR_SWEET_SHOP"}),
        frozenset({"SUPERMARKET", "RESTAURANT", "GENERAL_SHOP"}),
        ("packaged retail", "retailer supply", "restaurant supply"),
        ("grinder", "sieving unit", "sealer", "weighing scale"),
        ("batch trace", "adulteration control", "cleaning log", "pack weight check"),
        ("raw spice cost", "packaging", "power", "seasonal demand"),
        ("humidity/storage risk",),
        ("machine and stock protection",),
        (("raw spices", 0.72), ("packaging", 0.16), ("power", 0.07), ("loss", 0.05)),
        (("labour", 0.35), ("premises", 0.25), ("maintenance", 0.25), ("other", 0.15)),
    ),
    "mustard_oil": SectorFactors(
        "mustard_oil",
        ("households", "food retailers", "restaurants"),
        ("oilseed farmers/wholesalers", "packaging suppliers"),
        frozenset({"FOOD_SHOP", "MARKET"}),
        frozenset({"SUPERMARKET", "GENERAL_SHOP"}),
        ("packaged retail", "retailer supply", "bulk food-business supply"),
        ("oil expeller", "filter unit", "storage drums", "filling/sealing equipment"),
        ("seed moisture check", "batch yield log", "filtration check", "label compliance"),
        ("seed cost", "oil price", "utilization", "power", "by-product realization"),
        ("humidity/storage risk",),
        ("machine, fire and stock protection",),
        (("mustard seed", 0.78), ("packaging", 0.10), ("power", 0.07), ("loss", 0.05)),
        (("labour", 0.32), ("premises", 0.22), ("maintenance", 0.31), ("other", 0.15)),
    ),
    "electronics_mobile": SectorFactors(
        "electronics_mobile",
        ("households", "students/youth", "small businesses"),
        ("authorized distributors", "regional wholesalers", "repair/accessory suppliers"),
        frozenset({"ELECTRONICS_SHOP"}),
        frozenset({"GENERAL_SHOP", "SUPERMARKET", "MARKET", "HOUSEHOLD_SHOP"}),
        ("walk-in retail", "assisted digital ordering", "institution/small-business supply"),
        ("secure display", "billing device", "basic testing tools"),
        ("serial/warranty record", "return log", "stock ageing report"),
        ("inventory capital", "obsolescence", "margin", "returns/warranty", "brand competition"),
        (),
        ("inventory/theft protection",),
        (("inventory procurement", 0.89), ("returns/warranty", 0.06), ("delivery", 0.05)),
        (("premises", 0.40), ("labour", 0.25), ("digital/electricity", 0.20), ("other", 0.15)),
    ),
    "household_distribution": SectorFactors(
        "household_distribution",
        ("small retailers", "households", "institutions"),
        ("regional manufacturers", "wholesale markets", "FMCG distributors"),
        frozenset({"HOUSEHOLD_SHOP", "GENERAL_SHOP", "MARKET"}),
        frozenset({"SUPERMARKET", "ELECTRONICS_SHOP"}),
        ("retailer route", "institutional supply", "direct bulk order"),
        ("storage racks", "weighing/packing tools", "delivery handling equipment"),
        ("dispatch reconciliation", "damage log", "receivable ageing"),
        ("fuel", "inventory", "receivables", "route utilization"),
        ("flood/route disruption",),
        ("vehicle, stock and transit protection",),
        (
            ("inventory procurement", 0.82),
            ("fuel/transport", 0.10),
            ("damage", 0.03),
            ("credit loss", 0.05),
        ),
        (("labour", 0.32), ("storage", 0.28), ("vehicle maintenance", 0.25), ("other", 0.15)),
    ),
    "rural_distribution": SectorFactors(
        "rural_distribution",
        ("small retailers", "producers", "institutions and small businesses"),
        ("regional wholesalers", "producer groups", "transport contractors"),
        frozenset({"MARKET", "TRANSPORT_HUB"}),
        frozenset({"GENERAL_SHOP", "SUPERMARKET", "INDUSTRIAL", "WAREHOUSE"}),
        ("fixed retailer route", "aggregator service", "institutional delivery"),
        ("rented/shared vehicle access", "handling crates", "route/phone tools"),
        ("trip sheet", "load-factor log", "fuel and maintenance log"),
        ("fuel", "road access", "vehicle efficiency", "load factor", "empty return", "downtime"),
        ("heavy rain/flood route disruption",),
        ("commercial vehicle and goods-in-transit protection",),
        (
            ("transport/fuel", 0.55),
            ("handled goods/packaging", 0.30),
            ("loss/damage", 0.05),
            ("other trip cost", 0.10),
        ),
        (("labour", 0.35), ("vehicle maintenance", 0.35), ("digital/phone", 0.10), ("other", 0.20)),
    ),
    "dairy": SectorFactors(
        "dairy",
        ("households", "tea/sweet shops", "restaurants", "schools/institutions"),
        ("milk producers", "collection centres", "cooperatives/processors"),
        frozenset({"DAIRY", "FOOD_SHOP"}),
        frozenset({"GENERAL_SHOP", "SUPERMARKET", "TEA_OR_SWEET_SHOP", "MARKET", "RESTAURANT"}),
        ("door delivery", "retailer/tea-shop supply", "institutional supply"),
        ("food-grade cans", "weighing/testing kit", "insulated transport"),
        ("collection time log", "temperature/acidity check", "rejection/spoilage log"),
        ("yield", "feed/fodder", "animal health", "spoilage", "chilling", "route time"),
        ("heat stress", "flood/route disruption"),
        ("livestock, vehicle and stock/transit protection where applicable",),
        (
            ("milk procurement", 0.80),
            ("spoilage", 0.07),
            ("fuel/transport", 0.08),
            ("testing/packaging", 0.05),
        ),
        (("labour", 0.35), ("premises/chilling", 0.25), ("maintenance", 0.25), ("other", 0.15)),
    ),
}


ALIASES = {
    "food processing": "food_processing",
    "flour mill": "flour_mill",
    "spice processing": "spice_processing",
    "mustard oil": "mustard_oil",
    "electronics": "electronics_mobile",
    "household goods": "household_distribution",
    "transport": "rural_distribution",
    "milk": "dairy",
}


def sector_factors(sector: str) -> SectorFactors | None:
    key = ALIASES.get(sector.casefold().strip(), sector.casefold().strip())
    return REGISTRY.get(key)

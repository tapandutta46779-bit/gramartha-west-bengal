from __future__ import annotations

DISTRICT_ALIASES = {
    "24 paraganas north": "North Twenty Four Parganas",
    "north twenty four parganas": "North Twenty Four Parganas",
    "24 paraganas south": "South Twenty Four Parganas",
    "south twenty four parganas": "South Twenty Four Parganas",
    "coochbehar": "Koch Bihar",
    "koch bihar": "Koch Bihar",
    "dinajpur dakshin": "Dakshin Dinajpur",
    "dakshin dinajpur": "Dakshin Dinajpur",
    "dinajpur uttar": "Uttar Dinajpur",
    "uttar dinajpur": "Uttar Dinajpur",
    "darjeeling": "Darjiling",
    "darjiling": "Darjiling",
    "hooghly": "Hugli",
    "hugli": "Hugli",
    "howrah": "Haora",
    "haora": "Haora",
    "kalimpong": "Kalimpong",
    "medinipur east": "Purba Medinipur",
    "purba medinipur": "Purba Medinipur",
    "medinipur west": "Paschim Medinipur",
    "paschim medinipur": "Paschim Medinipur",
    "purulia": "Puruliya",
    "puruliya": "Puruliya",
    "paschim bardhaman": "Paschim Barddhaman",
    "paschim barddhaman": "Paschim Barddhaman",
}


def canonical_district(value: str) -> str | None:
    normalized = value.casefold().strip()
    if normalized in {"barddhaman", "bardhaman"}:
        return None
    return DISTRICT_ALIASES.get(normalized, value.strip())

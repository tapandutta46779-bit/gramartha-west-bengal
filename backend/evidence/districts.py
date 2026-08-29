from __future__ import annotations

CURRENT_WEST_BENGAL_DISTRICTS = (
    "Alipurduar",
    "Bankura",
    "Birbhum",
    "Cooch Behar",
    "Dakshin Dinajpur",
    "Darjeeling",
    "Hooghly",
    "Howrah",
    "Jalpaiguri",
    "Jhargram",
    "Kalimpong",
    "Kolkata",
    "Malda",
    "Murshidabad",
    "Nadia",
    "North 24 Parganas",
    "Paschim Bardhaman",
    "Paschim Medinipur",
    "Purba Bardhaman",
    "Purba Medinipur",
    "Purulia",
    "South 24 Parganas",
    "Uttar Dinajpur",
)

DISTRICT_ALIASES = {
    "north 24 parganas": "North Twenty Four Parganas",
    "24 paraganas north": "North Twenty Four Parganas",
    "north twenty four parganas": "North Twenty Four Parganas",
    "south 24 parganas": "South Twenty Four Parganas",
    "24 paraganas south": "South Twenty Four Parganas",
    "south twenty four parganas": "South Twenty Four Parganas",
    "coochbehar": "Koch Bihar",
    "cooch behar": "Koch Bihar",
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
    "malda": "Maldah",
    "maldah": "Maldah",
    "paschim bardhaman": "Paschim Barddhaman",
    "paschim barddhaman": "Paschim Barddhaman",
    "purba bardhaman": "Purba Barddhaman",
}

CURRENT_DISTRICT_ALIASES = {
    "alipurduar": "Alipurduar",
    "bankura": "Bankura",
    "birbhum": "Birbhum",
    "cooch behar": "Cooch Behar",
    "coochbehar": "Cooch Behar",
    "koch bihar": "Cooch Behar",
    "dakshin dinajpur": "Dakshin Dinajpur",
    "dinajpur dakshin": "Dakshin Dinajpur",
    "darjeeling": "Darjeeling",
    "darjiling": "Darjeeling",
    "hooghly": "Hooghly",
    "hugli": "Hooghly",
    "howrah": "Howrah",
    "haora": "Howrah",
    "jalpaiguri": "Jalpaiguri",
    "jhargram": "Jhargram",
    "kalimpong": "Kalimpong",
    "kolkata": "Kolkata",
    "malda": "Malda",
    "maldah": "Malda",
    "murshidabad": "Murshidabad",
    "nadia": "Nadia",
    "north 24 parganas": "North 24 Parganas",
    "north twenty four parganas": "North 24 Parganas",
    "24 paraganas north": "North 24 Parganas",
    "paschim bardhaman": "Paschim Bardhaman",
    "paschim barddhaman": "Paschim Bardhaman",
    "purba bardhaman": "Purba Bardhaman",
    # DS057 uses Bardhaman alongside a separate Paschim Bardhaman group.
    "bardhaman": "Purba Bardhaman",
    "paschim medinipur": "Paschim Medinipur",
    "medinipur west": "Paschim Medinipur",
    "purba medinipur": "Purba Medinipur",
    "medinipur east": "Purba Medinipur",
    "purulia": "Purulia",
    "puruliya": "Purulia",
    "south 24 parganas": "South 24 Parganas",
    "south twenty four parganas": "South 24 Parganas",
    "24 paraganas south": "South 24 Parganas",
    "uttar dinajpur": "Uttar Dinajpur",
    "dinajpur uttar": "Uttar Dinajpur",
}


def canonical_district(value: str) -> str | None:
    normalized = value.casefold().strip()
    if normalized in {"barddhaman", "bardhaman"}:
        return None
    return DISTRICT_ALIASES.get(normalized, value.strip())


def current_district(value: str, *, source: str | None = None) -> str | None:
    """Return the canonical current product district without rewriting unsafe history.

    `Bardhaman` is accepted only for the post-split DS057 publisher layer. Historical
    Census-2011 `Barddhaman` requires a locality crosswalk to a successor district.
    """

    normalized = value.casefold().strip()
    if normalized == "barddhaman":
        return None
    if normalized == "bardhaman" and source not in {None, "DS057"}:
        return None
    return CURRENT_DISTRICT_ALIASES.get(normalized)


def district_current_id(name: str) -> str:
    canonical = current_district(name) or name.strip()
    slug = "_".join(canonical.upper().replace("&", "AND").split())
    return f"WB:CURRENT:DISTRICT:{slug}"

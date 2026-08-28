from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher

from backend.models.geography import (
    GeographicIdentity,
    GeographicResolution,
    ResolutionMethod,
)

from .store import EvidenceStore

DISTRICT_ALIASES = {
    "north 24 parganas": "24 paraganas north",
    "north twenty four parganas": "24 paraganas north",
    "south 24 parganas": "24 paraganas south",
    "south twenty four parganas": "24 paraganas south",
    "purba bardhaman": "bardhaman",
    "paschim bardhaman": "paschim bardhaman",
    "uttar dinajpur": "dinajpur uttar",
    "dakshin dinajpur": "dinajpur dakshin",
    "cooch behar": "coochbehar",
    "malda": "maldah",
    "purba medinipur": "medinipur east",
    "paschim medinipur": "medinipur west",
}


def normalize_name(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).casefold()
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def canonical_district(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = normalize_name(value)
    return DISTRICT_ALIASES.get(normalized, normalized)


def resolve_locality(
    store: EvidenceStore,
    *,
    locality: str,
    district: str | None = None,
    state: str = "West Bengal",
    parent: str | None = None,
    allow_fuzzy: bool = False,
) -> GeographicResolution:
    if normalize_name(state) != "west bengal":
        return GeographicResolution(
            query_state=state,
            query_district=district,
            query_locality=locality,
            resolution_method=ResolutionMethod.NOT_FOUND,
            confidence=0,
            ambiguity_flags=["STATE_OUTSIDE_SUPPORTED_SCOPE"],
        )
    target_locality = normalize_name(locality)
    target_district = canonical_district(district)
    target_parent = normalize_name(parent) if parent else None
    identities = store.all_geographies()
    locality_matches = [
        item for item in identities if normalize_name(item.locality) == target_locality
    ]
    district_matches = [
        item
        for item in locality_matches
        if target_district is None or canonical_district(item.district) == target_district
    ]
    hierarchy_matches = [
        item
        for item in district_matches
        if target_parent is None
        or normalize_name(item.block or item.municipality or "") == target_parent
    ]
    alias_used = bool(
        district
        and normalize_name(district) in DISTRICT_ALIASES
        and DISTRICT_ALIASES[normalize_name(district)] != normalize_name(district)
    )
    if len(hierarchy_matches) == 1:
        item = hierarchy_matches[0]
        return GeographicResolution(
            query_state=state,
            query_district=district,
            query_locality=locality,
            resolved_geo_id=item.geo_id,
            resolution_method=(
                ResolutionMethod.EXACT_ALIAS if alias_used else ResolutionMethod.EXACT_HIERARCHY
            ),
            confidence=0.96 if alias_used else 1.0,
            source_ids=item.source_ids,
            matched_ids=_matched_ids(item),
            candidates=[item],
        )
    if len(hierarchy_matches) > 1:
        return GeographicResolution(
            query_state=state,
            query_district=district,
            query_locality=locality,
            resolution_method=ResolutionMethod.AMBIGUOUS,
            confidence=0,
            ambiguity_flags=["DUPLICATE_LOCALITY_NAME", "PARENT_REQUIRED"],
            candidates=hierarchy_matches[:20],
        )
    if not allow_fuzzy:
        return GeographicResolution(
            query_state=state,
            query_district=district,
            query_locality=locality,
            resolution_method=ResolutionMethod.NOT_FOUND,
            confidence=0,
            ambiguity_flags=["NO_EXACT_MATCH", "FUZZY_MATCH_NOT_ENABLED"],
        )
    pool = [
        item
        for item in identities
        if target_district is None or canonical_district(item.district) == target_district
    ]
    ranked = sorted(
        (
            (SequenceMatcher(None, target_locality, normalize_name(item.locality)).ratio(), item)
            for item in pool
        ),
        key=lambda pair: (-pair[0], pair[1].geo_id),
    )
    if not ranked or ranked[0][0] < 0.9:
        return GeographicResolution(
            query_state=state,
            query_district=district,
            query_locality=locality,
            resolution_method=ResolutionMethod.NOT_FOUND,
            confidence=0,
            ambiguity_flags=["NO_HIGH_CONFIDENCE_MATCH"],
        )
    best_score, best = ranked[0]
    close = [item for score, item in ranked if best_score - score < 0.05][:20]
    if len(close) > 1:
        return GeographicResolution(
            query_state=state,
            query_district=district,
            query_locality=locality,
            resolution_method=ResolutionMethod.AMBIGUOUS,
            confidence=0,
            ambiguity_flags=["FUZZY_MATCH_AMBIGUOUS"],
            candidates=close,
        )
    return GeographicResolution(
        query_state=state,
        query_district=district,
        query_locality=locality,
        resolved_geo_id=best.geo_id,
        resolution_method=ResolutionMethod.FUZZY_FLAGGED,
        confidence=best_score * 0.8,
        source_ids=best.source_ids,
        matched_ids=_matched_ids(best),
        ambiguity_flags=["FUZZY_NAME_MATCH_REQUIRES_REVIEW"],
        candidates=[best],
    )


def _matched_ids(item: GeographicIdentity) -> dict[str, str]:
    values = {"internal_geo_id": item.geo_id}
    if item.lgd_code:
        values["lgd_code"] = item.lgd_code
    if item.census_code:
        values["census_code"] = item.census_code
    if item.osm_ids:
        values["osm_ids"] = ",".join(item.osm_ids)
    return values

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import unicodedata
from collections import defaultdict

from backend.models.geography import (
    CurrentGeoEntity,
    GeoCrosswalk,
    GeographicIdentity,
    HistoricalGeoEntity,
)

from .districts import (
    CURRENT_WEST_BENGAL_DISTRICTS,
    current_district,
    district_current_id,
)

STATE_CURRENT_ID = "WB:CURRENT:STATE:WEST_BENGAL"

HISTORICAL_SUCCESSORS = {
    "barddhaman": {"Purba Bardhaman", "Paschim Bardhaman"},
    "darjiling": {"Darjeeling", "Kalimpong"},
    "jalpaiguri": {"Jalpaiguri", "Alipurduar"},
    "paschim medinipur": {"Paschim Medinipur", "Jhargram"},
}


def normalize_name(value: str | None) -> str:
    if not value:
        return ""
    normalized = unicodedata.normalize("NFKD", value).casefold()
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", normalized).strip()


def stable_current_id(entity_type: str, *parts: str) -> str:
    value = "|".join(normalize_name(part) for part in parts)
    digest = hashlib.sha256(value.encode()).hexdigest()[:16]
    return f"WB:CURRENT:{entity_type.upper()}:{digest}"


def rebuild_current_geography(connection: sqlite3.Connection) -> dict[str, int]:
    """Build a current product layer while preserving every raw source identity.

    DS057 is used as the post-split product hierarchy because it contains separate publisher
    groups for the current successor districts. Census-2011 rows remain historical. They crosswalk
    to a locality only after an exact normalized locality match and, when available, a compatible
    parent match. Ambiguous split-district rows are deliberately left without a locality mapping.
    """

    connection.row_factory = sqlite3.Row
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS current_geo_entity (
            canonical_current_id TEXT PRIMARY KEY,
            canonical_name TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            parent_current_id TEXT,
            district_current_id TEXT NOT NULL,
            current_district TEXT NOT NULL,
            official_code TEXT,
            effective_from TEXT,
            effective_to TEXT,
            source_geo_id TEXT,
            source TEXT NOT NULL,
            payload TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_current_geo_search
            ON current_geo_entity(current_district, canonical_name, entity_type);
        CREATE INDEX IF NOT EXISTS idx_current_geo_source
            ON current_geo_entity(source_geo_id);
        CREATE TABLE IF NOT EXISTS historical_geo_entity (
            source TEXT NOT NULL,
            source_geo_id TEXT PRIMARY KEY,
            source_name TEXT NOT NULL,
            source_parent TEXT,
            source_district TEXT NOT NULL,
            observation_year INTEGER NOT NULL,
            payload TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS geo_crosswalk (
            source TEXT NOT NULL,
            source_geo_id TEXT NOT NULL,
            canonical_current_id TEXT NOT NULL,
            relation TEXT NOT NULL,
            confidence REAL NOT NULL,
            effective_from TEXT,
            effective_to TEXT,
            notes TEXT NOT NULL,
            PRIMARY KEY (source, source_geo_id, canonical_current_id)
        );
        CREATE INDEX IF NOT EXISTS idx_geo_crosswalk_current
            ON geo_crosswalk(canonical_current_id);
        DELETE FROM current_geo_entity;
        DELETE FROM historical_geo_entity;
        DELETE FROM geo_crosswalk;
        """
    )
    for district in CURRENT_WEST_BENGAL_DISTRICTS:
        entity = CurrentGeoEntity(
            canonical_current_id=district_current_id(district),
            canonical_name=district,
            entity_type="DISTRICT",
            parent_current_id=STATE_CURRENT_ID,
            district_current_id=district_current_id(district),
            current_district=district,
            source="CURRENT_PRODUCT_CANONICAL_V1",
        )
        _insert_current(connection, entity)

    raw = [
        GeographicIdentity.model_validate_json(row["payload"])
        for row in connection.execute(
            "SELECT payload FROM geographic_identity ORDER BY geo_id"
        ).fetchall()
    ]
    current_rows = [item for item in raw if item.geo_id.startswith("DS057:")]
    historical_rows = [item for item in raw if item.geo_id.startswith("CENSUS2011:")]
    canonical_by_key: dict[tuple[str, str, str, str], CurrentGeoEntity] = {}
    locality_index: dict[str, list[CurrentGeoEntity]] = defaultdict(list)

    for item in current_rows:
        district = current_district(item.district, source="DS057")
        if district is None:
            continue
        parent_name, parent_type = _parent(item)
        parent_id = district_current_id(district)
        if parent_name:
            parent_id = stable_current_id(parent_type, district, parent_name)
            parent = CurrentGeoEntity(
                canonical_current_id=parent_id,
                canonical_name=parent_name,
                entity_type=parent_type,
                parent_current_id=district_current_id(district),
                district_current_id=district_current_id(district),
                current_district=district,
                source="DS057_POST_SPLIT_PUBLISHER_HIERARCHY",
            )
            _insert_current(connection, parent)
        canonical_id = stable_current_id(
            item.locality_type,
            district,
            parent_name or "",
            item.locality,
        )
        payload = item.model_copy(
            update={
                "district": district,
                "quality_flags": [
                    *item.quality_flags,
                    "CURRENT_PRODUCT_DISTRICT_CANONICALIZED_FROM_DS057",
                ],
            }
        )
        entity = CurrentGeoEntity(
            canonical_current_id=canonical_id,
            canonical_name=item.locality,
            entity_type=item.locality_type,
            parent_current_id=parent_id,
            district_current_id=district_current_id(district),
            current_district=district,
            official_code=item.lgd_code,
            source_geo_id=item.geo_id,
            source="DS057_POST_SPLIT_PUBLISHER_HIERARCHY",
            payload=payload,
        )
        key = (
            district,
            item.locality_type,
            normalize_name(parent_name),
            normalize_name(item.locality),
        )
        existing = canonical_by_key.get(key)
        if existing is None or _quality(entity) > _quality(existing):
            canonical_by_key[key] = entity

    for entity in canonical_by_key.values():
        _insert_current(connection, entity)
        locality_index[normalize_name(entity.canonical_name)].append(entity)

    exact_crosswalk = 0
    district_context = 0
    unsafe_split = 0
    for item in historical_rows:
        parent_name, _ = _parent(item)
        historical = HistoricalGeoEntity(
            source="CENSUS2011",
            source_geo_id=item.geo_id,
            source_name=item.locality,
            source_parent=parent_name,
            source_district=item.district,
            observation_year=2011,
        )
        connection.execute(
            "INSERT INTO historical_geo_entity VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                historical.source,
                historical.source_geo_id,
                historical.source_name,
                historical.source_parent,
                historical.source_district,
                historical.observation_year,
                item.model_dump_json(),
            ),
        )
        allowed = _historical_successors(item.district)
        candidates = [
            entity
            for entity in locality_index.get(normalize_name(item.locality), [])
            if entity.current_district in allowed
        ]
        if parent_name:
            parent_matches = [
                entity
                for entity in candidates
                if normalize_name(_entity_parent_name(entity)) == normalize_name(parent_name)
            ]
            if parent_matches:
                candidates = parent_matches
        candidates = _unique_entities(candidates)
        if len(candidates) == 1:
            _insert_crosswalk(
                connection,
                GeoCrosswalk(
                    source="CENSUS2011",
                    source_geo_id=item.geo_id,
                    canonical_current_id=candidates[0].canonical_current_id,
                    relation="EXACT_NAME_AND_COMPATIBLE_CURRENT_HIERARCHY",
                    confidence=0.95 if parent_name else 0.85,
                    notes=(
                        "Historical observation remains dated 2011; crosswalk does not make the "
                        "observation current."
                    ),
                ),
            )
            exact_crosswalk += 1
            continue
        direct = current_district(item.district, source="CENSUS2011")
        if direct and len(allowed) == 1:
            _insert_crosswalk(
                connection,
                GeoCrosswalk(
                    source="CENSUS2011",
                    source_geo_id=item.geo_id,
                    canonical_current_id=district_current_id(direct),
                    relation="CURRENT_DISTRICT_CONTEXT_ONLY",
                    confidence=0.55,
                    notes=(
                        "No unique current locality match; historical evidence may be used only "
                        "as a district-context baseline."
                    ),
                ),
            )
            district_context += 1
        elif len(allowed) > 1:
            unsafe_split += 1

    connection.commit()
    counts = {
        "current_districts": connection.execute(
            "SELECT count(*) FROM current_geo_entity WHERE entity_type = 'DISTRICT'"
        ).fetchone()[0],
        "current_subordinate_units": connection.execute(
            "SELECT count(*) FROM current_geo_entity WHERE entity_type NOT IN "
            "('DISTRICT', 'VILLAGE', 'TOWN', 'WARD')"
        ).fetchone()[0],
        "current_localities": connection.execute(
            "SELECT count(*) FROM current_geo_entity WHERE payload IS NOT NULL"
        ).fetchone()[0],
        "historical_entities": len(historical_rows),
        "exact_locality_crosswalks": exact_crosswalk,
        "district_context_crosswalks": district_context,
        "unsafe_split_unmapped": unsafe_split,
    }
    return counts


def _parent(item: GeographicIdentity) -> tuple[str | None, str]:
    if item.municipality:
        return item.municipality, "MUNICIPALITY"
    if item.block:
        return item.block, "BLOCK"
    if item.subdivision:
        return item.subdivision, "SUBDIVISION"
    return None, "DISTRICT"


def _entity_parent_name(entity: CurrentGeoEntity) -> str:
    payload = entity.payload
    if payload is None:
        return ""
    return payload.municipality or payload.block or payload.subdivision or ""


def _historical_successors(district: str) -> set[str]:
    normalized = normalize_name(district)
    if normalized in HISTORICAL_SUCCESSORS:
        return HISTORICAL_SUCCESSORS[normalized]
    direct = current_district(district, source="CENSUS2011")
    return {direct} if direct else set()


def _quality(entity: CurrentGeoEntity) -> tuple[int, int, int]:
    payload = entity.payload
    if payload is None:
        return (0, 0, 0)
    return (
        int(payload.latitude is not None and payload.longitude is not None),
        int(bool(payload.lgd_code or payload.census_code)),
        len(payload.source_ids),
    )


def _unique_entities(entities: list[CurrentGeoEntity]) -> list[CurrentGeoEntity]:
    return list({item.canonical_current_id: item for item in entities}.values())


def _insert_current(connection: sqlite3.Connection, entity: CurrentGeoEntity) -> None:
    connection.execute(
        """
        INSERT OR REPLACE INTO current_geo_entity VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            entity.canonical_current_id,
            entity.canonical_name,
            entity.entity_type,
            entity.parent_current_id,
            entity.district_current_id,
            entity.current_district,
            entity.official_code,
            entity.effective_from,
            entity.effective_to,
            entity.source_geo_id,
            entity.source,
            entity.payload.model_dump_json() if entity.payload else None,
        ),
    )


def _insert_crosswalk(connection: sqlite3.Connection, crosswalk: GeoCrosswalk) -> None:
    connection.execute(
        "INSERT INTO geo_crosswalk VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            crosswalk.source,
            crosswalk.source_geo_id,
            crosswalk.canonical_current_id,
            crosswalk.relation,
            crosswalk.confidence,
            crosswalk.effective_from,
            crosswalk.effective_to,
            crosswalk.notes,
        ),
    )


def audit_row_payload(row: sqlite3.Row) -> dict:
    value = dict(row)
    if value.get("payload"):
        value["payload"] = json.loads(value["payload"])
    return value

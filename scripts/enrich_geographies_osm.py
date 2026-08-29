from __future__ import annotations

import argparse
import json
import re
import sqlite3
import unicodedata
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

from shapely import wkt
from shapely.geometry import Point

from backend.evidence.store import EvidenceStore


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).casefold()
    value = re.sub(r"\([^)]*\)", " ", value)
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", value).split())


def normalize_district(value: str) -> str:
    normalized = normalize(value)
    normalized = normalized.replace("twenty four", "24").replace("twentyfour", "24")
    return " ".join(part for part in normalized.split() if part not in {"district", "zilla"})


DISTRICT_TARGETS = {
    "24 paraganas north": ("north 24 parganas",),
    "24 paraganas south": ("south 24 parganas",),
    "barddhaman": ("purba bardhaman", "paschim bardhaman"),
    "bardhaman": ("purba bardhaman",),
    "coochbehar": ("cooch behar",),
    "darjiling": ("darjeeling",),
    "dinajpur dakshin": ("dakshin dinajpur",),
    "dinajpur uttar": ("uttar dinajpur",),
    "haora": ("howrah",),
    "hugli": ("hooghly",),
    "koch bihar": ("cooch behar",),
    "medinipur east": ("purba medinipur",),
    "medinipur west": ("paschim medinipur",),
    "puruliya": ("purulia",),
}


def district_targets(value: str) -> tuple[str, ...]:
    normalized = normalize_district(value)
    return DISTRICT_TARGETS.get(normalized, (normalized,))


def district_context_matches(tags: dict[str, str], district: str) -> bool:
    contextual = " ".join(
        str(tags.get(key, "")) for key in ("addr:district", "is_in:district", "district", "is_in")
    )
    normalized_context = normalize_district(contextual)
    return bool(contextual) and any(
        target in normalized_context for target in district_targets(district)
    )


def enrich(evidence_database: Path, osm_database: Path, report_path: Path) -> dict:
    osm = sqlite3.connect(osm_database)
    osm.row_factory = sqlite3.Row
    places: dict[str, list[sqlite3.Row]] = defaultdict(list)
    for row in osm.execute(
        "SELECT osm_type, osm_id, name, lat, lon, tags_json FROM osm_entity "
        "WHERE category = 'PLACE' AND name IS NOT NULL"
    ):
        places[normalize(row["name"])].append(row)
    district_areas: dict[str, list] = defaultdict(list)
    for row in osm.execute("SELECT name, geometry_wkt FROM admin_area WHERE admin_level = 5"):
        district_areas[normalize_district(row["name"])].append(wkt.loads(row["geometry_wkt"]))
    subdistrict_areas: dict[str, list] = defaultdict(list)
    for row in osm.execute("SELECT name, geometry_wkt FROM admin_area WHERE admin_level = 6"):
        subdistrict_areas[normalize(row["name"])].append(wkt.loads(row["geometry_wkt"]))

    store = EvidenceStore(evidence_database)
    geographies = store.all_geographies()
    geography_name_counts = Counter(
        (district_targets(geography.district), normalize(geography.locality))
        for geography in geographies
    )
    geography_unit_counts = Counter(
        (
            district_targets(geography.district),
            normalize(geography.locality),
            normalize(geography.block or geography.subdivision or ""),
        )
        for geography in geographies
    )
    matched_by_method = Counter()
    ambiguous = 0
    unmatched = 0
    removed_previous = 0
    examples: dict[str, list[str]] = defaultdict(list)
    with store.transaction():
        for geography in geographies:
            if "OSM_PLACE_COORDINATE_PROXY" in geography.quality_flags:
                geography = geography.model_copy(
                    update={
                        "latitude": None,
                        "longitude": None,
                        "osm_ids": [],
                        "source_ids": [
                            item for item in geography.source_ids if item != "DS071-OSM"
                        ],
                        "quality_flags": [
                            item
                            for item in geography.quality_flags
                            if item
                            not in {
                                "OSM_PLACE_COORDINATE_PROXY",
                                "EXACT_NAME_UNIQUE",
                                "EXACT_NAME_AND_OSM_DISTRICT",
                                "EXACT_NAME_IN_DISTRICT_BOUNDARY",
                                "EXACT_NAME_IN_SUBDISTRICT_BOUNDARY",
                            }
                        ],
                    }
                )
                store.put_geography(geography)
                removed_previous += 1
            candidates = places.get(normalize(geography.locality), [])
            had_place_candidates = bool(candidates)
            district_geometries = [
                geometry
                for target in district_targets(geography.district)
                for geometry in district_areas.get(target, [])
            ]
            geography_key = (district_targets(geography.district), normalize(geography.locality))
            unit_name = normalize(geography.block or geography.subdivision or "")
            unit_key = (*geography_key, unit_name)
            requires_unit_disambiguation = geography_name_counts[geography_key] > 1
            unit_geometries = subdistrict_areas.get(unit_name, []) if unit_name else []
            contextual_matches = []
            for candidate in candidates:
                tags = json.loads(candidate["tags_json"])
                point = Point(candidate["lon"], candidate["lat"])
                district_tag_match = district_context_matches(tags, geography.district)
                district_polygon_match = any(
                    geometry.covers(point) for geometry in district_geometries
                )
                if not (district_tag_match or district_polygon_match):
                    continue
                if requires_unit_disambiguation:
                    if geography_unit_counts[unit_key] > 1:
                        continue
                    if any(geometry.covers(point) for geometry in unit_geometries):
                        contextual_matches.append((candidate, "EXACT_NAME_IN_SUBDISTRICT_BOUNDARY"))
                elif district_tag_match:
                    contextual_matches.append((candidate, "EXACT_NAME_AND_OSM_DISTRICT"))
                else:
                    contextual_matches.append((candidate, "EXACT_NAME_IN_DISTRICT_BOUNDARY"))
            if len(contextual_matches) == 1:
                candidates = [contextual_matches[0][0]]
                method = contextual_matches[0][1]
            else:
                candidates = []
                method = ""
            if len(candidates) == 1:
                candidate = candidates[0]
                store.put_geography(
                    geography.model_copy(
                        update={
                            "latitude": candidate["lat"],
                            "longitude": candidate["lon"],
                            "osm_ids": sorted(
                                {
                                    *geography.osm_ids,
                                    f"{candidate['osm_type']}/{candidate['osm_id']}",
                                }
                            ),
                            "source_ids": sorted({*geography.source_ids, "DS071-OSM"}),
                            "quality_flags": sorted(
                                {
                                    *geography.quality_flags,
                                    "OSM_PLACE_COORDINATE_PROXY",
                                    method,
                                }
                            ),
                        }
                    )
                )
                matched_by_method[method] += 1
            elif len(candidates) > 1:
                ambiguous += 1
                if len(examples["ambiguous"]) < 25:
                    description = (
                        f"{geography.district} | {geography.locality} | "
                        f"{len(candidates)} candidates"
                    )
                    examples["ambiguous"].append(description)
            else:
                if had_place_candidates:
                    ambiguous += 1
                    if len(examples["ambiguous"]) < 25:
                        examples["ambiguous"].append(
                            f"{geography.district} | {geography.locality} | unsafe name reuse"
                        )
                else:
                    unmatched += 1
                    if len(examples["unmatched"]) < 25:
                        examples["unmatched"].append(f"{geography.district} | {geography.locality}")
    total = sum(matched_by_method.values()) + ambiguous + unmatched
    result = {
        "created_at": datetime.now(UTC).isoformat(),
        "methodology_version": "DS057_OSM_PLACE_CROSSWALK_V4_HIERARCHICAL_BOUNDARY",
        "evidence_database": str(evidence_database),
        "osm_database": str(osm_database),
        "total_geographies": total,
        "matched": sum(matched_by_method.values()),
        "matched_by_method": dict(matched_by_method),
        "previous_proxy_coordinates_removed": removed_previous,
        "ambiguous_not_merged": ambiguous,
        "unmatched": unmatched,
        "examples": examples,
        "limitations": [
            "OSM coordinates are volunteered proxy evidence, not official LGD/Census codes.",
            "Only exact normalized names are considered; fuzzy matches are not auto-applied.",
            "Coordinates require an exact OSM district tag or containment in the matched "
            "OSM district boundary.",
            "Unique locality spelling alone is never sufficient for coordinate attachment.",
            "Names duplicated inside a district require unique block/subdistrict containment.",
        ],
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Add unambiguous OSM place coordinates")
    parser.add_argument("evidence_database", type=Path)
    parser.add_argument("osm_database", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(enrich(args.evidence_database, args.osm_database, args.report), indent=2))


if __name__ == "__main__":
    main()

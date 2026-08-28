from __future__ import annotations

import argparse
import json
import re
import sqlite3
import unicodedata
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

from backend.evidence.store import EvidenceStore


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).casefold()
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", value).split())


def enrich(evidence_database: Path, osm_database: Path, report_path: Path) -> dict:
    osm = sqlite3.connect(osm_database)
    osm.row_factory = sqlite3.Row
    places: dict[str, list[sqlite3.Row]] = defaultdict(list)
    for row in osm.execute(
        "SELECT osm_type, osm_id, name, lat, lon, tags_json FROM osm_entity "
        "WHERE category = 'PLACE' AND name IS NOT NULL"
    ):
        places[normalize(row["name"])].append(row)

    store = EvidenceStore(evidence_database)
    matched_by_method = Counter()
    ambiguous = 0
    unmatched = 0
    examples: dict[str, list[str]] = defaultdict(list)
    with store.transaction():
        for geography in store.all_geographies():
            candidates = places.get(normalize(geography.locality), [])
            method = "EXACT_NAME_UNIQUE"
            if len(candidates) > 1:
                district = normalize(geography.district)
                district_matches = []
                for candidate in candidates:
                    tags = json.loads(candidate["tags_json"])
                    contextual = " ".join(
                        str(tags.get(key, ""))
                        for key in ("addr:district", "is_in:district", "is_in")
                    )
                    if district and district in normalize(contextual):
                        district_matches.append(candidate)
                if len(district_matches) == 1:
                    candidates = district_matches
                    method = "EXACT_NAME_AND_OSM_DISTRICT"
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
                unmatched += 1
                if len(examples["unmatched"]) < 25:
                    examples["unmatched"].append(f"{geography.district} | {geography.locality}")
    total = sum(matched_by_method.values()) + ambiguous + unmatched
    result = {
        "created_at": datetime.now(UTC).isoformat(),
        "methodology_version": "DS057_OSM_PLACE_CROSSWALK_V1",
        "evidence_database": str(evidence_database),
        "osm_database": str(osm_database),
        "total_geographies": total,
        "matched": sum(matched_by_method.values()),
        "matched_by_method": dict(matched_by_method),
        "ambiguous_not_merged": ambiguous,
        "unmatched": unmatched,
        "examples": examples,
        "limitations": [
            "OSM coordinates are volunteered proxy evidence, not official LGD/Census codes.",
            "Only exact normalized names are considered; fuzzy matches are not auto-applied.",
            "Duplicate place names are not merged unless one OSM district tag disambiguates them.",
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

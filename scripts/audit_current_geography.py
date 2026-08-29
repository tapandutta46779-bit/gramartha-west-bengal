from __future__ import annotations

import csv
import json
import os
from pathlib import Path

os.environ.setdefault("SIH26091_SQLITE_PATH", "data/sih26091_phase2.sqlite")
os.environ.setdefault("SIH26091_OSM_SQLITE_PATH", "data/west_bengal_osm.sqlite")

from backend.api.contracts import AnalyzeRequest  # noqa: E402
from backend.evidence.current_geography import STATE_CURRENT_ID  # noqa: E402
from backend.evidence.store import EvidenceStore  # noqa: E402
from backend.service import analyze  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS"
JSON_OUTPUT = OUTPUT_DIR / "WEST_BENGAL_GEOGRAPHY_AUDIT.json"
CSV_OUTPUT = OUTPUT_DIR / "WEST_BENGAL_GEOGRAPHY_AUDIT.csv"
MD_OUTPUT = OUTPUT_DIR / "WEST_BENGAL_GEOGRAPHY_AUDIT.md"


def main() -> None:
    store = EvidenceStore(os.environ["SIH26091_SQLITE_PATH"])
    rows = []
    for district in store.list_districts():
        counts = _type_counts(store, district)
        sample = store.connection.execute(
            "SELECT canonical_name, source_geo_id, payload FROM current_geo_entity "
            "WHERE current_district = ? AND payload IS NOT NULL "
            "ORDER BY canonical_name, canonical_current_id LIMIT 1",
            (district,),
        ).fetchone()
        total = sum(counts.get(kind, 0) for kind in ("TOWN", "VILLAGE", "WARD"))
        coordinates = store.connection.execute(
            "SELECT count(*) FROM current_geo_entity WHERE current_district = ? "
            "AND payload IS NOT NULL AND json_extract(payload, '$.latitude') IS NOT NULL "
            "AND json_extract(payload, '$.longitude') IS NOT NULL",
            (district,),
        ).fetchone()[0]
        crosswalks = store.connection.execute(
            "SELECT count(*) FROM geo_crosswalk x JOIN current_geo_entity c "
            "ON c.canonical_current_id = x.canonical_current_id "
            "WHERE c.current_district = ? AND x.relation = "
            "'EXACT_NAME_AND_COMPATIBLE_CURRENT_HIERARCHY'",
            (district,),
        ).fetchone()[0]
        search_ok = False
        analysis_status = "NO_SAMPLE"
        selected = False
        sample_name = None
        sample_geo_id = None
        if sample:
            sample_name = sample["canonical_name"]
            sample_geo_id = sample["source_geo_id"]
            search_results = store.search_geographies(sample_name, 10, district)
            search_ok = any(item.geo_id == sample_geo_id for item in search_results)
            decision = analyze(
                AnalyzeRequest(
                    geo_id=sample_geo_id,
                    capital=100_000,
                    business_category="kirana",
                    analysis_mode="quick",
                ),
                store,
            )
            analysis_status = decision.status.value
            selected = decision.selected_venture is not None
        prior_count = len(store.get_regional_priors(district, "1")) + len(
            store.get_regional_priors(district, "2")
        )
        rows.append(
            {
                "district": district,
                "subdivisions": counts.get("SUBDIVISION", 0),
                "blocks": counts.get("BLOCK", 0),
                "municipalities": counts.get("MUNICIPALITY", 0),
                "towns": counts.get("TOWN", 0),
                "villages": counts.get("VILLAGE", 0),
                "wards": counts.get("WARD", 0),
                "localities": total,
                "coordinate_coverage_count": coordinates,
                "coordinate_coverage_rate": coordinates / total if total else 0,
                "census_crosswalk_count": crosswalks,
                "osm_coverage_count": coordinates,
                "survey_prior_count": prior_count,
                "search_sample": sample_name,
                "search_result": "PASS" if search_ok else "FAIL",
                "analysis_smoke_result": analysis_status,
                "analysis_selected_candidate": selected,
                "known_limitations": (
                    "Current product hierarchy is DS057-derived, not a complete official LGD "
                    "extract; coordinate and exact Census crosswalk coverage are partial."
                ),
            }
        )
    hierarchy = _hierarchy_checks(store)
    report = {
        "audit_version": "WEST_BENGAL_CURRENT_GEOGRAPHY_AUDIT_V1",
        "canonical_layer": "CURRENT_PRODUCT_GEOGRAPHY_V1",
        "district_count": len(rows),
        "all_districts_unique": len({row["district"] for row in rows}) == len(rows) == 23,
        "hierarchy_checks": hierarchy,
        "districts": rows,
        "limitations": [
            "LGD bulk download is CAPTCHA-gated and was not acquired in this run.",
            "DS057 publisher labels define the provisional current product hierarchy.",
            "Historical Census observations retain year 2011 after crosswalk.",
            "Exact locality crosswalks require compatible current hierarchy; unsafe split-era "
            "matches remain unmapped.",
        ],
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    JSON_OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    with CSV_OUTPUT.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    MD_OUTPUT.write_text(_markdown(report), encoding="utf-8")
    print(
        json.dumps(
            {"outputs": [str(JSON_OUTPUT), str(CSV_OUTPUT), str(MD_OUTPUT)], **hierarchy}, indent=2
        )
    )


def _type_counts(store: EvidenceStore, district: str) -> dict[str, int]:
    rows = store.connection.execute(
        "SELECT entity_type, count(*) count FROM current_geo_entity "
        "WHERE current_district = ? GROUP BY entity_type",
        (district,),
    ).fetchall()
    return {row["entity_type"]: row["count"] for row in rows}


def _hierarchy_checks(store: EvidenceStore) -> dict[str, int]:
    orphans = store.connection.execute(
        "SELECT count(*) FROM current_geo_entity child LEFT JOIN current_geo_entity parent "
        "ON parent.canonical_current_id = child.parent_current_id "
        "WHERE child.parent_current_id IS NOT NULL AND child.parent_current_id != ? "
        "AND parent.canonical_current_id IS NULL",
        (STATE_CURRENT_ID,),
    ).fetchone()[0]
    wrong_district = store.connection.execute(
        "SELECT count(*) FROM current_geo_entity child JOIN current_geo_entity parent "
        "ON parent.canonical_current_id = child.parent_current_id "
        "WHERE child.current_district != parent.current_district"
    ).fetchone()[0]
    same_parent_duplicates = store.connection.execute(
        "SELECT count(*) FROM (SELECT parent_current_id, lower(canonical_name), entity_type, "
        "count(*) n FROM current_geo_entity GROUP BY parent_current_id, "
        "lower(canonical_name), entity_type HAVING n > 1)"
    ).fetchone()[0]
    cross_district_source_leakage = store.connection.execute(
        "SELECT count(*) FROM (SELECT source_geo_id, count(DISTINCT current_district) n "
        "FROM current_geo_entity WHERE source_geo_id IS NOT NULL GROUP BY source_geo_id "
        "HAVING n > 1)"
    ).fetchone()[0]
    return {
        "orphan_nodes": orphans,
        "wrong_parent_district": wrong_district,
        "same_parent_duplicates": same_parent_duplicates,
        "cross_district_source_leakage": cross_district_source_leakage,
    }


def _markdown(report: dict) -> str:
    lines = [
        "# West Bengal Current Geography Audit",
        "",
        f"Canonical layer: `{report['canonical_layer']}`.",
        "",
        "The customer-facing layer contains exactly 23 current product districts. Original "
        "source geography remains unchanged. Census-2011 entities are stored separately and "
        "crosswalked only when hierarchy-compatible.",
        "",
        "| District | Blocks | Municipalities | Towns | Villages | Wards | Coordinates | "
        "Census crosswalks | Priors | Search | Analysis |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in report["districts"]:
        lines.append(
            f"| {row['district']} | {row['blocks']} | {row['municipalities']} | "
            f"{row['towns']} | {row['villages']} | {row['wards']} | "
            f"{row['coordinate_coverage_count']} | {row['census_crosswalk_count']} | "
            f"{row['survey_prior_count']} | {row['search_result']} | "
            f"{row['analysis_smoke_result']} |"
        )
    lines.extend(["", "## Hierarchy checks", ""])
    for key, value in report["hierarchy_checks"].items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()

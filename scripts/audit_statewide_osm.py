from __future__ import annotations

import argparse
import csv
import json
import os
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

from backend.evidence.districts import CURRENT_WEST_BENGAL_DISTRICTS
from backend.evidence.store import EvidenceStore
from backend.service import _spatial_context

SECTORS = (
    "dairy",
    "kirana",
    "poultry",
    "fishery",
    "food processing",
    "flour mill",
    "spice processing",
    "mustard oil",
    "household goods",
    "electronics",
    "transport",
)


def audit(evidence_path: Path, osm_path: Path, output_dir: Path) -> dict:
    os.environ["SIH26091_OSM_SQLITE_PATH"] = str(osm_path)
    store = EvidenceStore(evidence_path)
    by_district: dict[str, list] = defaultdict(list)
    for geography in store.all_geographies():
        by_district[geography.district].append(geography)

    rows = []
    for district in CURRENT_WEST_BENGAL_DISTRICTS:
        geographies = by_district.get(district, [])
        coordinate_linked = next(
            (item for item in geographies if item.latitude is not None),
            None,
        )
        unresolved = next(
            (item for item in geographies if item.latitude is None),
            None,
        )
        samples = []
        for item in (coordinate_linked, unresolved):
            if item is not None and item.geo_id not in {sample.geo_id for sample in samples}:
                samples.append(item)
        for geography in samples:
            for sector in SECTORS:
                failure = None
                try:
                    spatial = _spatial_context(geography, 10, sector, store)
                except Exception as error:  # audit must record rather than conceal failures
                    spatial = {"catchment": {}, "competition": {}}
                    failure = f"{type(error).__name__}: {error}"
                catchment = spatial.get("catchment", {})
                competition = spatial.get("competition", {})
                direct = int(competition.get("direct_count", 0) or 0)
                indirect = int(competition.get("indirect_count", 0) or 0)
                named = len(competition.get("likely_direct_competitors", [])) + len(
                    competition.get("likely_indirect_competitors", [])
                )
                unnamed_displayed = sum(
                    not bool(item.get("name"))
                    for key in ("likely_direct_competitors", "likely_indirect_competitors")
                    for item in competition.get(key, [])
                )
                rows.append(
                    {
                        "district": district,
                        "geo_id": geography.geo_id,
                        "locality": geography.locality,
                        "locality_type": geography.locality_type,
                        "sector": sector,
                        "coordinate_quality": catchment.get("center", {}).get(
                            "coordinate_quality"
                        ),
                        "scan_executed": bool(catchment),
                        "direct_count": direct,
                        "indirect_count": indirect,
                        "displayed_candidate_count": named,
                        "displayed_unnamed_count": unnamed_displayed,
                        "mapped_unnamed_count": int(
                            competition.get("direct_unnamed_count", 0) or 0
                        )
                        + int(competition.get("indirect_unnamed_count", 0) or 0),
                        "candidate_returned": direct + indirect + named > 0,
                        "nearest_market": bool(catchment.get("nearest_market")),
                        "failure": failure,
                    }
                )

    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "statewide_osm_matrix.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    total = len(rows)
    summary = {
        "created_at": datetime.now(UTC).isoformat(),
        "evidence_database": str(evidence_path),
        "osm_database": str(osm_path),
        "districts_expected": len(CURRENT_WEST_BENGAL_DISTRICTS),
        "districts_tested": len({row["district"] for row in rows}),
        "localities_tested": len({row["geo_id"] for row in rows}),
        "sectors_tested": list(SECTORS),
        "matrix_rows": total,
        "resolved_coordinate_rate": sum(bool(row["coordinate_quality"]) for row in rows) / total,
        "scan_execution_rate": sum(row["scan_executed"] for row in rows) / total,
        "candidate_return_rate": sum(row["candidate_returned"] for row in rows) / total,
        "nearest_market_rate": sum(row["nearest_market"] for row in rows) / total,
        "displayed_unnamed_candidates": sum(
            row["displayed_unnamed_count"] for row in rows
        ),
        "failures": [row for row in rows if row["failure"]],
        "caveat": (
            "District representative-point scans are district context only; they are not "
            "locality coordinates or proof of local competitors. OSM is incomplete "
            "volunteered data."
        ),
        "matrix_csv": str(csv_path),
    }
    (output_dir / "statewide_osm_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit statewide OSM spatial execution")
    parser.add_argument("--evidence", type=Path, default=Path("data/sih26091_phase2.sqlite"))
    parser.add_argument("--osm", type=Path, default=Path("data/west_bengal_osm.sqlite"))
    parser.add_argument("--output", type=Path, default=Path("output/validation/osm_statewide"))
    args = parser.parse_args()
    print(json.dumps(audit(args.evidence, args.osm, args.output), indent=2))


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import csv
import gzip
import json
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from statistics import median

from backend.evidence.districts import CURRENT_WEST_BENGAL_DISTRICTS
from backend.evidence.store import EvidenceStore
from backend.pipeline.sector_factors import sector_factors
from backend.service import (
    _OFFICIAL_LOCALITY_COORDINATE_PROXIES,
    _deduplicate_entities,
    _entity_display_name,
)
from backend.spatial.osm_store import OsmSpatialStore

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

MATRIX_FIELDS = (
    "district",
    "geo_id",
    "locality",
    "locality_type",
    "sector",
    "coordinate_quality",
    "scan_executed",
    "direct_count",
    "indirect_count",
    "named_direct_in_radius",
    "named_indirect_in_radius",
    "unnamed_mapped_in_radius",
    "named_in_discovery_radius",
    "candidate_returned",
    "failure",
)


def _parent_key(item) -> tuple[str, str, str] | None:
    if item.municipality:
        return item.district, "municipality", item.municipality
    if item.block:
        return item.district, "block", item.block
    return None


def _parent_proxies(geographies) -> dict[tuple[str, str, str], dict]:
    linked: dict[tuple[str, str, str], list[tuple[float, float]]] = defaultdict(list)
    for item in geographies:
        key = _parent_key(item)
        if key and item.latitude is not None and item.longitude is not None:
            linked[key].append((float(item.latitude), float(item.longitude)))
    proxies = {}
    for key, coordinates in linked.items():
        if len(coordinates) < 2:
            continue
        latitude = median(value[0] for value in coordinates)
        longitude = median(value[1] for value in coordinates)
        if any(
            abs(lat - latitude) > 0.20 or abs(lon - longitude) > 0.22 for lat, lon in coordinates
        ):
            continue
        proxies[key] = {
            "latitude": latitude,
            "longitude": longitude,
            "coordinate_quality": f"{key[1].upper()}_SIBLING_MEDIAN_PROXY",
            "coordinate_reference_count": len(coordinates),
            "coordinate_parent": key[2],
        }
    return proxies


def _coordinate(item, parent_proxies, district_proxies):
    if item.latitude is not None and item.longitude is not None:
        return {
            "latitude": float(item.latitude),
            "longitude": float(item.longitude),
            "coordinate_quality": "OSM_PLACE_PROXY",
        }
    if item.geo_id in _OFFICIAL_LOCALITY_COORDINATE_PROXIES:
        return _OFFICIAL_LOCALITY_COORDINATE_PROXIES[item.geo_id]
    key = _parent_key(item)
    if key and key in parent_proxies:
        return parent_proxies[key]
    return district_proxies.get(item.district)


def _scan_cache_key(coordinate: dict) -> tuple[float, float]:
    return round(coordinate["latitude"], 7), round(coordinate["longitude"], 7)


def _scan_metrics(osm: OsmSpatialStore, cache_key: tuple[float, float]) -> dict[str, dict]:
    entities_10 = osm.radial_catchment(*cache_key, 10, limit=50_000).entities
    entities_30 = osm.radial_catchment(*cache_key, 30, limit=50_000).entities
    metrics = {}
    for sector in SECTORS:
        factors = sector_factors(sector)
        direct_categories = factors.direct_osm_categories
        indirect_categories = factors.indirect_osm_categories - direct_categories
        direct = _deduplicate_entities(
            [item for item in entities_10 if item.category in direct_categories], *cache_key
        )
        indirect = _deduplicate_entities(
            [item for item in entities_10 if item.category in indirect_categories], *cache_key
        )
        named_discovery = _deduplicate_entities(
            [
                item
                for item in entities_30
                if item.category in direct_categories | indirect_categories
                and _entity_display_name(item)[0]
            ],
            *cache_key,
        )
        named_direct = sum(bool(_entity_display_name(item)[0]) for item in direct)
        named_indirect = sum(bool(_entity_display_name(item)[0]) for item in indirect)
        unnamed = len(direct) + len(indirect) - named_direct - named_indirect
        metrics[sector] = {
            "scan_executed": True,
            "direct_count": len(direct),
            "indirect_count": len(indirect),
            "named_direct_in_radius": named_direct,
            "named_indirect_in_radius": named_indirect,
            "unnamed_mapped_in_radius": unnamed,
            "named_in_discovery_radius": len(named_discovery),
            "candidate_returned": bool(direct or indirect or named_discovery),
            "failure": "",
        }
    return metrics


def audit(evidence_path: Path, osm_path: Path, output_dir: Path) -> dict:
    evidence = EvidenceStore(evidence_path)
    osm = OsmSpatialStore(osm_path)
    geographies = evidence.all_geographies()
    parent_proxies = _parent_proxies(geographies)
    district_proxies = {
        district: osm.administrative_area_proxy(district)
        for district in CURRENT_WEST_BENGAL_DISTRICTS
    }
    metrics_cache = {}
    coordinate_quality_counts = Counter()
    district_stats = defaultdict(Counter)
    failures = []
    unresolved_coordinate_count = 0
    totals = Counter()
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "all_localities_all_sectors_osm_matrix.csv.gz"
    matrix_handle = gzip.open(csv_path, "wt", newline="", encoding="utf-8")
    writer = csv.DictWriter(matrix_handle, fieldnames=MATRIX_FIELDS)
    writer.writeheader()

    for geography in geographies:
        coordinate = _coordinate(geography, parent_proxies, district_proxies)
        if coordinate is None:
            unresolved_coordinate_count += 1
            failure = "NO_DEFENSIBLE_COORDINATE_OR_LABELLED_PROXY"
            failures.append(
                {
                    "district": geography.district,
                    "geo_id": geography.geo_id,
                    "locality": geography.locality,
                    "failure": failure,
                }
            )
            for sector in SECTORS:
                row = {
                    "district": geography.district,
                    "geo_id": geography.geo_id,
                    "locality": geography.locality,
                    "locality_type": geography.locality_type,
                    "sector": sector,
                    "coordinate_quality": "UNAVAILABLE",
                    "scan_executed": False,
                    "direct_count": 0,
                    "indirect_count": 0,
                    "named_direct_in_radius": 0,
                    "named_indirect_in_radius": 0,
                    "unnamed_mapped_in_radius": 0,
                    "named_in_discovery_radius": 0,
                    "candidate_returned": False,
                    "failure": failure,
                }
                writer.writerow(row)
                totals["matrix_rows"] += 1
                district_stats[geography.district]["matrix_rows"] += 1
            continue

        quality = coordinate["coordinate_quality"]
        coordinate_quality_counts[quality] += 1
        cache_key = _scan_cache_key(coordinate)
        scan_failure = ""
        try:
            if cache_key not in metrics_cache:
                metrics_cache[cache_key] = _scan_metrics(osm, cache_key)
            scan_metrics = metrics_cache[cache_key]
        except Exception as error:
            scan_failure = f"{type(error).__name__}: {error}"
            failures.append(
                {
                    "district": geography.district,
                    "geo_id": geography.geo_id,
                    "locality": geography.locality,
                    "failure": scan_failure,
                }
            )
            scan_metrics = {
                sector: {
                    "scan_executed": False,
                    "direct_count": 0,
                    "indirect_count": 0,
                    "named_direct_in_radius": 0,
                    "named_indirect_in_radius": 0,
                    "unnamed_mapped_in_radius": 0,
                    "named_in_discovery_radius": 0,
                    "candidate_returned": False,
                    "failure": scan_failure,
                }
                for sector in SECTORS
            }

        for sector in SECTORS:
            metric = scan_metrics[sector]
            row = {
                "district": geography.district,
                "geo_id": geography.geo_id,
                "locality": geography.locality,
                "locality_type": geography.locality_type,
                "sector": sector,
                "coordinate_quality": quality,
                **metric,
            }
            writer.writerow(row)
            totals["matrix_rows"] += 1
            totals["scan_executed"] += int(metric["scan_executed"])
            totals["candidate_returned"] += int(metric["candidate_returned"])
            totals["named_in_radius"] += (
                metric["named_direct_in_radius"] + metric["named_indirect_in_radius"]
            )
            totals["unnamed_in_radius"] += metric["unnamed_mapped_in_radius"]
            stats = district_stats[geography.district]
            stats["matrix_rows"] += 1
            stats["scan_executed"] += int(row["scan_executed"])
            stats["candidate_returned"] += int(row["candidate_returned"])
            stats["named_in_radius"] += (
                metric["named_direct_in_radius"] + metric["named_indirect_in_radius"]
            )
            stats["unnamed_in_radius"] += metric["unnamed_mapped_in_radius"]

    matrix_handle.close()
    failure_path = output_dir / "exact_failures.json"
    failure_path.write_text(
        json.dumps(failures, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    total = totals["matrix_rows"]
    summary = {
        "created_at": datetime.now(UTC).isoformat(),
        "scope": "EVERY_SUPPORTED_WEST_BENGAL_LOCALITY_X_EVERY_SUPPORTED_SECTOR",
        "evidence_database": str(evidence_path),
        "osm_database": str(osm_path),
        "osm_metadata": osm.metadata(),
        "districts_expected": len(CURRENT_WEST_BENGAL_DISTRICTS),
        "districts_tested": len({item.district for item in geographies}),
        "localities_tested": len(geographies),
        "sectors_tested": list(SECTORS),
        "matrix_rows": total,
        "unique_scan_centers": len(metrics_cache),
        "coordinate_resolution_rate": (len(geographies) - unresolved_coordinate_count)
        / len(geographies),
        "coordinate_quality_counts": dict(sorted(coordinate_quality_counts.items())),
        "scan_execution_rate": totals["scan_executed"] / total,
        "candidate_return_rate": totals["candidate_returned"] / total,
        "named_in_radius_total": totals["named_in_radius"],
        "unnamed_mapped_in_radius_total": totals["unnamed_in_radius"],
        "failures_count": len(failures),
        "district_statistics": {key: dict(value) for key, value in sorted(district_stats.items())},
        "matrix_csv_gzip": str(csv_path),
        "exact_failures_json": str(failure_path),
        "interpretation_caveat": (
            "A named-candidate zero is retained when the expanded statewide index genuinely "
            "contains no sector-mapped named OSM feature in the bounded scan. OSM is volunteered "
            "proxy evidence, not a complete business registry; counts do not measure capacity, "
            "sales or market share. Parent and district proxies are explicitly labelled and "
            "are not exact locality centroids."
        ),
    }
    (output_dir / "all_localities_all_sectors_osm_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit every supported locality and sector")
    parser.add_argument("--evidence", type=Path, default=Path("data/sih26091_phase2.sqlite"))
    parser.add_argument("--osm", type=Path, default=Path("data/west_bengal_osm.sqlite"))
    parser.add_argument(
        "--output", type=Path, default=Path("output/validation/osm_all_localities_all_sectors")
    )
    args = parser.parse_args()
    print(json.dumps(audit(args.evidence, args.osm, args.output), indent=2))


if __name__ == "__main__":
    main()

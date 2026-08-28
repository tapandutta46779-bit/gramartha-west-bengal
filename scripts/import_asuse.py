from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

from scripts.import_hces import _number, file_sha256


def build_asuse_priors(input_dir: Path, mapping_path: Path, output_path: Path) -> dict:
    mapping = json.loads(mapping_path.read_text())
    spec = mapping["enterprises"]
    source = input_dir / spec["file"]
    measures = spec["measure_columns"]
    totals = defaultdict(lambda: defaultdict(float))
    counts = defaultdict(int)
    with source.open(newline="", encoding=spec.get("encoding", "utf-8-sig")) as handle:
        for row in csv.DictReader(handle):
            if row[spec["state_column"]].strip() not in set(mapping["west_bengal_values"]):
                continue
            nic = row[spec["nic_column"]].strip()
            group = (
                row.get(spec.get("district_column", ""), "").strip(),
                row[spec["sector_column"]].strip(),
                nic[:2],
            )
            weight = _number(row, spec["weight_column"])
            if weight <= 0:
                continue
            totals[group]["weight"] += weight
            for measure, column in measures.items():
                totals[group][measure] += weight * _number(row, column)
            counts[group] += 1
    priors = []
    for (district, sector, nic2), values in sorted(totals.items()):
        weight = values.pop("weight")
        priors.append(
            {
                "district": district or None,
                "rural_urban_sector": sector,
                "nic_2_digit": nic2,
                "sample_enterprises": counts[(district, sector, nic2)],
                "weighted_enterprises": weight,
                "weighted_means": {measure: value / weight for measure, value in values.items()},
                "evidence_type": "SAMPLED_PRIOR",
            }
        )
    result = {
        "dataset_id": mapping["dataset_id"],
        "dataset_version": mapping["dataset_version"],
        "official_source_url": mapping["official_source_url"],
        "created_at": datetime.now(UTC).isoformat(),
        "methodology_version": "ASUSE_WEIGHTED_SECTOR_PRIOR_V1",
        "geographic_claim": "Sampled sector prior; not exact incumbent capacity or sales.",
        "inputs": [
            {
                "file": source.name,
                "size_bytes": source.stat().st_size,
                "sha256": file_sha256(source),
            },
            {
                "file": mapping_path.name,
                "size_bytes": mapping_path.stat().st_size,
                "sha256": file_sha256(mapping_path),
            },
        ],
        "priors": priors,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Import extracted official ASUSE CSV files")
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("mapping", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(build_asuse_priors(args.input_dir, args.mapping, args.output), indent=2))


if __name__ == "__main__":
    main()

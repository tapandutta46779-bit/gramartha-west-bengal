from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _number(row: dict[str, str], column: str | None, default: float = 0) -> float:
    if not column:
        return default
    value = row.get(column, "").strip().replace(",", "")
    return float(value) if value else default


def _key(row: dict[str, str], columns: list[str]) -> tuple[str, ...]:
    return tuple(row[column].strip() for column in columns)


def build_hces_priors(input_dir: Path, mapping_path: Path, output_path: Path) -> dict:
    mapping = json.loads(mapping_path.read_text())
    household_spec = mapping["households"]
    item_spec = mapping["items"]
    household_path = input_dir / household_spec["file"]
    item_path = input_dir / item_spec["file"]
    household_join = household_spec["join_columns"]
    item_join = item_spec["join_columns"]
    if len(household_join) != len(item_join):
        raise ValueError("household and item join column counts differ")

    households = {}
    with household_path.open(
        newline="", encoding=household_spec.get("encoding", "utf-8-sig")
    ) as handle:
        for row in csv.DictReader(handle):
            state_value = row[household_spec["state_column"]].strip()
            if state_value not in set(mapping["west_bengal_values"]):
                continue
            households[_key(row, household_join)] = {
                "district": row.get(household_spec.get("district_column", ""), "").strip(),
                "nss_region": row.get(household_spec.get("nss_region_column", ""), "").strip(),
                "sector": row[household_spec["sector_column"]].strip(),
                "weight": _number(row, household_spec["weight_column"]),
                "household_size": _number(row, household_spec["household_size_column"]),
            }
    categories = {
        str(item_code): category
        for category, item_codes in mapping["item_categories"].items()
        for item_code in item_codes
    }
    totals = defaultdict(lambda: defaultdict(float))
    sample_households: dict[tuple, set[tuple[str, ...]]] = defaultdict(set)
    with item_path.open(newline="", encoding=item_spec.get("encoding", "utf-8-sig")) as handle:
        for row in csv.DictReader(handle):
            household_key = _key(row, item_join)
            household = households.get(household_key)
            if not household:
                continue
            category = categories.get(row[item_spec["item_code_column"]].strip())
            if not category:
                continue
            recall_days = _number(
                row,
                item_spec.get("recall_days_column"),
                float(item_spec.get("default_recall_days", 30)),
            )
            if recall_days <= 0:
                raise ValueError("recall days must be positive")
            group = (
                household["district"],
                household["nss_region"],
                household["sector"],
                category,
            )
            weight = household["weight"]
            monthly_factor = 30 / recall_days
            totals[group]["weighted_persons"] += weight * household["household_size"]
            totals[group]["weighted_quantity"] += (
                weight * _number(row, item_spec.get("quantity_column")) * monthly_factor
            )
            totals[group]["weighted_expenditure"] += (
                weight * _number(row, item_spec.get("expenditure_column")) * monthly_factor
            )
            sample_households[group].add(household_key)
    priors = []
    for group, values in sorted(totals.items()):
        denominator = values["weighted_persons"]
        if denominator <= 0:
            continue
        district, nss_region, sector, category = group
        priors.append(
            {
                "district": district or None,
                "nss_region": nss_region or None,
                "rural_urban_sector": sector,
                "category": category,
                "monthly_quantity_per_capita": values["weighted_quantity"] / denominator,
                "monthly_expenditure_inr_per_capita": (
                    values["weighted_expenditure"] / denominator
                ),
                "quantity_unit": item_spec.get("quantity_unit", "SOURCE_UNIT"),
                "sample_households": len(sample_households[group]),
                "weighted_persons": denominator,
                "evidence_type": "SAMPLED_PRIOR",
            }
        )
    result = {
        "dataset_id": mapping["dataset_id"],
        "dataset_version": mapping["dataset_version"],
        "official_source_url": mapping["official_source_url"],
        "created_at": datetime.now(UTC).isoformat(),
        "methodology_version": "HCES_WEIGHTED_PRIOR_V1",
        "geographic_claim": "Sampled state/district/NSS-region prior; not village observation.",
        "inputs": [
            {
                "file": path.name,
                "size_bytes": path.stat().st_size,
                "sha256": file_sha256(path),
            }
            for path in (household_path, item_path, mapping_path)
        ],
        "west_bengal_households": len(households),
        "priors": priors,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Import extracted official HCES CSV files")
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("mapping", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(build_hces_priors(args.input_dir, args.mapping, args.output), indent=2))


if __name__ == "__main__":
    main()

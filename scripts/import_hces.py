from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import zipfile
from collections import defaultdict
from contextlib import ExitStack
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
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


def _normalize_code(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    try:
        numeric = Decimal(value)
    except InvalidOperation:
        return value
    if not numeric:
        return "0"
    normalized = format(numeric.normalize(), "f")
    return normalized.rstrip("0").rstrip(".") if "." in normalized else normalized


def _key(
    row: dict[str, str], columns: list[str], normalize_codes: bool = False
) -> tuple[str, ...]:
    normalizer = _normalize_code if normalize_codes else str.strip
    return tuple(normalizer(row[column]) for column in columns)


def build_hces_priors(input_path: Path, mapping_path: Path, output_path: Path) -> dict:
    mapping = json.loads(mapping_path.read_text())
    household_spec = mapping["households"]
    item_spec = mapping["items"]
    household_join = household_spec["join_columns"]
    item_join = item_spec["join_columns"]
    normalize_join_codes = mapping.get("normalize_join_codes", False)
    if len(household_join) != len(item_join):
        raise ValueError("household and item join column counts differ")

    zip_archive = zipfile.ZipFile(input_path) if input_path.is_file() else None

    def open_csv(stack: ExitStack, spec: dict):
        if zip_archive:
            raw = stack.enter_context(zip_archive.open(spec["file"]))
            return stack.enter_context(
                io.TextIOWrapper(
                    raw, encoding=spec.get("encoding", "utf-8-sig"), errors="strict", newline=""
                )
            )
        return stack.enter_context(
            (input_path / spec["file"]).open(
                newline="", encoding=spec.get("encoding", "utf-8-sig")
            )
        )

    households = {}
    with ExitStack() as stack:
        handle = open_csv(stack, household_spec)
        for row in csv.DictReader(handle):
            if any(
                row.get(column, "").strip() not in {str(value) for value in values}
                for column, values in household_spec.get("row_filters", {}).items()
            ):
                continue
            state_value = row[household_spec["state_column"]].strip()
            if state_value not in set(mapping["west_bengal_values"]):
                continue
            households[_key(row, household_join, normalize_join_codes)] = {
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
    household_amounts = defaultdict(lambda: defaultdict(float))
    with ExitStack() as stack:
        handle = open_csv(stack, item_spec)
        for row in csv.DictReader(handle):
            category = categories.get(row[item_spec["item_code_column"]].strip())
            if not category:
                continue
            household_key = _key(row, item_join, normalize_join_codes)
            household = households.get(household_key)
            if not household:
                continue
            recall_days = _number(
                row,
                item_spec.get("recall_days_column"),
                float(item_spec.get("default_recall_days", 30)),
            )
            if recall_days <= 0:
                raise ValueError("recall days must be positive")
            monthly_factor = 30 / recall_days
            household_amounts[(household_key, category)]["quantity"] += _number(
                row, item_spec.get("quantity_column")
            ) * monthly_factor
            household_amounts[(household_key, category)]["expenditure"] += _number(
                row, item_spec.get("expenditure_column")
            ) * monthly_factor
    totals = defaultdict(lambda: defaultdict(float))
    sample_households: dict[tuple, int] = defaultdict(int)
    for household_key, household in households.items():
        size = household["household_size"]
        if size <= 0:
            continue
        person_weight = household["weight"] * size
        for category in mapping["item_categories"]:
            group = (
                household["district"],
                household["nss_region"],
                household["sector"],
                category,
            )
            amount = household_amounts[(household_key, category)]
            quantity_per_capita = amount["quantity"] / size
            expenditure_per_capita = amount["expenditure"] / size
            totals[group]["weighted_persons"] += person_weight
            totals[group]["weighted_quantity"] += person_weight * quantity_per_capita
            totals[group]["weighted_expenditure"] += person_weight * expenditure_per_capita
            totals[group]["sum_weight_squared"] += person_weight**2
            totals[group]["sum_weighted_quantity_squared"] += (
                person_weight * quantity_per_capita**2
            )
            totals[group]["sum_weighted_expenditure_squared"] += (
                person_weight * expenditure_per_capita**2
            )
            sample_households[group] += 1
    priors = []
    for group, values in sorted(totals.items()):
        denominator = values["weighted_persons"]
        if denominator <= 0:
            continue
        district, nss_region, sector, category = group
        quantity_mean = values["weighted_quantity"] / denominator
        expenditure_mean = values["weighted_expenditure"] / denominator
        effective_n = denominator**2 / values["sum_weight_squared"]
        quantity_variance = max(
            0,
            values["sum_weighted_quantity_squared"] / denominator - quantity_mean**2,
        )
        expenditure_variance = max(
            0,
            values["sum_weighted_expenditure_squared"] / denominator - expenditure_mean**2,
        )
        quantity_se = math.sqrt(quantity_variance / effective_n)
        expenditure_se = math.sqrt(expenditure_variance / effective_n)
        priors.append(
            {
                "district": district or None,
                "nss_region": nss_region or None,
                "rural_urban_sector": sector,
                "category": category,
                "monthly_quantity_per_capita": quantity_mean,
                "monthly_quantity_per_capita_lower_95": max(0, quantity_mean - 1.96 * quantity_se),
                "monthly_quantity_per_capita_upper_95": quantity_mean + 1.96 * quantity_se,
                "monthly_expenditure_inr_per_capita": expenditure_mean,
                "monthly_expenditure_inr_per_capita_lower_95": max(
                    0, expenditure_mean - 1.96 * expenditure_se
                ),
                "monthly_expenditure_inr_per_capita_upper_95": (
                    expenditure_mean + 1.96 * expenditure_se
                ),
                "quantity_unit": item_spec.get("quantity_unit", "SOURCE_UNIT"),
                "sample_households": sample_households[group],
                "effective_sample_size_approx": effective_n,
                "weighted_persons": denominator,
                "evidence_type": "SAMPLED_PRIOR",
                "interval_method": "NORMAL_APPROX_WEIGHTED_HOUSEHOLD_VARIATION_NOT_DESIGN_SE",
            }
        )
    if zip_archive:
        input_records = [
            {
                "file": input_path.name,
                "size_bytes": input_path.stat().st_size,
                "sha256": file_sha256(input_path),
                "members": [
                    {
                        "name": name,
                        "uncompressed_size_bytes": zip_archive.getinfo(name).file_size,
                        "crc32": f"{zip_archive.getinfo(name).CRC:08x}",
                    }
                    for name in (household_spec["file"], item_spec["file"])
                ],
            },
            {
                "file": mapping_path.name,
                "size_bytes": mapping_path.stat().st_size,
                "sha256": file_sha256(mapping_path),
            },
        ]
        zip_archive.close()
    else:
        household_path = input_path / household_spec["file"]
        item_path = input_path / item_spec["file"]
        input_records = [
            {"file": path.name, "size_bytes": path.stat().st_size, "sha256": file_sha256(path)}
            for path in (household_path, item_path, mapping_path)
        ]
    result = {
        "dataset_id": mapping["dataset_id"],
        "dataset_version": mapping["dataset_version"],
        "official_source_url": mapping["official_source_url"],
        "created_at": datetime.now(UTC).isoformat(),
        "methodology_version": "HCES_WEIGHTED_PRIOR_V2_ZERO_INCLUSIVE",
        "geographic_claim": "Sampled state/district/NSS-region prior; not village observation.",
        "inputs": input_records,
        "west_bengal_households": len(households),
        "priors": priors,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Import official HCES CSV files or CSV ZIP")
    parser.add_argument("input_path", type=Path)
    parser.add_argument("mapping", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(build_hces_priors(args.input_path, args.mapping, args.output), indent=2))


if __name__ == "__main__":
    main()

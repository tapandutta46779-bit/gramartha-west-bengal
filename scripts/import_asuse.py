from __future__ import annotations

import argparse
import csv
import io
import json
import math
import zipfile
from collections import defaultdict
from contextlib import ExitStack
from datetime import UTC, datetime
from pathlib import Path

from scripts.import_hces import _number, file_sha256


def _value(row: dict[str, str], aliases: list[str]) -> str:
    for alias in aliases:
        if alias in row:
            return row[alias].strip()
    raise KeyError(f"none of the columns are present: {aliases}")


def _enterprise_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return (
        _value(row, ["fsu_serial_no", "FSU_Serial_No"]),
        _value(row, ["segment_no", "Segment_No"]),
        _value(
            row,
            ["second_stage_stratum_no", "second_stage_stratum", "Second_Stage_Stratum_No"],
        ),
        _value(row, ["sample_est_no", "sample_estab_no", "Sample_Establishment_No"]),
    )


def _member_name(archive: zipfile.ZipFile, selector: str) -> str:
    matches = [name for name in archive.namelist() if selector in name and name.endswith(".csv")]
    if len(matches) != 1:
        raise ValueError(f"expected one CSV member matching {selector!r}, found {matches}")
    return matches[0]


def _weighted_summary(values: dict[str, float]) -> dict[str, float]:
    weight = values["weight"]
    mean = values["weighted_value"] / weight
    effective_n = weight**2 / values["weight_squared"]
    variance = max(0, values["weighted_value_squared"] / weight - mean**2)
    standard_error = math.sqrt(variance / effective_n)
    return {
        "mean": mean,
        "lower_95": mean - 1.96 * standard_error,
        "upper_95": mean + 1.96 * standard_error,
        "effective_sample_size_approx": effective_n,
        "weighted_enterprises_with_measure": weight,
    }


def build_asuse_priors(input_path: Path, mapping_path: Path, output_path: Path) -> dict:
    mapping = json.loads(mapping_path.read_text())
    members = mapping["members"]
    state_code = str(mapping["state_code"])
    district_names = mapping.get("district_names", {})
    archive = zipfile.ZipFile(input_path) if input_path.is_file() else None
    selected_files: dict[str, str] = {}

    def open_csv(stack: ExitStack, role: str):
        selector = members[role]
        if archive:
            selected_files[role] = _member_name(archive, selector)
            raw = stack.enter_context(archive.open(selected_files[role]))
            return stack.enter_context(
                io.TextIOWrapper(raw, encoding="utf-8-sig", errors="strict", newline="")
            )
        matches = list(input_path.glob(f"**/*{selector}*.csv"))
        if len(matches) != 1:
            raise ValueError(f"expected one CSV file matching {selector!r}, found {matches}")
        selected_files[role] = str(matches[0].relative_to(input_path))
        return stack.enter_context(matches[0].open(newline="", encoding="utf-8-sig"))

    enterprises: dict[tuple[str, str, str, str], dict] = {}
    weight_divisor = float(mapping.get("weight_divisor", 100))
    with ExitStack() as stack:
        for row in csv.DictReader(open_csv(stack, "profile")):
            nss_region = _value(row, ["nss_region", "NSS_Region"])
            if nss_region[:2] != state_code:
                continue
            weight = _number(row, "mlt") / weight_divisor
            if weight <= 0:
                continue
            enterprises[_enterprise_key(row)] = {
                "district": _value(row, ["district", "District"]),
                "nss_region": nss_region,
                "sector": _value(row, ["sector", "Sector"]),
                "nic2": row["major_nic_2dig"].strip(),
                "nic5": row["major_nic_5dig"].strip(),
                "nature_of_operation": row["nature_of_operation"].strip(),
                "months_operated": _number(row, "months_operated"),
                "weight": weight,
                "metrics": {},
            }

    with ExitStack() as stack:
        for row in csv.DictReader(open_csv(stack, "reference_period")):
            enterprise = enterprises.get(_enterprise_key(row))
            if enterprise:
                enterprise["reference_period_type"] = row["ref_period_type"].strip()

    financial_codes = {value: name for name, value in mapping["financial_item_codes"].items()}
    with ExitStack() as stack:
        for row in csv.DictReader(open_csv(stack, "financials")):
            metric = financial_codes.get(row["item_no"].strip())
            if not metric:
                continue
            enterprise = enterprises.get(_enterprise_key(row))
            if enterprise:
                enterprise["metrics"][metric] = _number(row, "value_rs")

    with ExitStack() as stack:
        for row in csv.DictReader(open_csv(stack, "workers")):
            if row["item_no"].strip() != mapping["total_workers_item_code"]:
                continue
            enterprise = enterprises.get(_enterprise_key(row))
            if enterprise:
                enterprise["metrics"]["workers"] = _number(row, "total_workers")

    equipment_codes = set(mapping["equipment_asset_item_codes"])
    total_asset_code = mapping["total_fixed_assets_excluding_land_item_code"]
    land_code = mapping["land_asset_item_code"]
    with ExitStack() as stack:
        for row in csv.DictReader(open_csv(stack, "assets")):
            item_code = row["item_no"].strip()
            enterprise = enterprises.get(_enterprise_key(row))
            if not enterprise:
                continue
            value = _number(row, "mv_assets_owned")
            if item_code in equipment_codes:
                enterprise["metrics"]["equipment_investment_owned"] = (
                    enterprise["metrics"].get("equipment_investment_owned", 0) + value
                )
            elif item_code == total_asset_code:
                enterprise["metrics"]["fixed_assets_excluding_land_owned"] = value
            elif item_code == land_code:
                enterprise["metrics"]["land_owned"] = value

    totals: dict[tuple[str, str, str], dict] = defaultdict(
        lambda: {
            "sample_enterprises": 0,
            "weighted_enterprises": 0.0,
            "metrics": defaultdict(
                lambda: {
                    "observations": 0,
                    "weight": 0.0,
                    "weight_squared": 0.0,
                    "weighted_value": 0.0,
                    "weighted_value_squared": 0.0,
                }
            ),
        }
    )
    incomplete_annualization = 0
    for enterprise in enterprises.values():
        group = (enterprise["district"], enterprise["sector"], enterprise["nic2"])
        group_total = totals[group]
        group_total["sample_enterprises"] += 1
        group_total["weighted_enterprises"] += enterprise["weight"]
        ref_type = enterprise.get("reference_period_type")
        if ref_type == "4":
            annual_factor = 1.0
        elif enterprise["nature_of_operation"] == "1":
            annual_factor = 12.0
        elif enterprise["months_operated"] > 0:
            annual_factor = enterprise["months_operated"]
        else:
            annual_factor = None
            incomplete_annualization += 1
        metrics = dict(enterprise["metrics"])
        for source_name in ("input", "output", "gva"):
            if source_name in metrics and annual_factor is not None:
                metrics[f"annual_{source_name}_inr"] = metrics.pop(source_name) * annual_factor
        if "land_owned" in metrics or "fixed_assets_excluding_land_owned" in metrics:
            metrics["total_fixed_assets_owned"] = metrics.get("land_owned", 0) + metrics.get(
                "fixed_assets_excluding_land_owned", 0
            )
        for name, value in metrics.items():
            metric_total = group_total["metrics"][name]
            weight = enterprise["weight"]
            metric_total["observations"] += 1
            metric_total["weight"] += weight
            metric_total["weight_squared"] += weight**2
            metric_total["weighted_value"] += weight * value
            metric_total["weighted_value_squared"] += weight * value**2

    priors = []
    for (district, sector, nic2), values in sorted(totals.items()):
        summaries = {
            name: _weighted_summary(metric_values)
            for name, metric_values in sorted(values["metrics"].items())
            if metric_values["weight"] > 0
        }
        priors.append(
            {
                "district_code": district,
                "district_name": district_names.get(district),
                "rural_urban_sector": sector,
                "nic_2_digit": nic2,
                "sample_enterprises": values["sample_enterprises"],
                "weighted_enterprises": values["weighted_enterprises"],
                "metric_observations": {
                    name: metric_values["observations"]
                    for name, metric_values in sorted(values["metrics"].items())
                },
                "weighted_metric_summaries": summaries,
                "evidence_type": "SAMPLED_PRIOR",
                "interval_method": "NORMAL_APPROX_WEIGHTED_ENTERPRISE_VARIATION_NOT_DESIGN_SE",
            }
        )

    if archive:
        input_records = [
            {
                "file": input_path.name,
                "size_bytes": input_path.stat().st_size,
                "sha256": file_sha256(input_path),
                "members": [
                    {
                        "role": role,
                        "name": name,
                        "uncompressed_size_bytes": archive.getinfo(name).file_size,
                        "crc32": f"{archive.getinfo(name).CRC:08x}",
                    }
                    for role, name in selected_files.items()
                ],
            }
        ]
        archive.close()
    else:
        input_records = [
            {
                "role": role,
                "file": name,
                "size_bytes": (input_path / name).stat().st_size,
                "sha256": file_sha256(input_path / name),
            }
            for role, name in selected_files.items()
        ]
    input_records.append(
        {
            "file": mapping_path.name,
            "size_bytes": mapping_path.stat().st_size,
            "sha256": file_sha256(mapping_path),
        }
    )
    result = {
        "dataset_id": mapping["dataset_id"],
        "dataset_version": mapping["dataset_version"],
        "official_source_url": mapping["official_source_url"],
        "created_at": datetime.now(UTC).isoformat(),
        "methodology_version": "ASUSE_WEIGHTED_SECTOR_PRIOR_V2_OFFICIAL_ITEMS",
        "weight_rule": f"final_weight = MLT / {weight_divisor:g}",
        "annualization_rule": (
            "m=1 for annual reference type 4; otherwise m=12 for perennial enterprises "
            "and m=months operated for seasonal/casual enterprises"
        ),
        "geographic_claim": (
            "Sampled West Bengal district-code/sector/NIC prior; not an exact locality, "
            "incumbent-capacity, or sales observation."
        ),
        "inputs": input_records,
        "west_bengal_enterprises": len(enterprises),
        "enterprises_missing_annualization_factor": incomplete_annualization,
        "priors": priors,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Import official ASUSE CSV files or CSV ZIP")
    parser.add_argument("input_path", type=Path)
    parser.add_argument("mapping", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(build_asuse_priors(args.input_path, args.mapping, args.output), indent=2))


if __name__ == "__main__":
    main()

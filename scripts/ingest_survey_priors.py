from __future__ import annotations

import json
from datetime import UTC, date, datetime
from pathlib import Path

from backend.evidence.store import EvidenceStore
from backend.models.evidence import (
    ConfidenceLevel,
    DataChangeClass,
    EvidenceRecord,
    EvidenceType,
    FreshnessStatus,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS"
DATABASE = ROOT / "data/sih26091_phase2.sqlite"
AS_OF = date(2026, 8, 28)


def _record(
    *,
    record_id: str,
    variable: str,
    value: float,
    unit: str,
    district: str,
    sector: str,
    source_id: str,
    source_url: str,
    source_dataset: str,
    methodology: str,
    raw_reference: str,
    lower: float | None,
    upper: float | None,
    attributes: dict,
    observation_date: date,
    freshness_status: FreshnessStatus,
) -> EvidenceRecord:
    return EvidenceRecord(
        id=record_id,
        variable=variable,
        value=value,
        unit=unit,
        geography=f"{district}; sector {sector}",
        geo_id=f"REGION:WB:{district}:SECTOR:{sector}",
        source_id=source_id,
        source_url=source_url,
        source_dataset=source_dataset,
        observation_date=observation_date,
        retrieved_at=datetime.now(UTC),
        evidence_type=EvidenceType.SAMPLED,
        confidence=ConfidenceLevel.MEDIUM,
        data_change_class=DataChangeClass.TIME_SENSITIVE_FAST_CHANGING,
        freshness_status=freshness_status,
        freshness_as_of=AS_OF,
        quality_flags=[
            "DISTRICT_SECTOR_SURVEY_PRIOR",
            "NOT_EXACT_LOCALITY_OBSERVATION",
        ],
        methodology_version=methodology,
        raw_reference=raw_reference,
        attributes={"lower": lower, "upper": upper, **attributes},
    )


def ingest_hces(store: EvidenceStore, year: str, production: bool) -> int:
    path = OUTPUT / f"HCES_{year}_West_Bengal_liquid_milk_priors.json"
    payload = json.loads(path.read_text())
    district_names = json.loads((ROOT / "config/asuse_2025_mapping.json").read_text())[
        "district_names"
    ]
    count = 0
    suffix = "" if production else f"_{year}"
    for prior in payload["priors"]:
        district = district_names[prior["district"]]
        sector = prior["rural_urban_sector"]
        values = [
            (
                f"monthly_liquid_milk_litres_per_capita_prior{suffix}",
                prior["monthly_quantity_per_capita"],
                "litres/person/month",
                prior["monthly_quantity_per_capita_lower_95"],
                prior["monthly_quantity_per_capita_upper_95"],
            ),
            (
                f"monthly_liquid_milk_expenditure_inr_per_capita_prior{suffix}",
                prior["monthly_expenditure_inr_per_capita"],
                "INR/person/month",
                prior["monthly_expenditure_inr_per_capita_lower_95"],
                prior["monthly_expenditure_inr_per_capita_upper_95"],
            ),
        ]
        for variable, value, unit, lower, upper in values:
            record = _record(
                record_id=f"HCES:{year}:{prior['district']}:{sector}:{variable}",
                variable=variable,
                value=value,
                unit=unit,
                district=district,
                sector=sector,
                source_id=f"HCES-{year}",
                source_url=payload["official_source_url"],
                source_dataset=payload["dataset_version"],
                methodology=payload["methodology_version"],
                raw_reference=str(path.relative_to(ROOT)),
                lower=lower,
                upper=upper,
                attributes={
                    "sample_households": prior["sample_households"],
                    "effective_sample_size_approx": prior["effective_sample_size_approx"],
                    "observation_period": year.replace("_", "-"),
                    "interval_method": prior["interval_method"],
                },
                observation_date=(
                    date(2024, 7, 31) if year == "2023_24" else date(2023, 7, 31)
                ),
                freshness_status=(
                    FreshnessStatus.RECENT
                    if year == "2023_24"
                    else FreshnessStatus.STALE_FOR_DECISION
                ),
            )
            store.put_regional_prior(record, district=district, sector=sector)
            count += 1
    return count


def ingest_asuse(store: EvidenceStore) -> int:
    path = OUTPUT / "ASUSE_2025_West_Bengal_enterprise_priors.json"
    payload = json.loads(path.read_text())
    count = 0
    metric_units = {
        "annual_gva_inr": "INR/enterprise/year",
        "annual_input_inr": "INR/enterprise/year",
        "annual_output_inr": "INR/enterprise/year",
        "workers": "workers/enterprise",
        "equipment_investment_owned": "INR/enterprise",
        "total_fixed_assets_owned": "INR/enterprise",
    }
    for prior in payload["priors"]:
        if prior["nic_2_digit"] not in {"10", "46", "47"}:
            continue
        district = prior["district_name"]
        sector = prior["rural_urban_sector"]
        for metric, unit in metric_units.items():
            summary = prior["weighted_metric_summaries"].get(metric)
            if not summary:
                continue
            variable = f"asuse_nic{prior['nic_2_digit']}_{metric}_prior"
            record = _record(
                record_id=(
                    f"ASUSE:2025:{prior['district_code']}:{sector}:"
                    f"NIC{prior['nic_2_digit']}:{metric}"
                ),
                variable=variable,
                value=summary["mean"],
                unit=unit,
                district=district,
                sector=sector,
                source_id="ASUSE-2025",
                source_url=payload["official_source_url"],
                source_dataset=payload["dataset_version"],
                methodology=payload["methodology_version"],
                raw_reference=str(path.relative_to(ROOT)),
                lower=summary["lower_95"],
                upper=summary["upper_95"],
                attributes={
                    "nic_2_digit": prior["nic_2_digit"],
                    "sample_enterprises": prior["sample_enterprises"],
                    "metric_observations": prior["metric_observations"].get(metric),
                    "effective_sample_size_approx": summary["effective_sample_size_approx"],
                    "observation_period": "2025-01-01/2025-12-31",
                    "interval_method": prior["interval_method"],
                    "not_incumbent_capacity": True,
                },
                observation_date=date(2025, 12, 31),
                freshness_status=FreshnessStatus.RECENT,
            )
            store.put_regional_prior(record, district=district, sector=sector)
            count += 1
    return count


def main() -> None:
    store = EvidenceStore(DATABASE)
    with store.transaction():
        store.connection.execute("DELETE FROM regional_prior")
        hces_2022 = ingest_hces(store, "2022_23", production=False)
        hces_2023 = ingest_hces(store, "2023_24", production=True)
        asuse_2025 = ingest_asuse(store)
    print(
        json.dumps(
            {
                "hces_2022_23_records": hces_2022,
                "hces_2023_24_records": hces_2023,
                "asuse_2025_records": asuse_2025,
                "database": str(DATABASE.relative_to(ROOT)),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

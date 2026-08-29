from __future__ import annotations

import json
from datetime import UTC, date, datetime
from pathlib import Path

from backend.evidence.districts import canonical_district
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
                observation_date=(date(2024, 7, 31) if year == "2023_24" else date(2023, 7, 31)),
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


def _district_population_anchors(store: EvidenceStore) -> dict[str, float]:
    rows = store.connection.execute(
        """
        SELECT c.current_district AS district,
               SUM(CAST(json_extract(e.payload, '$.value') AS REAL)) AS population
        FROM current_geo_entity c
        JOIN evidence_record e ON e.geo_id = c.source_geo_id
        WHERE c.payload IS NOT NULL AND e.variable = 'population_observed_2011'
        GROUP BY c.current_district
        """
    ).fetchall()
    return {row["district"]: float(row["population"]) for row in rows if row["population"]}


def ingest_wb_milk_production(store: EvidenceStore) -> int:
    path = ROOT / "config/wb_milk_production_2024_25.json"
    payload = json.loads(path.read_text())
    population_anchors = _district_population_anchors(store)
    count = 0
    for current_name, production in payload["districts"].items():
        district = canonical_district(current_name)
        if district is None:
            continue
        for sector in ("1", "2"):
            record = EvidenceRecord(
                id=f"WBARD:MILK:2024-25:{current_name}:{sector}",
                variable="district_annual_milk_production_kg",
                value=production,
                unit="kg/year",
                geography=f"{current_name}; sector {sector}",
                geo_id=f"REGION:WB:{current_name}:SECTOR:{sector}",
                source_id="WB-ARD-MILK-2024-25",
                source_url=payload["source_url"],
                source_dataset=payload["dataset"],
                observation_date=date(2025, 3, 31),
                retrieved_at=datetime.now(UTC),
                evidence_type=EvidenceType.ESTIMATED,
                confidence=ConfidenceLevel.MEDIUM,
                data_change_class=DataChangeClass.TIME_SENSITIVE_FAST_CHANGING,
                freshness_status=FreshnessStatus.RECENT,
                freshness_as_of=AS_OF,
                quality_flags=[
                    "OFFICIAL_DISTRICT_ANNUAL_PRODUCTION_ESTIMATE",
                    "NOT_LOCALITY_REACHABLE_SUPPLY",
                    "MARKETED_SURPLUS_AND_ACCESSIBILITY_MUST_BE_MODELLED",
                ],
                methodology_version="wb-ard-district-production-direct-v1",
                raw_reference=payload["raw_file"],
                attributes={
                    "observation_period": payload["observation_period"],
                    "raw_sha256": payload["raw_sha256"],
                    "raw_size_bytes": payload["raw_size_bytes"],
                    "district_population_observed_2011": population_anchors.get(current_name),
                    "state_population_observed_2011": payload["state_population_observed_2011"],
                    "state_total_kg": payload["state_total_kg"],
                    "population_anchor_method": (
                        "sum of exact linked current-product localities"
                        if current_name in population_anchors
                        else (
                            "state per-capita fallback because current-district "
                            "crosswalk is incomplete"
                        )
                    ),
                },
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
        milk_2024 = ingest_wb_milk_production(store)
    print(
        json.dumps(
            {
                "hces_2022_23_records": hces_2022,
                "hces_2023_24_records": hces_2023,
                "asuse_2025_records": asuse_2025,
                "wb_ard_milk_2024_25_records": milk_2024,
                "database": str(DATABASE.relative_to(ROOT)),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

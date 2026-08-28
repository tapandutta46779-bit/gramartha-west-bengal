from __future__ import annotations

from datetime import date

from backend.models.evidence import (
    DataChangeClass,
    EvidenceRecord,
    FreshnessStatus,
)

STRUCTURAL_PREFIXES = ("population_", "households_", "road_", "geography_")
TIME_SENSITIVE_PREFIXES = (
    "livestock_",
    "milk_price_",
    "fuel_price_",
    "transport_cost_",
    "incumbent_capacity_",
    "venture_",
    "wage_",
    "rent_",
    "monthly_liquid_milk_",
    "asuse_",
)


def classify_record(record: EvidenceRecord, *, as_of: date) -> EvidenceRecord:
    variable = record.variable.casefold()
    if variable.startswith(STRUCTURAL_PREFIXES):
        if "projected" in variable:
            status = FreshnessStatus.PROJECTED
        elif "current" in variable:
            status = _time_sensitive_status(record, as_of)
        else:
            status = FreshnessStatus.HISTORICAL_BASELINE
        return record.model_copy(
            update={
                "data_change_class": DataChangeClass.STRUCTURAL_SLOW_CHANGING,
                "freshness_status": status,
                "freshness_as_of": as_of,
            }
        )
    if variable.startswith(TIME_SENSITIVE_PREFIXES):
        status = _time_sensitive_status(record, as_of)
        return record.model_copy(
            update={
                "data_change_class": DataChangeClass.TIME_SENSITIVE_FAST_CHANGING,
                "freshness_status": status,
                "freshness_as_of": as_of,
            }
        )
    return record.model_copy(update={"freshness_as_of": as_of})


def _time_sensitive_status(record: EvidenceRecord, as_of: date) -> FreshnessStatus:
    observation = record.observation_date
    if observation is None:
        year = record.attributes.get("census_reference_year")
        if isinstance(year, int) and as_of.year - year >= 3:
            return FreshnessStatus.STALE_FOR_DECISION
        return FreshnessStatus.UNKNOWN
    age_days = (as_of - observation).days
    if age_days <= 120:
        return FreshnessStatus.CURRENT
    if record.variable.startswith(("monthly_liquid_milk_", "asuse_")) and age_days <= 1095:
        return FreshnessStatus.RECENT
    if age_days <= 730:
        return FreshnessStatus.RECENT
    return FreshnessStatus.STALE_FOR_DECISION

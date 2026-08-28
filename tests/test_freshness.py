from datetime import UTC, date, datetime

from backend.evidence.freshness import classify_record
from backend.models.evidence import (
    ConfidenceLevel,
    DataChangeClass,
    EvidenceRecord,
    EvidenceType,
    FreshnessStatus,
)


def evidence(variable: str, observed: date | None) -> EvidenceRecord:
    return EvidenceRecord(
        id=variable,
        variable=variable,
        value=1,
        unit="unit",
        geography="test",
        geo_id="WB:test",
        source_id="test",
        source_url="https://example.invalid",
        source_dataset="test",
        observation_date=observed,
        retrieved_at=datetime.now(UTC),
        evidence_type=EvidenceType.OBSERVED,
        confidence=ConfidenceLevel.HIGH,
        methodology_version="test",
    )


def test_freshness_preserves_structural_year_and_projection_status() -> None:
    as_of = date(2026, 8, 28)
    old = classify_record(evidence("population_observed_2011", date(2011, 3, 1)), as_of=as_of)
    assert old.data_change_class == DataChangeClass.STRUCTURAL_SLOW_CHANGING
    assert old.freshness_status == FreshnessStatus.HISTORICAL_BASELINE

    projected = classify_record(evidence("population_projected_2026", None), as_of=as_of)
    assert projected.freshness_status == FreshnessStatus.PROJECTED


def test_time_sensitive_age_thresholds_are_explicit() -> None:
    as_of = date(2026, 8, 28)
    current = classify_record(evidence("milk_price_inr_per_litre", date(2026, 8, 1)), as_of=as_of)
    recent = classify_record(
        evidence("monthly_liquid_milk_litres_per_capita_prior", date(2024, 7, 31)),
        as_of=as_of,
    )
    stale = classify_record(evidence("livestock_cattle", date(2019, 1, 1)), as_of=as_of)
    assert current.freshness_status == FreshnessStatus.CURRENT
    assert recent.freshness_status == FreshnessStatus.RECENT
    assert stale.freshness_status == FreshnessStatus.STALE_FOR_DECISION

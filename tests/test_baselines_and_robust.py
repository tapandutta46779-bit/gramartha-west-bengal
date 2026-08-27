from datetime import UTC, datetime

from backend.engine.robust import select_minimum_regret
from backend.learning.baselines import evidence_weighted_interval
from backend.models.evidence import ConfidenceLevel, EvidenceRecord, EvidenceType


def record(record_id: str, value: float, evidence_type: EvidenceType) -> EvidenceRecord:
    return EvidenceRecord(
        id=record_id,
        variable="monthly_demand",
        value=value,
        unit="units/month",
        geography="Controlled",
        geo_id="SYNTHETIC:test",
        source_id="controlled",
        source_url="https://example.invalid",
        source_dataset="controlled",
        retrieved_at=datetime.now(UTC),
        evidence_type=evidence_type,
        confidence=ConfidenceLevel.HIGH,
        methodology_version="test",
    )


def test_baseline_excludes_synthetic_and_returns_evidence_envelope():
    interval = evidence_weighted_interval(
        [
            record("one", 10, EvidenceType.OBSERVED),
            record("two", 20, EvidenceType.OBSERVED),
            record("synthetic", 999, EvidenceType.SYNTHETIC),
        ],
        variable="monthly_demand",
        unit="units/month",
    )
    assert interval.central == 15
    assert interval.lower == 10
    assert interval.upper == 20
    assert interval.evidence_ids == ["one", "two"]


def test_baseline_refuses_synthetic_only_input():
    interval = evidence_weighted_interval(
        [record("synthetic", 999, EvidenceType.SYNTHETIC)],
        variable="monthly_demand",
        unit="units/month",
    )
    assert interval.status == "INSUFFICIENT_EVIDENCE"


def test_exact_minimax_regret_selection():
    result = select_minimum_regret(
        {
            "low": {"small": 8, "large": 3},
            "base": {"small": 8, "large": 10},
            "high": {"small": 8, "large": 14},
        }
    )
    assert result.selected_candidate_id == "large"
    assert result.maximum_regret == 5

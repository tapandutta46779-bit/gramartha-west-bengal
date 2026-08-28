from datetime import UTC, date, datetime

from backend.models.evidence import (
    ConfidenceLevel,
    EvidenceRecord,
    EvidenceType,
    FreshnessStatus,
)
from backend.models.profile import EntrepreneurProfile
from backend.pipeline.automatic import build_automatic_inputs


def record(variable: str, value: float, freshness: FreshnessStatus) -> EvidenceRecord:
    return EvidenceRecord(
        id=variable,
        variable=variable,
        value=value,
        unit="test",
        geography="Test",
        geo_id="WB:test",
        source_id="test",
        source_url="https://example.invalid",
        source_dataset="controlled",
        observation_date=date(2026, 8, 1),
        retrieved_at=datetime.now(UTC),
        evidence_type=EvidenceType.OBSERVED,
        confidence=ConfidenceLevel.HIGH,
        freshness_status=freshness,
        methodology_version="test",
    )


def inputs(dynamic_status: FreshnessStatus) -> list[EvidenceRecord]:
    return [
        record("monthly_dairy_demand_litres", 100, FreshnessStatus.CURRENT),
        record("reachable_milk_supply_litres_month", 100, dynamic_status),
        record("milk_price_inr_per_litre", 60, dynamic_status),
        record("incumbent_capacity_litres_month", 20, dynamic_status),
        record("transport_cost_inr_per_litre", 2, dynamic_status),
        record("venture_transport_capex_inr", 1000, dynamic_status),
        record("venture_transport_opex_inr_month", 100, dynamic_status),
        record("venture_transport_capacity_litres_month", 30, dynamic_status),
        record("venture_working_capital_inr", 500, dynamic_status),
    ]


def test_stale_dynamic_values_cannot_unlock_graph_or_venture() -> None:
    profile = EntrepreneurProfile(
        geo_id="WB:test", available_capital=10_000, business_category="dairy"
    )
    stale = build_automatic_inputs(
        geo_id="WB:test", sector="dairy", evidence=inputs(FreshnessStatus.STALE_FOR_DECISION),
        profile=profile,
    )
    assert stale.graph is None
    assert not stale.candidates

    current = build_automatic_inputs(
        geo_id="WB:test", sector="dairy", evidence=inputs(FreshnessStatus.CURRENT),
        profile=profile,
    )
    assert current.graph is not None
    assert current.candidates

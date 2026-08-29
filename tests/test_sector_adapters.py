from datetime import UTC, datetime

import pytest

from backend.models.evidence import ConfidenceLevel, EvidenceRecord, EvidenceType, FreshnessStatus
from backend.models.profile import EntrepreneurProfile
from backend.pipeline.automatic import build_automatic_inputs


def prior(variable: str, value: float) -> EvidenceRecord:
    return EvidenceRecord(
        id=f"test:{variable}",
        variable=variable,
        value=value,
        unit="INR",
        geography="Test district",
        geo_id="test-geo",
        source_id="ASUSE",
        source_url="https://microdata.gov.in/",
        source_dataset="ASUSE 2023-24",
        retrieved_at=datetime.now(UTC),
        evidence_type=EvidenceType.SAMPLED,
        confidence=ConfidenceLevel.MEDIUM,
        freshness_status=FreshnessStatus.RECENT,
        methodology_version="weighted-prior-test-v1",
    )


@pytest.mark.parametrize(
    ("sector", "nic"),
    [
        ("kirana", "47"),
        ("poultry", "46"),
        ("fishery", "46"),
        ("food processing", "10"),
        ("transport", "46"),
        ("flour mill", "10"),
        ("spice processing", "10"),
        ("mustard oil", "10"),
        ("electronics", "47"),
        ("household goods", "46"),
    ],
)
def test_sector_adapter_builds_traceable_candidate_and_graph(sector: str, nic: str):
    prefix = f"asuse_nic{nic}_"
    evidence = [
        prior(f"{prefix}annual_output_inr_prior", 360_000),
        prior(f"{prefix}annual_input_inr_prior", 240_000),
        prior(f"{prefix}total_fixed_assets_owned_prior", 220_000),
        prior(f"{prefix}workers_prior", 2),
    ]
    result = build_automatic_inputs(
        geo_id="test-geo",
        sector=sector,
        evidence=evidence,
        profile=EntrepreneurProfile(
            geo_id="test-geo", available_capital=100_000, business_category=sector
        ),
    )
    assert result.graph is not None
    assert len(result.candidates) == 5
    assert result.demand.status == "MODELLED_BENCHMARK"
    assert result.demand.lower < result.demand.central < result.demand.upper
    assert min(candidate.investment for candidate in result.candidates) <= 100_000
    investments = [candidate.investment for candidate in result.candidates]
    assert investments == sorted(investments)
    assert len(set(investments)) == 5
    assert result.gates[0].blocking is False

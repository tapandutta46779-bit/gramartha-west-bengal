from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class EvidenceType(StrEnum):
    OBSERVED = "OBSERVED"
    SAMPLED = "SAMPLED"
    ESTIMATED = "ESTIMATED"
    INFERRED = "INFERRED"
    MODELLED = "MODELLED"
    SYNTHETIC = "SYNTHETIC"


class ConfidenceLevel(StrEnum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INSUFFICIENT = "INSUFFICIENT"


class EvidenceSource(BaseModel):
    source_id: str
    name: str
    dataset: str
    url: HttpUrl | str
    version: str
    retrieved_at: datetime
    checksum_sha256: str | None = None
    geographic_coverage: str
    license_or_terms: str | None = None


class EvidenceRecord(BaseModel):
    id: str
    variable: str
    value: float | int | str | bool | None
    unit: str
    geography: str
    geo_id: str
    source_id: str
    source_url: HttpUrl | str
    source_dataset: str
    observation_date: date | None = None
    retrieved_at: datetime
    evidence_type: EvidenceType
    confidence: ConfidenceLevel
    quality_flags: list[str] = Field(default_factory=list)
    methodology_version: str
    raw_reference: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)


class EstimateInterval(BaseModel):
    central: float | None
    lower: float | None
    upper: float | None
    unit: str
    confidence: ConfidenceLevel
    evidence_ids: list[str] = Field(default_factory=list)
    method_version: str
    status: str = "ESTIMATED"
    notes: list[str] = Field(default_factory=list)

    @classmethod
    def insufficient(cls, unit: str, method_version: str, note: str) -> EstimateInterval:
        return cls(
            central=None,
            lower=None,
            upper=None,
            unit=unit,
            confidence=ConfidenceLevel.INSUFFICIENT,
            method_version=method_version,
            status="INSUFFICIENT_EVIDENCE",
            notes=[note],
        )

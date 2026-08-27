from __future__ import annotations

from backend.models.evidence import (
    ConfidenceLevel,
    EstimateInterval,
    EvidenceRecord,
    EvidenceType,
)

TYPE_WEIGHT = {
    EvidenceType.OBSERVED: 1.0,
    EvidenceType.SAMPLED: 0.8,
    EvidenceType.ESTIMATED: 0.6,
    EvidenceType.INFERRED: 0.45,
    EvidenceType.MODELLED: 0.5,
    EvidenceType.SYNTHETIC: 0.0,
}
CONFIDENCE_WEIGHT = {
    ConfidenceLevel.HIGH: 1.0,
    ConfidenceLevel.MEDIUM: 0.7,
    ConfidenceLevel.LOW: 0.4,
    ConfidenceLevel.INSUFFICIENT: 0.0,
}


def evidence_weighted_interval(
    records: list[EvidenceRecord],
    *,
    variable: str,
    unit: str,
    method_version: str = "evidence-weighted-baseline-v1",
) -> EstimateInterval:
    eligible = [
        item
        for item in records
        if item.variable == variable
        and item.unit == unit
        and isinstance(item.value, (int, float))
        and not isinstance(item.value, bool)
        and TYPE_WEIGHT[item.evidence_type] > 0
        and CONFIDENCE_WEIGHT[item.confidence] > 0
    ]
    if not eligible:
        return EstimateInterval.insufficient(
            unit, method_version, f"No non-synthetic numeric evidence for {variable}."
        )
    weighted = [
        (
            float(item.value),
            TYPE_WEIGHT[item.evidence_type] * CONFIDENCE_WEIGHT[item.confidence],
        )
        for item in eligible
    ]
    central = sum(value * weight for value, weight in weighted) / sum(
        weight for _, weight in weighted
    )
    values = [value for value, _ in weighted]
    confidence = ConfidenceLevel.HIGH if len(eligible) >= 3 else ConfidenceLevel.MEDIUM
    return EstimateInterval(
        central=central,
        lower=min(values),
        upper=max(values),
        unit=unit,
        confidence=confidence,
        evidence_ids=[item.id for item in eligible],
        method_version=method_version,
        notes=[
            "Range is the observed evidence envelope, not a statistical confidence interval.",
            "Synthetic records are excluded from the estimate.",
        ],
    )

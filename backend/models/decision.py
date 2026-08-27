from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from .evidence import ConfidenceLevel, EvidenceRecord
from .finance import DigitalTwinResult, LoanTerms, StressResult
from .flow import Bottleneck, FlowResult
from .geography import GeographicIdentity
from .profile import EntrepreneurProfile
from .venture import CounterfactualResult, MVVResult, VentureCandidate


class DecisionStatus(StrEnum):
    RECOMMENDED = "RECOMMENDED"
    CONDITIONAL = "CONDITIONAL"
    NOT_FEASIBLE = "NOT_FEASIBLE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class DecisionExplanation(BaseModel):
    language: str = "en"
    summary: str
    evidence_statement: str
    caveats: list[str] = Field(default_factory=list)


class VentureDecision(BaseModel):
    analysis_id: str
    created_at: datetime
    status: DecisionStatus
    methodology_version: str
    geography: GeographicIdentity | None = None
    entrepreneur: EntrepreneurProfile | None = None
    confidence: ConfidenceLevel
    evidence: list[EvidenceRecord] = Field(default_factory=list)
    evidence_gaps: list[str] = Field(default_factory=list)
    baseline_flow: FlowResult | None = None
    bottlenecks: list[Bottleneck] = Field(default_factory=list)
    selected_venture: VentureCandidate | None = None
    counterfactual: CounterfactualResult | None = None
    mvv: MVVResult | None = None
    loan_terms: LoanTerms | None = None
    digital_twin: DigitalTwinResult | None = None
    stress: StressResult | None = None
    alternatives: list[VentureCandidate] = Field(default_factory=list)
    staged_plan: list[str] = Field(default_factory=list)
    explanation: DecisionExplanation
    calculation_trace: dict = Field(default_factory=dict)

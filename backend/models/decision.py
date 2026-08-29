from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from .economic_graph import EconomicGraph
from .evidence import ConfidenceLevel, EstimateInterval, EvidenceRecord
from .finance import DigitalTwinResult, LoanTerms, SchemeEligibility, StressResult
from .flow import Bottleneck, FlowResult
from .geography import GeographicIdentity, GeographicResolution
from .profile import EntrepreneurProfile
from .venture import CounterfactualResult, MVVResult, VentureCandidate


class DecisionStatus(StrEnum):
    RECOMMENDED = "RECOMMENDED"
    CONDITIONAL = "CONDITIONAL"
    NOT_FEASIBLE = "NOT_FEASIBLE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class EvidenceGapCode(StrEnum):
    NO_DEMAND_EVIDENCE = "NO_DEMAND_EVIDENCE"
    NO_SUPPLY_EVIDENCE = "NO_SUPPLY_EVIDENCE"
    NO_PRICE_EVIDENCE = "NO_PRICE_EVIDENCE"
    NO_CAPACITY_EVIDENCE = "NO_CAPACITY_EVIDENCE"
    NO_ROUTE_COST_EVIDENCE = "NO_ROUTE_COST_EVIDENCE"
    NO_VENTURE_COST_EVIDENCE = "NO_VENTURE_COST_EVIDENCE"
    NO_CURRENT_FINANCE_RULE = "NO_CURRENT_FINANCE_RULE"
    AMBIGUOUS_LOCATION = "AMBIGUOUS_LOCATION"
    LOCATION_NOT_FOUND = "LOCATION_NOT_FOUND"
    LOW_GEO_CONFIDENCE = "LOW_GEO_CONFIDENCE"
    UNSUPPORTED_SECTOR = "UNSUPPORTED_SECTOR"
    INSUFFICIENT_TRAINING_DATA = "INSUFFICIENT_TRAINING_DATA"


class EvidenceGate(BaseModel):
    code: EvidenceGapCode
    message: str
    blocking: bool = True
    required_variables: list[str] = Field(default_factory=list)


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
    geo_resolution: GeographicResolution | None = None
    entrepreneur: EntrepreneurProfile | None = None
    sector: str | None = None
    confidence: ConfidenceLevel
    evidence: list[EvidenceRecord] = Field(default_factory=list)
    evidence_gaps: list[str] = Field(default_factory=list)
    evidence_gates: list[EvidenceGate] = Field(default_factory=list)
    data_quality: dict[str, Any] = Field(default_factory=dict)
    demand: EstimateInterval | None = None
    supply: EstimateInterval | None = None
    price: EstimateInterval | None = None
    competition: dict[str, Any] = Field(default_factory=dict)
    sector_intelligence: dict[str, Any] = Field(default_factory=dict)
    entry_difficulty: dict[str, Any] = Field(default_factory=dict)
    premortem: list[dict[str, Any]] = Field(default_factory=list)
    action_plan: dict[str, list[str]] = Field(default_factory=dict)
    catchment: dict[str, Any] = Field(default_factory=dict)
    generated_graph: EconomicGraph | None = None
    economic_graph_summary: dict[str, Any] = Field(default_factory=dict)
    baseline_flow: FlowResult | None = None
    bottlenecks: list[Bottleneck] = Field(default_factory=list)
    selected_venture: VentureCandidate | None = None
    counterfactual: CounterfactualResult | None = None
    mvv: MVVResult | None = None
    constraint_analysis: dict[str, Any] = Field(default_factory=dict)
    loan_terms: LoanTerms | None = None
    official_finance: list[SchemeEligibility] = Field(default_factory=list)
    prudent_financing: dict[str, Any] = Field(default_factory=dict)
    digital_twin: DigitalTwinResult | None = None
    operating_break_even: int | None = None
    investment_payback: int | None = None
    stress: StressResult | None = None
    failure_boundaries: list[Any] = Field(default_factory=list)
    sensitivity_analysis: list[dict[str, Any]] = Field(default_factory=list)
    robust_comparison: dict[str, Any] = Field(default_factory=dict)
    alternatives: list[VentureCandidate] = Field(default_factory=list)
    candidate_ventures: list[VentureCandidate] = Field(default_factory=list)
    staged_plan: list[str] = Field(default_factory=list)
    swot: dict[str, list[str]] = Field(default_factory=dict)
    explanation: DecisionExplanation
    calculation_trace: dict = Field(default_factory=dict)
    limitations: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    model_versions: dict[str, str] = Field(default_factory=dict)
    data_versions: dict[str, str] = Field(default_factory=dict)
    software_git_commit: str | None = None

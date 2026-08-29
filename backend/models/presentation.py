from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class ConclusionStatus(StrEnum):
    PROMISING_VERIFY_START_SMALL = "PROMISING_VERIFY_START_SMALL"
    WORTH_TESTING_NOT_PROVEN = "WORTH_TESTING_NOT_PROVEN"
    CAUTION_WEAK_OR_UNCERTAIN = "CAUTION_WEAK_OR_UNCERTAIN"
    NOT_ATTRACTIVE_UNDER_CURRENT_CONDITIONS = "NOT_ATTRACTIVE_UNDER_CURRENT_CONDITIONS"
    MORE_INFORMATION_IS_NEEDED_FIRST = "MORE_INFORMATION_IS_NEEDED_FIRST"


class SummaryRange(BaseModel):
    lower: float | None = None
    central: float | None = None
    upper: float | None = None
    unit: str
    status: str


class CompetitionSummary(BaseModel):
    direct_count: int | None = None
    indirect_count: int | None = None
    intensity: str = "UNKNOWN"
    radius_km: float | None = None
    coordinate_quality: str | None = None
    nearest_direct_name: str | None = None
    nearest_indirect_name: str | None = None
    caveat: str


class PlainLanguagePresentation(BaseModel):
    language: str
    recommended_venture_name: str
    recommended_venture_category: str
    why_recommended: str
    why_here: str
    who_suits: str
    who_should_avoid: str
    top_advantages: list[str] = Field(default_factory=list)
    top_disadvantages: list[str] = Field(default_factory=list)
    top_risks: list[str] = Field(default_factory=list)
    top_actions: list[str] = Field(default_factory=list)
    data_confidence: str
    conclusion_text: str
    labels: dict[str, str] = Field(default_factory=dict)


class DetailedLanguagePresentation(BaseModel):
    language: str
    labels: dict[str, str] = Field(default_factory=dict)
    translations: dict[str, str] = Field(default_factory=dict)


class PlainLanguageSummary(BaseModel):
    analysis_id: str
    conclusion_status: ConclusionStatus
    recommended_venture_name: str
    recommended_venture_category: str
    why_recommended: str
    why_here: str
    who_suits: str
    who_should_avoid: str
    capital_required: SummaryRange
    own_money_used: SummaryRange
    money_kept_as_reserve: SummaryRange
    finance_needed: SummaryRange
    monthly_revenue: SummaryRange
    monthly_operating_cash: SummaryRange
    break_even_month: int | None = None
    payback_month: int | None = None
    demand_opportunity: SummaryRange
    price_guidance: SummaryRange
    competition_summary: CompetitionSummary
    top_advantages: list[str] = Field(default_factory=list)
    top_disadvantages: list[str] = Field(default_factory=list)
    top_risks: list[str] = Field(default_factory=list)
    top_actions: list[str] = Field(default_factory=list)
    data_confidence: str
    conclusion_text: str
    presentations: dict[str, PlainLanguagePresentation]
    detailed_presentations: dict[str, DetailedLanguagePresentation] = Field(default_factory=dict)
    method_version: str = "plain-language-summary-v2-full-detail"

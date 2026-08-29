from datetime import UTC, datetime
from io import BytesIO

from pypdf import PdfReader

from backend.models.decision import DecisionExplanation, DecisionStatus, VentureDecision
from backend.models.evidence import ConfidenceLevel, EstimateInterval
from backend.models.finance import DigitalTwinResult, MonthProjection
from backend.models.geography import GeographicIdentity
from backend.models.venture import PrimitiveType, VentureCandidate, VenturePrimitive
from backend.presentation import build_plain_language_summary
from backend.reporting.customer_pdf import build_customer_pdf


def decision_fixture() -> VentureDecision:
    primitive = VenturePrimitive(
        primitive_id="dairy:test",
        primitive_type=PrimitiveType.AGGREGATION,
        sector_compatibility=["dairy"],
        capex=60_000,
        working_capital=20_000,
        monthly_opex=10_000,
        capacity=1_000,
        staff=2,
    )
    venture = VentureCandidate(
        candidate_id="dairy:test:v1",
        primitives=[primitive],
        investment=80_000,
        monthly_opex=10_000,
        total_capacity=1_000,
    )
    months = [
        MonthProjection(
            month=month,
            demand=900,
            sales_volume=850,
            revenue=60_000,
            variable_cost=40_000,
            fixed_cost=10_000,
            debt_payment=0,
            operating_cash_flow=10_000,
            closing_cash=20_000 + month * 10_000,
            debt_service_coverage_ratio=None,
        )
        for month in range(1, 37)
    ]
    return VentureDecision(
        analysis_id="stable-analysis-id",
        created_at=datetime.now(UTC),
        status=DecisionStatus.CONDITIONAL,
        methodology_version="decision-test",
        geography=GeographicIdentity(
            geo_id="WB:TEST",
            state="West Bengal",
            district="Nadia",
            locality="Controlled Locality",
            locality_type="VILLAGE",
        ),
        sector="dairy",
        confidence=ConfidenceLevel.MEDIUM,
        demand=EstimateInterval(
            central=1_200,
            lower=1_000,
            upper=1_400,
            unit="litres/month",
            confidence=ConfidenceLevel.MEDIUM,
            method_version="test",
        ),
        supply=EstimateInterval(
            central=700,
            lower=600,
            upper=800,
            unit="litres/month",
            confidence=ConfidenceLevel.MEDIUM,
            method_version="test",
        ),
        price=EstimateInterval(
            central=50,
            lower=45,
            upper=55,
            unit="INR/litre",
            confidence=ConfidenceLevel.MEDIUM,
            method_version="test",
        ),
        competition={
            "direct_count": 2,
            "indirect_count": 3,
            "competition_intensity": "MODERATE_PROXY_DENSITY",
            "caveat": "OSM counts do not measure capacity, sales or market share.",
        },
        catchment={"radius_km": 10},
        selected_venture=venture,
        prudent_financing={
            "own_capital_deployed": 80_000,
            "capital_preserved_as_reserve": 20_000,
            "illustrative_financing_requirement": 0,
        },
        digital_twin=DigitalTwinResult(
            months=months,
            minimum_cash=30_000,
            cumulative_cash_flow=360_000,
            operating_break_even_month=1,
            cash_break_even_month=1,
            investment_payback_month=8,
            initial_cash_position=20_000,
            owner_capital_at_risk=80_000,
            default_month=None,
        ),
        operating_break_even=1,
        investment_payback=8,
        robust_comparison={
            "candidate_summaries": [
                {
                    "candidate_id": "dairy:test:v1",
                    "scenario_survival_rate": 0.9,
                }
            ]
        },
        explanation=DecisionExplanation(
            summary="test",
            evidence_statement="test",
        ),
    )


def test_plain_language_summary_is_one_numeric_contract_with_three_text_views():
    summary = build_plain_language_summary(decision_fixture())
    assert summary.analysis_id == "stable-analysis-id"
    assert set(summary.presentations) == {"en", "bn", "hi"}
    assert summary.capital_required.central == 80_000
    assert summary.monthly_revenue.central == 60_000
    assert summary.monthly_operating_cash.central == 10_000
    assert (
        summary.presentations["en"].recommended_venture_name
        != summary.presentations["bn"].recommended_venture_name
    )
    assert "ছোট" in summary.presentations["bn"].recommended_venture_name
    assert "छोटी" in summary.presentations["hi"].recommended_venture_name
    assert summary.method_version == "plain-language-summary-v1"


def test_multilingual_pdfs_preserve_page_count_and_analysis_id():
    decision = decision_fixture()
    decision.plain_language_summary = build_plain_language_summary(decision)
    results = {}
    for language in ("en", "bn", "hi"):
        payload = build_customer_pdf(decision, language)
        reader = PdfReader(BytesIO(payload))
        assert len(reader.pages) >= 2
        assert reader.metadata.title.endswith(f"- {language}")
        results[language] = len(reader.pages)
    assert len(set(results.values())) == 1

# ruff: noqa: E501 - dense multilingual report rows are easier to review intact.
from __future__ import annotations

from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from fpdf import FPDF
from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    CondPageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from backend.models.decision import VentureDecision
from backend.presentation import build_plain_language_summary
from backend.presentation.detail_language import translate_detail_text

GREEN = colors.HexColor("#123B31")
ORANGE = colors.HexColor("#D96F2B")
PALE = colors.HexColor("#F2F6F2")
INK = colors.HexColor("#17231D")
MUTED = colors.HexColor("#667168")
FONT_DIR = Path(__file__).resolve().parent / "fonts"


def build_customer_pdf(decision: VentureDecision, language: str = "en") -> bytes:
    selected_language = language if language in {"en", "bn", "hi"} else "en"
    summary = decision.plain_language_summary or build_plain_language_summary(decision)
    first_page = _build_plain_language_page(decision, summary, selected_language)
    technical_pages = _build_localized_technical_pdf(decision, selected_language)
    writer = PdfWriter()
    writer.append(PdfReader(BytesIO(first_page)))
    writer.append(PdfReader(BytesIO(technical_pages)))
    writer.add_metadata(
        {
            "/Title": f"GramArtha business plan - {decision.analysis_id} - {selected_language}",
            "/Author": "GramArtha / SIH26091",
            "/Subject": "Plain-language decision summary followed by the complete technical report",
        }
    )
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def _build_localized_technical_pdf(decision: VentureDecision, language: str) -> bytes:
    """Build the complete seven-page technical layer in the selected language.

    The canonical VentureDecision is never mutated.  Locality names, official
    dataset names, URLs, analysis identifiers and numerical values are preserved.
    """
    summary = decision.plain_language_summary or build_plain_language_summary(decision)
    detail = summary.detailed_presentations[language]
    labels = detail.labels
    translations = detail.translations
    pdf = FPDF(format="A4", unit="mm")
    pdf.set_margins(13, 11, 13)
    pdf.set_auto_page_break(False)
    if language == "bn":
        pdf.add_font("GramArthaUnicode", fname=str(FONT_DIR / "NotoSansBengali.ttf"))
        family = "GramArthaUnicode"
    elif language == "hi":
        pdf.add_font("GramArthaUnicode", fname=str(FONT_DIR / "NotoSansDevanagari.ttf"))
        family = "GramArthaUnicode"
    else:
        pdf.add_font("GramArthaUnicode", fname=str(FONT_DIR / "NotoSansBengali.ttf"))
        family = "GramArthaUnicode"
    if language != "en":
        pdf.set_text_shaping(True)

    def label(key: str) -> str:
        return labels.get(key, DETAIL_FALLBACK.get(key, key.replace("_", " ").title()))

    def tr(value) -> str:
        if value is None:
            return "-"
        text = str(value)
        return translations.get(text, translate_detail_text(text, language))

    geography = decision.geography
    venture = decision.selected_venture
    primitive = venture.primitives[0] if venture else None
    twin = decision.digital_twin
    month_12 = twin.months[min(11, len(twin.months) - 1)] if twin and twin.months else None
    presentation = summary.presentations[language]

    def add_page(title: str):
        pdf.add_page()
        pdf.set_fill_color(18, 59, 49)
        pdf.rect(0, 0, 210, 19, style="F")
        pdf.set_text_color(255, 255, 255)
        pdf.set_font(family, size=7)
        pdf.set_xy(13, 5)
        pdf.cell(60, 4, "GRAMARTHA")
        pdf.set_xy(63, 5)
        pdf.set_font(family, size=11)
        pdf.cell(134, 5, title, align="R")
        pdf.set_y(24)
        pdf.set_text_color(23, 35, 29)
        pdf.set_draw_color(220, 229, 223)
        pdf.line(13, 282, 197, 282)
        pdf.set_xy(13, 284)
        pdf.set_text_color(102, 113, 104)
        pdf.set_font(family, size=5.8)
        pdf.cell(130, 4, f"GramArtha | {decision.analysis_id}")
        pdf.cell(54, 4, f"{label('page')} {pdf.page_no() + 1}", align="R")
        pdf.set_y(24)
        pdf.set_text_color(23, 35, 29)

    def heading(title: str):
        pdf.set_text_color(18, 59, 49)
        pdf.set_font(family, size=10)
        pdf.multi_cell(184, 5.2, title)
        pdf.set_text_color(23, 35, 29)

    def paragraph(text: str, *, muted: bool = False):
        pdf.set_text_color(*(102, 113, 104) if muted else (23, 35, 29))
        pdf.set_font(family, size=6.5)
        pdf.multi_cell(184, 3.4, text)
        pdf.ln(1)

    def rows(values):
        for key, value in values:
            pdf.set_fill_color(247, 249, 247)
            pdf.set_text_color(18, 59, 49)
            pdf.set_font(family, size=6.1)
            pdf.set_x(13)
            pdf.cell(62, 5.2, str(key), fill=True)
            pdf.set_text_color(23, 35, 29)
            pdf.cell(122, 5.2, str(value), fill=True)
            pdf.ln(5.6)
        pdf.ln(1)

    def bullets(title: str, values, limit: int | None = None):
        if not values:
            return
        pdf.set_text_color(18, 59, 49)
        pdf.set_font(family, size=7.2)
        pdf.multi_cell(184, 4, title)
        pdf.set_text_color(23, 35, 29)
        pdf.set_font(family, size=6.1)
        selected = list(values) if limit is None else list(values)[:limit]
        for item in selected:
            pdf.set_x(16)
            pdf.multi_cell(181, 3.2, f"- {tr(item)}")
        pdf.ln(1)

    # Page 2: recommendation, geography and market evidence.
    add_page(label("recommendation"))
    heading(presentation.recommended_venture_name)
    paragraph(presentation.why_recommended + " " + presentation.why_here)
    rows([
        (label("canonical_locality"), f"{geography.locality}, {geography.district}" if geography else "-"),
        (label("locality_type"), tr(geography.locality_type if geography else None)),
        (label("project_cost"), _money(venture.investment if venture else None)),
        (label("own_capital"), _money(decision.prudent_financing.get("own_capital_deployed"))),
        (label("finance_required"), _money(decision.prudent_financing.get("illustrative_financing_requirement"))),
        (label("confidence"), tr(decision.confidence.value)),
        (label("demand_opportunity"), _localized_interval(decision.demand, language, tr)),
        (label("reachable_supply"), _localized_interval(decision.supply, language, tr)),
        (label("price"), _localized_interval(decision.price, language, tr)),
        (label("planning_radius"), f"{_number(decision.catchment.get('radius_km'))} {_localized_unit('km', language)}"),
    ])
    paragraph(presentation.data_confidence, muted=True)
    bullets(label("customer_segments"), decision.sector_intelligence.get("customer_segments", []))
    bullets(label("supplier_plan"), decision.sector_intelligence.get("supplier_types", []))

    # Page 3: competition, catchment and operating context.
    add_page(label("competition"))
    rows([
        (label("direct_inside"), decision.competition.get("direct_count", tr("UNKNOWN"))),
        (label("indirect_inside"), decision.competition.get("indirect_count", tr("UNKNOWN"))),
        (label("competition_intensity"), tr(decision.competition.get("competition_intensity", "UNKNOWN"))),
        (label("coordinates_quality"), tr(decision.competition.get("coordinate_quality", "UNKNOWN"))),
        (label("nearest_market"), (decision.catchment.get("nearest_market") or {}).get("name", tr("UNKNOWN"))),
        (label("nearest_institution"), (decision.sector_intelligence.get("institutional_buyer_candidates") or [{}])[0].get("name", tr("UNKNOWN"))),
    ])
    paragraph(tr(decision.competition.get("caveat", "")), muted=True)
    _localized_entity_list(pdf, family, label("all_direct"), decision.competition.get("likely_direct_competitors", []), label, tr, language, add_page)
    _localized_entity_list(pdf, family, label("all_indirect"), decision.competition.get("likely_indirect_competitors", []), label, tr, language, add_page)
    if pdf.get_y() > 225:
        add_page(label("competition"))
    bullets(label("channels"), [f"{tr(item.get('role'))}: {tr(item.get('channel'))} ({tr(item.get('confidence'))})" for item in decision.sector_intelligence.get("distribution_channels", [])])
    bullets(label("operational_factors"), decision.sector_intelligence.get("operational_factors", []))
    bullets(label("weather"), decision.sector_intelligence.get("weather_factors", []))

    # Page 4: minimum viable setup and cost structure.
    add_page(label("business_setup"))
    if primitive:
        rows([
            (label("equipment_setup"), _money(primitive.capex)),
            (label("working_capital"), _money(primitive.working_capital)),
            (label("monthly_opex"), _money(primitive.monthly_opex)),
            (label("people"), primitive.staff),
            (label("space"), f"{_number(primitive.space_sqft)} {_localized_unit('sq ft', language)}"),
            (label("service_radius"), f"{_number(primitive.service_radius_km)} {_localized_unit('km', language)}"),
            (label("inventory_days"), primitive.inventory_days),
            (label("receivable_days"), primitive.receivable_days),
            (label("payable_days"), primitive.payable_days),
        ])
        bullets(label("equipment"), primitive.equipment)
        bullets(label("quality_controls"), primitive.quality_controls)
        bullets(label("licences"), primitive.licence_assumptions)
    heading(label("costs"))
    rows([(tr(key.replace("_", " ").title()), _money(value)) for key, value in decision.prudent_financing.get("capex_breakdown", {}).items()])
    bullets(label("insurance"), decision.sector_intelligence.get("insurance_options", []))

    # Page 5: finance, metrics, schemes and 36-month checkpoints.
    add_page(label("finance_cash"))
    metrics = decision.prudent_financing.get("financial_metrics", {})
    rows([
        (label("monthly_revenue"), _money(month_12.revenue if month_12 else None)),
        (label("operating_cash"), _money(month_12.operating_cash_flow if month_12 else None)),
        (label("operating_be"), _localized_month(twin.operating_break_even_month if twin else None, language)),
        (label("cash_be"), _localized_month(twin.cash_break_even_month if twin else None, language)),
        (label("payback"), _localized_month(twin.investment_payback_month if twin else None, language)),
        (label("npv"), _money(metrics.get("npv_36_month_at_12pct"))),
        (label("irr"), _percent(metrics.get("irr_annualized"))),
        (label("break_even_volume"), _number(metrics.get("break_even_volume_month"))),
    ])
    if twin:
        checkpoints = [m for m in twin.months if m.month % 3 == 0]
        bullets(label("cash36"), [f"{label('month')} {m.month}: {label('revenue')} {_money(m.revenue)}; {label('operating_cash')} {_money(m.operating_cash_flow)}; {label('closing_cash')} {_money(m.closing_cash)}" for m in checkpoints])
    bullets(label("finance_fit"), [f"{item.scheme_name}: {tr(item.status_wording)}" for item in decision.official_finance])

    # Page 6: scenarios, sensitivity, SWOT and failure boundaries.
    add_page(label("risk_scenarios"))
    scenario = next((item for item in decision.robust_comparison.get("candidate_summaries", []) if venture and item.get("candidate_id") == venture.candidate_id), {})
    rows([
        (label("scenarios"), scenario.get("scenario_count", label("quick_plan"))),
        (label("remain_solvent"), _percent(scenario.get("scenario_survival_rate"))),
        (label("payback36"), _percent(scenario.get("payback_within_36_months_rate"))),
        (label("p10_cash"), _money(scenario.get("minimum_cash_p10"))),
        (label("cvar"), _money(scenario.get("cvar95_loss"))),
    ])
    paragraph(label("scenario_caveat"), muted=True)
    for key in ("strengths", "weaknesses", "opportunities", "threats"):
        bullets(tr(key.upper()), decision.swot.get(key, []), 4)
    bullets(label("failure_boundaries"), [f"{tr(item.get('variable'))}: {_number(item.get('threshold'))} {_localized_unit(item.get('unit', ''), language)} - {tr(item.get('interpretation'))}" for item in decision.failure_boundaries])
    bullets(label("sensitivity"), [f"{tr(item.get('variable'))}: {tr('LOW')} {_money(item.get('profit_low'))}; {tr('MEDIUM')} {_money(item.get('profit_central'))}; {tr('HIGH')} {_money(item.get('profit_high'))}" for item in decision.sensitivity_analysis])

    # Page 7: pre-mortem and every staged action.
    add_page(label("actions"))
    bullets(label("premortem"), [f"{tr(item.get('cause'))} {tr(item.get('prevention'))}" for item in decision.premortem])
    action_keys = {"before_starting":"before_starting","day_1_7":"week1","first_30_days":"month1","months_2_3":"months23","months_4_6":"months46","stop_or_reconsider":"stop_reconsider"}
    for key, values in decision.action_plan.items():
        bullets(label(action_keys.get(key, key)), values)
    bullets(label("actions"), decision.staged_plan)

    # Page 8: evidence freshness, limitations and provenance.
    add_page(label("evidence"))
    rows([
        (label("confidence"), tr(decision.confidence.value)),
        (label("status"), tr(decision.status.value)),
        (label("decision_chain"), decision.methodology_version),
        ("Analysis ID", decision.analysis_id),
    ])
    for item in decision.evidence:
        paragraph(f"{tr(item.variable)} | {item.source_dataset} | {item.observation_date or tr('UNKNOWN')} | {tr(item.freshness_status.value)} | {tr(item.confidence.value)}", muted=False)
    bullets(label("limitations"), decision.limitations)
    bullets(label("sources"), decision.sources)
    return bytes(pdf.output())


DETAIL_FALLBACK = {"page": "Page"}


def _localized_interval(value, language, tr):
    if value is None or value.central is None:
        return "-"
    return f"{_number(value.lower)} - {_number(value.upper)} {_localized_unit(value.unit, language)} ({tr(value.status)})"


def _localized_month(value, language):
    if value is None:
        return {"bn": "৩৬ মাসের পরে / অর্জিত নয়", "hi": "36 माह के बाद / प्राप्त नहीं"}.get(language, "Beyond 36 months / not reached")
    return {"bn": f"মাস {value}", "hi": f"माह {value}"}.get(language, f"Month {value}")


def _localized_entity_list(pdf, family, title, entities, label, tr, language, add_page):
    if not entities:
        return
    def list_heading():
        pdf.set_text_color(18, 59, 49)
        pdf.set_font(family, size=7.2)
        pdf.multi_cell(184, 4, title)
        pdf.set_text_color(23, 35, 29)
        pdf.set_font(family, size=6.1)

    if pdf.get_y() > 268:
        add_page(title)
    list_heading()
    for item in entities:
        if pdf.get_y() > 272:
            add_page(title)
            list_heading()
        name = item.get("name") or label("unnamed")
        category = tr(item.get("category") or label("mapped_place"))
        distance = f"{_number(item.get('straight_line_distance_km'))} {_localized_unit('km', language)}"
        pdf.set_x(16)
        pdf.multi_cell(181, 3.2, f"- {name} | {category} | {distance}")
    pdf.ln(1)


def _build_technical_pdf(decision: VentureDecision) -> bytes:
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=17 * mm,
        leftMargin=17 * mm,
        topMargin=17 * mm,
        bottomMargin=15 * mm,
        title=f"GramArtha business plan - {decision.analysis_id}",
        author="GramArtha / SIH26091",
    )
    styles = _styles()
    story = []
    geography = decision.geography
    venture = decision.selected_venture
    primitive = venture.primitives[0] if venture else None
    twin = decision.digital_twin
    month_12 = twin.months[min(11, len(twin.months) - 1)] if twin and twin.months else None

    story.extend(
        [
            Paragraph("GRAMARTHA", styles["brand"]),
            Paragraph("Hyper-local business planning report", styles["gramartha_title"]),
            Paragraph(
                _text(
                    f"{geography.locality}, {geography.district}"
                    if geography
                    else "Unresolved geography"
                ),
                styles["subtitle"],
            ),
            Spacer(1, 8 * mm),
            _summary_table(decision, month_12, styles),
            Spacer(1, 5 * mm),
            Paragraph(
                "Planning estimates are not guaranteed income, a loan sanction, or a substitute "
                "for current supplier, customer, licence and lender verification.",
                styles["notice"],
            ),
        ]
    )

    _section(story, "1. Recommendation", styles)
    if venture and primitive:
        story.append(
            Paragraph(
                _text(
                    "The finite MVV oracle selected "
                    f"{primitive.primitive_type.value.lower()} as the lowest-investment tested "
                    "configuration satisfying the active profile constraints and creating useful "
                    "counterfactual flow."
                ),
                styles["body"],
            )
        )
        story.append(
            _key_value_table(
                [
                    ("Candidate", venture.candidate_id.split(":")[-1]),
                    ("Project cost", _money(venture.investment)),
                    (
                        "Own capital deployed",
                        _money(decision.prudent_financing.get("own_capital_deployed")),
                    ),
                    (
                        "Capital retained",
                        _money(decision.prudent_financing.get("capital_preserved_as_reserve")),
                    ),
                    (
                        "Finance required",
                        _money(
                            decision.prudent_financing.get("illustrative_financing_requirement")
                        ),
                    ),
                    ("Entry difficulty", decision.entry_difficulty.get("label", "Unknown")),
                ],
                styles,
            )
        )
    else:
        story.append(Paragraph("No venture was selected.", styles["body"]))

    _section(story, "2. Local market and evidence", styles)
    story.append(
        _key_value_table(
            [
                ("Demand", _interval(decision.demand)),
                ("Reachable supply", _interval(decision.supply)),
                ("Price / unit value", _interval(decision.price)),
                (
                    "Modelled gap",
                    _number(
                        max(
                            float(decision.demand.central or 0)
                            - float(decision.supply.central or 0),
                            0,
                        )
                    )
                    + f" {decision.demand.unit if decision.demand else ''}",
                ),
                ("Planning radius", f"{decision.catchment.get('radius_km', 'Unknown')} km"),
                (
                    "Nearest market",
                    (decision.catchment.get("nearest_market") or {}).get("name", "Not linked"),
                ),
            ],
            styles,
        )
    )
    _bullet_block(
        story,
        "Customer segments",
        decision.sector_intelligence.get("customer_segments", []),
        styles,
    )
    _bullet_block(
        story, "Supplier types", decision.sector_intelligence.get("supplier_types", []), styles
    )
    channels = [
        f"{item.get('role')}: {item.get('channel')} ({item.get('confidence')})"
        for item in decision.sector_intelligence.get("distribution_channels", [])
    ]
    _bullet_block(story, "Distribution channels", channels, styles)

    _section(story, "3. Competition and catchment", styles)
    story.append(
        _key_value_table(
            [
                ("Direct mapped candidates", decision.competition.get("direct_count", "Unknown")),
                (
                    "Indirect mapped candidates",
                    decision.competition.get("indirect_count", "Unknown"),
                ),
                ("Intensity", decision.competition.get("competition_intensity", "Unknown")),
                (
                    "Incumbent capacity",
                    "Unknown"
                    if decision.competition.get("capacity") is None
                    else decision.competition["capacity"],
                ),
                ("Market concentration / HHI", "Not calculated - market shares are unavailable"),
            ],
            styles,
        )
    )
    _entity_table(
        story,
        "Nearest direct candidates",
        decision.competition.get("likely_direct_competitors", []),
        styles,
    )
    _entity_table(
        story,
        "Nearest indirect candidates",
        decision.competition.get("likely_indirect_competitors", []),
        styles,
    )

    story.append(CondPageBreak(35 * mm))
    _section(story, "4. Business setup", styles)
    if primitive:
        story.append(
            _key_value_table(
                [
                    ("CAPEX", _money(primitive.capex)),
                    ("Working capital", _money(primitive.working_capital)),
                    ("Monthly fixed OPEX", _money(primitive.monthly_opex)),
                    ("Staff", primitive.staff),
                    ("Space", f"{_number(primitive.space_sqft)} sq ft"),
                    ("Service radius", f"{_number(primitive.service_radius_km)} km"),
                    ("Inventory days", _number(primitive.inventory_days)),
                    ("Receivable days", _number(primitive.receivable_days)),
                    ("Payable days", _number(primitive.payable_days)),
                ],
                styles,
            )
        )
        _bullet_block(story, "Equipment", primitive.equipment, styles)
        _bullet_block(story, "Quality controls", primitive.quality_controls, styles)
        _bullet_block(story, "Licences to verify", primitive.licence_assumptions, styles)
        _bullet_block(story, "Operational factors", primitive.operational_factors, styles)
        _bullet_block(story, "Weather / seasonality factors", primitive.weather_factors, styles)

    _section(story, "5. CAPEX, OPEX and working capital", styles)
    _mapping_table(
        story, "CAPEX allocation", decision.prudent_financing.get("capex_breakdown", {}), styles
    )
    opex = decision.prudent_financing.get("monthly_opex_breakdown", {})
    _mapping_table(story, "Fixed monthly OPEX allocation", opex.get("fixed", {}), styles)
    _mapping_table(
        story, "Month-12 variable cost allocation", opex.get("variable_month_12", {}), styles
    )
    working_capital = decision.prudent_financing.get("working_capital", {})
    story.append(
        _key_value_table(
            [
                ("Minimum modelled", _money(working_capital.get("minimum_modelled"))),
                (
                    "Recommended with 15% buffer",
                    _money(working_capital.get("recommended_with_15pct_buffer")),
                ),
                (
                    "Cash-conversion cycle",
                    f"{_number(working_capital.get('cash_conversion_cycle_days'))} days",
                ),
            ],
            styles,
        )
    )

    _section(story, "6. Finance and 36-month cash flow", styles)
    metrics = decision.prudent_financing.get("financial_metrics", {})
    story.append(
        _key_value_table(
            [
                ("Month-12 revenue", _money(month_12.revenue if month_12 else None)),
                (
                    "Month-12 operating cash",
                    _money(month_12.operating_cash_flow if month_12 else None),
                ),
                ("Operating break-even", _month(twin.operating_break_even_month if twin else None)),
                ("Investment payback", _month(twin.investment_payback_month if twin else None)),
                ("36-month NPV at 12%", _money(metrics.get("npv_36_month_at_12pct"))),
                ("Annualized IRR", _percent(metrics.get("irr_annualized"))),
                ("Break-even volume", _number(metrics.get("break_even_volume_month"))),
            ],
            styles,
        )
    )
    _cash_table(story, twin, styles)
    _finance_table(story, decision, styles)

    story.append(CondPageBreak(35 * mm))
    _section(story, "7. Scenario analysis and failure boundaries", styles)
    selected_summary = next(
        (
            item
            for item in decision.robust_comparison.get("candidate_summaries", [])
            if venture and item.get("candidate_id") == venture.candidate_id
        ),
        {},
    )
    story.append(
        _key_value_table(
            [
                ("Scenario count", selected_summary.get("scenario_count", "Quick plan")),
                ("Scenario survival", _percent(selected_summary.get("scenario_survival_rate"))),
                (
                    "Payback within 36 months",
                    _percent(selected_summary.get("payback_within_36_months_rate")),
                ),
                ("10th percentile minimum cash", _money(selected_summary.get("minimum_cash_p10"))),
                ("CVaR 95% cumulative loss", _money(selected_summary.get("cvar95_loss"))),
                ("Calibration", decision.robust_comparison.get("calibration_status", "Not run")),
            ],
            styles,
        )
    )
    _boundary_table(story, decision.failure_boundaries, styles)
    _sensitivity_table(story, decision.sensitivity_analysis, styles)

    _section(story, "8. Computed SWOT and pre-mortem", styles)
    for key in ("strengths", "weaknesses", "opportunities", "threats"):
        _bullet_block(story, key.title(), decision.swot.get(key, []), styles)
    pre_mortem = [
        f"{item.get('cause')} Prevention: {item.get('prevention')}" for item in decision.premortem
    ]
    _bullet_block(story, "Pre-mortem", pre_mortem, styles)

    _section(story, "9. Action plan", styles)
    action_labels = {
        "before_starting": "Before starting",
        "day_1_7": "Week 1",
        "first_30_days": "Month 1",
        "months_2_3": "Months 2-3",
        "months_4_6": "Months 4-6",
        "stop_or_reconsider": "Stop / reconsider",
    }
    for key, values in decision.action_plan.items():
        _bullet_block(story, action_labels.get(key, key), values, styles)

    story.append(CondPageBreak(35 * mm))
    _section(story, "10. Evidence, confidence and limitations", styles)
    story.append(
        Paragraph(
            _text(
                f"Decision confidence: {decision.confidence.value}. Methodology: "
                f"{decision.methodology_version}. Analysis ID: {decision.analysis_id}."
            ),
            styles["body"],
        )
    )
    grouped_evidence: dict[tuple[str, str, str, str], list[str]] = {}
    for item in decision.evidence:
        key = (
            item.source_dataset,
            str(item.observation_date or "Unknown"),
            item.freshness_status.value,
            item.confidence.value,
        )
        grouped_evidence.setdefault(key, []).append(item.variable)
    evidence_rows = []
    for (dataset, observation, freshness, confidence), variables in grouped_evidence.items():
        evidence_rows.append(
            [
                Paragraph(_text(", ".join(sorted(set(variables)))), styles["table"]),
                Paragraph(_text(dataset), styles["table"]),
                Paragraph(_text(observation), styles["table"]),
                Paragraph(_text(freshness), styles["table"]),
                Paragraph(_text(confidence), styles["table"]),
            ]
        )
    if evidence_rows:
        story.append(
            _table(
                [["Variable", "Dataset", "Observation", "Freshness", "Confidence"], *evidence_rows],
                [42 * mm, 58 * mm, 25 * mm, 28 * mm, 22 * mm],
            )
        )
    _bullet_block(story, "Evidence gates and limitations", decision.limitations, styles)
    if decision.sources:
        story.append(Paragraph("Sources", styles["h2x"]))
        story.append(
            Paragraph(
                "<br/>".join(
                    f"{index}. {_text(source)}"
                    for index, source in enumerate(decision.sources, start=1)
                ),
                styles["source"],
            )
        )

    document.build(
        story,
        onFirstPage=lambda canvas, doc: _page(canvas, doc, decision),
        onLaterPages=lambda canvas, doc: _page(canvas, doc, decision),
    )
    return buffer.getvalue()


def _build_plain_language_page(decision, summary, language: str) -> bytes:
    presentation = summary.presentations[language]
    labels = presentation.labels
    pdf = FPDF(format="A4", unit="mm")
    pdf.set_margins(13, 11, 13)
    pdf.set_auto_page_break(False)
    if language == "bn":
        pdf.add_font("GramArthaUnicode", fname=str(FONT_DIR / "NotoSansBengali.ttf"))
        family = "GramArthaUnicode"
    elif language == "hi":
        pdf.add_font("GramArthaUnicode", fname=str(FONT_DIR / "NotoSansDevanagari.ttf"))
        family = "GramArthaUnicode"
    else:
        family = "Helvetica"
    if language != "en":
        pdf.set_text_shaping(True)
    pdf.add_page()
    pdf.set_draw_color(220, 229, 223)
    pdf.set_fill_color(18, 59, 49)
    pdf.rect(0, 0, 210, 27, style="F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font(family, size=9)
    pdf.set_xy(13, 7)
    pdf.cell(0, 4, "GRAMARTHA")
    pdf.set_font(family, size=17)
    pdf.set_xy(13, 12)
    pdf.cell(0, 8, labels["simple_summary"])
    pdf.set_text_color(23, 35, 29)
    pdf.set_font(family, size=13)
    pdf.set_xy(13, 32)
    pdf.multi_cell(184, 7, presentation.recommended_venture_name)
    geography = decision.geography
    location = (
        f"{geography.locality}, {geography.district}" if geography else "Unresolved geography"
    )
    pdf.set_text_color(102, 113, 104)
    if language != "en":
        pdf.set_text_shaping(False)
    pdf.set_font(family, size=8)
    pdf.set_x(13)
    pdf.multi_cell(184, 4, location)
    if language != "en":
        pdf.set_text_shaping(True)
    pdf.ln(1)
    _fpdf_box(
        pdf,
        family,
        labels["conclusion"],
        presentation.conclusion_text,
        fill=(255, 245, 233),
        accent=(217, 111, 43),
    )
    _fpdf_two_text(
        pdf,
        family,
        (labels["why"], presentation.why_recommended + " " + presentation.why_here),
        (labels["who"], presentation.who_suits + " " + presentation.who_should_avoid),
    )
    _fpdf_section_title(pdf, family, labels["money"])
    _fpdf_metric_grid(
        pdf,
        family,
        [
            (labels["capital"], _summary_range(summary.capital_required, True, language)),
            (labels["own"], _summary_range(summary.own_money_used, True, language)),
            (labels["reserve"], _summary_range(summary.money_kept_as_reserve, True, language)),
            (labels["finance"], _summary_range(summary.finance_needed, True, language)),
            (labels["revenue"], _summary_range(summary.monthly_revenue, True, language)),
            (labels["cash"], _summary_range(summary.monthly_operating_cash, True, language)),
            (labels["break_even"], _summary_month(summary.break_even_month, labels)),
            (labels["payback"], _summary_month(summary.payback_month, labels)),
        ],
    )
    _fpdf_section_title(pdf, family, labels["market"])
    competition = summary.competition_summary
    competition_text = _summary_competition(competition, language)
    _fpdf_metric_grid(
        pdf,
        family,
        [
            (labels["demand"], _summary_range(summary.demand_opportunity, False, language)),
            (labels["price"], _summary_range(summary.price_guidance, True, language, True)),
            (labels["competition"], competition_text),
        ],
        columns=3,
    )
    _fpdf_three_lists(
        pdf,
        family,
        [
            (labels["advantages"], presentation.top_advantages[:3]),
            (labels["disadvantages"], presentation.top_disadvantages[:2]),
            (labels["risks"], presentation.top_risks[:3]),
        ],
    )
    _fpdf_action_box(pdf, family, labels["actions"], presentation.top_actions[:3])
    pdf.set_y(279)
    pdf.set_draw_color(220, 229, 223)
    pdf.line(13, 278, 197, 278)
    pdf.set_text_color(102, 113, 104)
    pdf.set_font(family, size=6.5)
    pdf.cell(
        0,
        4,
        f"{presentation.data_confidence}  |  {summary.method_version}  |  Page 1",
        align="C",
    )
    return bytes(pdf.output())


def _fpdf_section_title(pdf, family, title):
    pdf.ln(1.5)
    pdf.set_text_color(18, 59, 49)
    pdf.set_font(family, size=9.5)
    pdf.cell(0, 5, title)
    pdf.ln(5.5)


def _fpdf_box(pdf, family, title, body, *, fill, accent):
    x, y, width = pdf.get_x(), pdf.get_y(), 184
    pdf.set_fill_color(*fill)
    pdf.set_draw_color(*accent)
    pdf.rect(x, y, width, 20, style="DF")
    pdf.set_xy(x + 4, y + 3)
    pdf.set_text_color(*accent)
    pdf.set_font(family, size=8)
    pdf.cell(width - 8, 4, title)
    pdf.set_xy(x + 4, y + 8)
    pdf.set_text_color(23, 35, 29)
    pdf.set_font(family, size=8.5)
    pdf.multi_cell(width - 8, 4.2, body)
    pdf.set_y(y + 22)


def _fpdf_two_text(pdf, family, left, right):
    x, y, gap, width = 13, pdf.get_y(), 4, 90
    for index, (title, body) in enumerate((left, right)):
        cell_x = x + index * (width + gap)
        pdf.set_xy(cell_x, y)
        pdf.set_text_color(18, 59, 49)
        pdf.set_font(family, size=8)
        pdf.cell(width, 4, title)
        pdf.set_xy(cell_x, y + 5)
        pdf.set_text_color(23, 35, 29)
        pdf.set_font(family, size=7.2)
        pdf.multi_cell(width, 3.6, body)
    pdf.set_y(y + 25)


def _fpdf_metric_grid(pdf, family, items, columns=4):
    x, y, gap = 13, pdf.get_y(), 2.5
    width = (184 - gap * (columns - 1)) / columns
    rows = (len(items) + columns - 1) // columns
    for index, (label, value) in enumerate(items):
        row, column = divmod(index, columns)
        cell_x, cell_y = x + column * (width + gap), y + row * 20
        pdf.set_fill_color(248, 250, 247)
        pdf.set_draw_color(226, 231, 225)
        pdf.rect(cell_x, cell_y, width, 18, style="DF")
        pdf.set_xy(cell_x + 2, cell_y + 2)
        pdf.set_text_color(102, 113, 104)
        pdf.set_font(family, size=5.8)
        pdf.multi_cell(width - 4, 2.6, str(label), max_line_height=2.6)
        pdf.set_xy(cell_x + 2, cell_y + 10)
        pdf.set_text_color(23, 35, 29)
        ascii_value = str(value).isascii()
        if ascii_value and family != "Helvetica":
            pdf.set_text_shaping(False)
        pdf.set_font(family, size=6.4)
        pdf.multi_cell(width - 4, 3, str(value), max_line_height=3)
        if ascii_value and family != "Helvetica":
            pdf.set_text_shaping(True)
    pdf.set_y(y + rows * 20)


def _fpdf_three_lists(pdf, family, groups):
    x, y, gap, width = 13, pdf.get_y() + 2, 3, (184 - 6) / 3
    for index, (title, values) in enumerate(groups):
        cell_x = x + index * (width + gap)
        pdf.set_xy(cell_x, y)
        pdf.set_text_color(18, 59, 49)
        pdf.set_font(family, size=8)
        pdf.cell(width, 4, title)
        pdf.set_xy(cell_x, y + 5)
        pdf.set_text_color(23, 35, 29)
        pdf.set_font(family, size=6.5)
        pdf.multi_cell(width, 3.3, "\n".join(f"- {item}" for item in values))
    pdf.set_y(y + 42)


def _fpdf_action_box(pdf, family, title, values):
    x, y, width, height = 13, pdf.get_y() + 1, 184, 31
    pdf.set_fill_color(237, 247, 242)
    pdf.set_draw_color(192, 216, 204)
    pdf.rect(x, y, width, height, style="DF")
    pdf.set_xy(x + 4, y + 3)
    pdf.set_text_color(18, 59, 49)
    pdf.set_font(family, size=8)
    pdf.cell(width - 8, 4, title)
    pdf.set_xy(x + 4, y + 8)
    pdf.set_text_color(23, 35, 29)
    pdf.set_font(family, size=6.6)
    pdf.multi_cell(
        width - 8, 3.5, "\n".join(f"{index}. {item}" for index, item in enumerate(values, 1))
    )
    pdf.set_y(y + height + 1)


def _summary_range(value, money, language, include_unit=False):
    if value.lower is None or value.upper is None:
        return "-"
    if money:
        suffix = f" / {_localized_unit(value.unit, language)}" if include_unit else ""
        return f"INR {value.lower:,.0f} - {value.upper:,.0f}{suffix}"
    return f"{value.lower:,.1f} - {value.upper:,.1f} {_localized_unit(value.unit, language)}"


def _summary_month(value, labels):
    if value is None:
        return labels["beyond"]
    return labels["month"].replace("{month}", str(value))


def _localized_unit(unit, language):
    maps = {
        "bn": {
            "litres/month": "লিটার/মাস",
            "litre/month": "লিটার/মাস",
            "units/month": "ইউনিট/মাস",
            "INR/litre": "টাকা/লিটার",
            "INR/month": "টাকা/মাস",
            "km": "কিমি",
            "sq ft": "বর্গফুট",
            "days": "দিন",
            "planning revenue units/month": "পরিকল্পিত আয় একক/মাস",
            "share of central planning price": "কেন্দ্রীয় পরিকল্পিত দামের অংশ",
            "multiple of central variable cost": "কেন্দ্রীয় পরিবর্তনশীল খরচের গুণিতক",
            "multiple of central fixed OPEX": "কেন্দ্রীয় স্থির পরিচালন ব্যয়ের গুণিতক",
            "INR opening cash after startup investment": "প্রারম্ভিক বিনিয়োগের পর উদ্বোধনী নগদ (INR)",
        },
        "hi": {
            "litres/month": "लीटर/माह",
            "litre/month": "लीटर/माह",
            "units/month": "इकाई/माह",
            "INR/litre": "रुपये/लीटर",
            "INR/month": "रुपये/माह",
            "km": "किमी",
            "sq ft": "वर्ग फुट",
            "days": "दिन",
            "planning revenue units/month": "योजना आय इकाई/माह",
            "share of central planning price": "केंद्रीय योजना मूल्य का हिस्सा",
            "multiple of central variable cost": "केंद्रीय परिवर्ती लागत का गुणक",
            "multiple of central fixed OPEX": "केंद्रीय स्थिर परिचालन व्यय का गुणक",
            "INR opening cash after startup investment": "प्रारंभिक निवेश के बाद आरंभिक नकदी (INR)",
        },
    }
    return maps.get(language, {}).get(unit, unit)


def _summary_competition(competition, language):
    direct_count = competition.direct_count if competition.direct_count is not None else "-"
    indirect_count = competition.indirect_count if competition.indirect_count is not None else "-"
    if language == "bn":
        return (
            f"{direct_count} সরাসরি / {indirect_count} পরোক্ষ; "
            f"মানচিত্রভিত্তিক ঘনত্ব; {competition.radius_km or '-'} কিমি"
        )
    if language == "hi":
        return (
            f"{direct_count} प्रत्यक्ष / {indirect_count} अप्रत्यक्ष; "
            f"मानचित्र-आधारित घनत्व; {competition.radius_km or '-'} किमी"
        )
    return (
        f"{direct_count} direct / {indirect_count} indirect; "
        f"{competition.intensity}; {competition.radius_km or '-'} km"
    )


def _styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="brand",
            parent=styles["Normal"],
            textColor=ORANGE,
            fontSize=9,
            leading=11,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="gramartha_title",
            parent=styles["Title"],
            textColor=GREEN,
            fontSize=24,
            leading=28,
            alignment=TA_CENTER,
        )
    )
    styles.add(
        ParagraphStyle(
            name="subtitle",
            parent=styles["Normal"],
            textColor=MUTED,
            fontSize=10,
            leading=14,
            alignment=TA_CENTER,
        )
    )
    styles.add(
        ParagraphStyle(
            name="h1x",
            parent=styles["Heading1"],
            textColor=GREEN,
            fontSize=15,
            leading=19,
            spaceBefore=9,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="h2x",
            parent=styles["Heading2"],
            textColor=INK,
            fontSize=10,
            leading=13,
            spaceBefore=7,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="body",
            parent=styles["BodyText"],
            textColor=INK,
            fontSize=8.5,
            leading=12,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="table", parent=styles["BodyText"], textColor=INK, fontSize=6.7, leading=8.5
        )
    )
    styles.add(
        ParagraphStyle(
            name="source",
            parent=styles["BodyText"],
            textColor=MUTED,
            fontSize=6.2,
            leading=7.5,
            spaceAfter=2,
        )
    )
    styles.add(
        ParagraphStyle(
            name="notice",
            parent=styles["BodyText"],
            backColor=colors.HexColor("#FFF5E9"),
            borderColor=ORANGE,
            borderWidth=0.5,
            borderPadding=7,
            textColor=INK,
            fontSize=8,
            leading=11,
        )
    )
    return styles


def _page(canvas, document, decision):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#DDE5DF"))
    canvas.line(18 * mm, 14 * mm, 192 * mm, 14 * mm)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 9 * mm, f"GramArtha | {decision.analysis_id}")
    canvas.drawRightString(192 * mm, 9 * mm, f"Page {document.page}")
    canvas.restoreState()


def _section(story, title, styles):
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(_text(title), styles["h1x"]))


def _bullet_block(story, title, values, styles):
    if not values:
        return
    story.append(Paragraph(_text(title), styles["h2x"]))
    story.extend(Paragraph(f"- {_text(str(value))}", styles["body"]) for value in values)


def _summary_table(decision, month_12, styles):
    venture = decision.selected_venture
    data = [
        ["Recommendation", "Project cost", "Month-12 cash", "Confidence"],
        [
            Paragraph(_text((decision.sector or "No selection").title()), styles["table"]),
            Paragraph(_text(_money(venture.investment if venture else None)), styles["table"]),
            Paragraph(
                _text(_money(month_12.operating_cash_flow if month_12 else None)), styles["table"]
            ),
            Paragraph(_text(decision.confidence.value), styles["table"]),
        ],
    ]
    return _table(data, [44 * mm] * 4)


def _key_value_table(rows, styles):
    return _table(
        [
            [
                Paragraph(_text(str(key)), styles["table"]),
                Paragraph(_text(str(value)), styles["table"]),
            ]
            for key, value in rows
        ],
        [65 * mm, 111 * mm],
        header=False,
    )


def _mapping_table(story, title, mapping, styles):
    if not mapping:
        return
    story.append(Paragraph(_text(title), styles["h2x"]))
    story.append(
        _key_value_table(
            [(key.replace("_", " ").title(), _money(value)) for key, value in mapping.items()],
            styles,
        )
    )


def _entity_table(story, title, entities, styles):
    if not entities:
        return
    story.append(Paragraph(_text(title), styles["h2x"]))
    rows = [["Name", "Category", "Straight-line distance"]]
    rows.extend(
        [
            Paragraph(_text(item.get("name") or "Unnamed mapped candidate"), styles["table"]),
            Paragraph(_text(item.get("category") or "Unknown"), styles["table"]),
            Paragraph(
                _text(f"{_number(item.get('straight_line_distance_km'))} km"), styles["table"]
            ),
        ]
        for item in entities
    )
    story.append(_table(rows, [80 * mm, 55 * mm, 41 * mm]))


def _cash_table(story, twin, styles):
    if not twin:
        return
    story.append(Paragraph("Quarterly cash-flow checkpoints", styles["h2x"]))
    rows = [["Month", "Revenue", "Operating cash", "Closing cash", "DSCR"]]
    rows.extend(
        [
            month.month,
            _money(month.revenue),
            _money(month.operating_cash_flow),
            _money(month.closing_cash),
            _number(month.debt_service_coverage_ratio),
        ]
        for month in twin.months
        if month.month % 3 == 0
    )
    story.append(_table(rows, [22 * mm, 39 * mm, 39 * mm, 39 * mm, 37 * mm]))


def _finance_table(story, decision, styles):
    if not decision.official_finance:
        return
    story.append(Paragraph("Current scheme screening", styles["h2x"]))
    rows = [["Scheme", "Freshness", "Eligibility", "Status"]]
    rows.extend(
        [
            Paragraph(_text(item.scheme_name), styles["table"]),
            Paragraph(_text(item.freshness_status), styles["table"]),
            Paragraph(_text(str(item.eligible)), styles["table"]),
            Paragraph(_text(item.status_wording), styles["table"]),
        ]
        for item in decision.official_finance
    )
    story.append(_table(rows, [42 * mm, 28 * mm, 24 * mm, 82 * mm]))


def _boundary_table(story, values, styles):
    if not values:
        return
    story.append(Paragraph("Failure boundaries", styles["h2x"]))
    rows = [["Variable", "Threshold", "Interpretation"]]
    rows.extend(
        [
            Paragraph(_text(item.get("variable", "")), styles["table"]),
            Paragraph(
                _text(f"{_number(item.get('threshold'))} {item.get('unit', '')}"), styles["table"]
            ),
            Paragraph(_text(item.get("interpretation", "")), styles["table"]),
        ]
        for item in values
    )
    story.append(_table(rows, [38 * mm, 43 * mm, 95 * mm]))


def _sensitivity_table(story, values, styles):
    if not values:
        return
    story.append(Paragraph("Sensitivity ranking", styles["h2x"]))
    rows = [["Variable", "Low cash", "Central cash", "High cash", "Elasticity"]]
    rows.extend(
        [
            item.get("variable"),
            _money(item.get("profit_low")),
            _money(item.get("profit_central")),
            _money(item.get("profit_high")),
            _number(item.get("elasticity")),
        ]
        for item in values
    )
    story.append(_table(rows, [40 * mm, 34 * mm, 34 * mm, 34 * mm, 34 * mm]))


def _table(data, widths, header=True):
    table = Table(data, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#DDE5DF")),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("TEXTCOLOR", (0, 0), (-1, -1), INK),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
    ]
    if header:
        commands.extend(
            [
                ("BACKGROUND", (0, 0), (-1, 0), GREEN),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    else:
        commands.append(("BACKGROUND", (0, 0), (0, -1), PALE))
    table.setStyle(TableStyle(commands))
    return table


def _interval(value):
    if value is None or value.central is None:
        return "Insufficient evidence"
    return f"{_number(value.lower)} - {_number(value.upper)} {value.unit} ({value.status})"


def _money(value):
    return "-" if value is None else f"INR {float(value):,.0f}"


def _number(value):
    return "-" if value is None else f"{float(value):,.2f}".rstrip("0").rstrip(".")


def _percent(value):
    return "-" if value is None else f"{float(value) * 100:.1f}%"


def _month(value):
    return "Beyond 36 months / not reached" if value is None else f"Month {value}"


def _text(value):
    return escape(str(value).replace("\u2011", "-").replace("\u2192", "->"))

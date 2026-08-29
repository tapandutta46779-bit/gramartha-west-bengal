from __future__ import annotations

from io import BytesIO
from xml.sax.saxutils import escape

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

GREEN = colors.HexColor("#123B31")
ORANGE = colors.HexColor("#D96F2B")
PALE = colors.HexColor("#F2F6F2")
INK = colors.HexColor("#17231D")
MUTED = colors.HexColor("#667168")


def build_customer_pdf(decision: VentureDecision) -> bytes:
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
        for item in entities[:12]
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

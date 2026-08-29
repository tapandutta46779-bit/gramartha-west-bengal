from __future__ import annotations

import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    CondPageBreak,
    Frame,
    LongTable,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/GRAMARTHA_MASTER_TECHNICAL_REPORT_V0.6.0.md"
OUTPUT = ROOT / "output/pdf/GramArtha_Master_Technical_Report_v0.6.0.pdf"

GREEN = colors.HexColor("#123B31")
TEAL = colors.HexColor("#18745A")
ORANGE = colors.HexColor("#D96F2B")
PALE = colors.HexColor("#EFF5F1")
INK = colors.HexColor("#17231D")
MUTED = colors.HexColor("#667168")


def rich(value: str) -> str:
    value = html.escape(value.strip().replace("\u2011", "-").replace("\u2192", "->"))
    value = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
    return value


def style_map():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "GA60Title",
            parent=base["Title"],
            fontSize=25,
            leading=30,
            textColor=GREEN,
            alignment=TA_CENTER,
            spaceAfter=8 * mm,
        ),
        "subtitle": ParagraphStyle(
            "GA60Subtitle",
            parent=base["Normal"],
            fontSize=10,
            leading=14,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceAfter=4 * mm,
        ),
        "h2": ParagraphStyle(
            "GA60H2",
            parent=base["Heading2"],
            fontSize=15,
            leading=19,
            textColor=TEAL,
            spaceBefore=3.5 * mm,
            spaceAfter=2.5 * mm,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "GA60Body",
            parent=base["BodyText"],
            fontSize=9.8,
            leading=13.5,
            textColor=INK,
            spaceAfter=1.8 * mm,
        ),
        "bullet": ParagraphStyle(
            "GA60Bullet",
            parent=base["BodyText"],
            fontSize=9.4,
            leading=12.8,
            leftIndent=5 * mm,
            firstLineIndent=-3.5 * mm,
            textColor=INK,
            spaceAfter=1.0 * mm,
        ),
        "table": ParagraphStyle(
            "GA60Table", parent=base["BodyText"], fontSize=7.1, leading=9.1, textColor=INK
        ),
        "table_header": ParagraphStyle(
            "GA60TableHeader",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.1,
            leading=9.1,
            textColor=colors.white,
        ),
    }


def header_footer(canvas, document):
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(GREEN)
    canvas.rect(0, height - 9 * mm, width, 9 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 7.4)
    canvas.drawString(18 * mm, height - 6 * mm, "GRAMARTHA | MASTER TECHNICAL REPORT v0.6.0")
    canvas.setStrokeColor(colors.HexColor("#C5D4CB"))
    canvas.line(18 * mm, 14 * mm, width - 18 * mm, 14 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7.2)
    canvas.drawString(18 * mm, 9.5 * mm, "SIH26091 | Audited 29 August 2026")
    canvas.drawRightString(width - 18 * mm, 9.5 * mm, f"Page {document.page}")
    canvas.restoreState()


def table_from(lines, styles):
    rows = []
    for index, line in enumerate(lines):
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        style = styles["table_header"] if index == 0 else styles["table"]
        rows.append([Paragraph(rich(cell), style) for cell in cells])
    available = A4[0] - 36 * mm
    widths = [available / len(rows[0])] * len(rows[0])
    table = LongTable(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), GREEN),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B7C7BD")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
            ]
        )
    )
    return table


def story():
    styles = style_map()
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    result = [
        Spacer(1, 18 * mm),
        Paragraph("SIH26091 | GRAMARTHA", styles["subtitle"]),
        Paragraph("Master Technical Report", styles["title"]),
        Paragraph(
            "Version 0.6.0 | System architecture, data engineering, mathematical models, "
            "decision pipeline and production implementation",
            styles["subtitle"],
        ),
        Spacer(1, 8 * mm),
        Paragraph(
            "A complete technical description of the evidence-to-decision system for "
            "hyper-local enterprise discovery across West Bengal.",
            ParagraphStyle(
                "GA60Cover",
                parent=styles["body"],
                fontSize=12,
                leading=18,
                textColor=GREEN,
                alignment=TA_CENTER,
                leftIndent=12 * mm,
                rightIndent=12 * mm,
            ),
        ),
        Spacer(1, 9 * mm),
        LongTable(
            [
                [
                    Paragraph("SYSTEM SCALE", styles["table_header"]),
                    Paragraph("DECISION ENGINE", styles["table_header"]),
                ],
                [
                    Paragraph(
                        "23 districts, 40,474 current product localities, 381,523 locality "
                        "evidence records and 1,022 regional priors.",
                        styles["table"],
                    ),
                    Paragraph(
                        "Graph construction, min-cost maximum flow, bottleneck analysis, exact "
                        "finite MVV search, finance, digital twin and robust stress selection.",
                        styles["table"],
                    ),
                ],
            ],
            colWidths=[(A4[0] - 52 * mm) / 2] * 2,
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), GREEN),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#B7C7BD")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 7),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ]
            ),
        ),
        Spacer(1, 7 * mm),
        table_from(
            [
                "| Stage | Computation | Primary output |",
                "| 1. Resolve | Current geography + historical crosswalk | Canonical locality |",
                "| 2. Evidence | Source, date, unit, freshness, confidence | "
                "Auditable variable set |",
                "| 3. Estimate | Demand, supply, price, capacity intervals | Local market state |",
                "| 4. Network | Catchment + economic graph + exact flow | Gap and bottleneck |",
                "| 5. Design | Venture generation + profile constraints | "
                "Feasible configurations |",
                "| 6. Select | MVV + inverse optimization + Pareto/regret | "
                "Recommended configuration |",
                "| 7. Finance | 36-month twin + stress + schemes | Capital and action plan |",
            ],
            styles,
        ),
        Spacer(1, 6 * mm),
        Paragraph(
            "Prepared as a professional engineering reference for implementation review, "
            "model audit, product demonstration and controlled future expansion.",
            ParagraphStyle(
                "GA60CoverFoot",
                parent=styles["body"],
                fontSize=9.5,
                leading=14,
                textColor=MUTED,
                alignment=TA_CENTER,
                leftIndent=12 * mm,
                rightIndent=12 * mm,
            ),
        ),
        PageBreak(),
        Paragraph("Technical contents", styles["h2"]),
        table_from(
            [
                "| Part | Sections | Engineering coverage |",
                "| I. Product and evidence foundation | 1-8 | Problem, workflow, geography, "
                "sources and freshness |",
                "| II. Statistical estimation | 9-17 | HCES, ASUSE, models, population, "
                "demand, supply, price and factors |",
                "| III. Network and venture computation | 18-27 | Sector adapters, dairy, "
                "graph, flow, bottlenecks, MVV and robustness |",
                "| IV. Finance and risk | 28-35 | Unit economics, digital twin, schemes, "
                "scenarios, CVaR, sensitivity and staging |",
                "| V. Product implementation | 36-45 | UI, PDFs, API, schema, deployment, "
                "testing and expansion |",
            ],
            styles,
        ),
        Spacer(1, 5 * mm),
        Paragraph(
            "Reading path: Sections 1-8 define the evidence contract; Sections 9-17 explain "
            "statistical estimation; Sections 18-27 formalize network repair and optimization; "
            "Sections 28-35 establish finance and risk mathematics; Sections 36-45 document "
            "the production software, interfaces, verification and deployment architecture.",
            styles["body"],
        ),
        Spacer(1, 3 * mm),
        table_from(
            [
                "| Design rule | Engineering consequence |",
                "| Evidence before inference | Missing current facts become gates or field tasks |",
                "| Unit-safe computation | Physical and monetary flows never share "
                "implicit units |",
                "| Exact scope labels | Finite search, projections and proxies retain "
                "their scope |",
                "| One decision object | API, website and PDF reproduce the same calculations |",
                "| Reproducible release | Checksummed inputs, deterministic tests and "
                "versioned deploys |",
            ],
            styles,
        ),
        Spacer(1, 3 * mm),
        table_from(
            [
                "| Symbol | Definition |",
                "| D, S, U | Demand, reachable supply and unserved demand |",
                "| f_e, u_e, c_e | Edge flow, capacity and unit economic cost |",
                "| I, C, Dmax | Investment, own capital and acceptable-debt ceiling |",
                "| CCC | Inventory days + receivable days - payable days |",
                "| VaR95, CVaR95 | Loss percentile and mean tail loss |",
            ],
            styles,
        ),
        PageBreak(),
    ]
    paragraph = []

    def flush():
        if paragraph:
            result.append(Paragraph(rich(" ".join(paragraph)), styles["body"]))
            paragraph.clear()

    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith("| "):
            flush()
            table_lines = [line]
            index += 2
            while index < len(lines) and lines[index].startswith("|"):
                table_lines.append(lines[index])
                index += 1
            result.extend([table_from(table_lines, styles), Spacer(1, 3 * mm)])
            continue
        if line.startswith("## "):
            flush()
            result.append(CondPageBreak(22 * mm))
            result.append(Paragraph(rich(line[3:]), styles["h2"]))
        elif line.startswith("- ") or re.match(r"^\d+\. ", line):
            flush()
            value = re.sub(r"^(- |\d+\. )", "", line)
            result.append(Paragraph(rich(value), styles["bullet"], bulletText="-"))
        elif not line.strip():
            flush()
        elif not line.startswith("# ") and not line.startswith("Audit date:"):
            paragraph.append(line.strip())
        index += 1
    flush()
    return result


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document = BaseDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=17 * mm,
        bottomMargin=19 * mm,
        title="GramArtha Master Technical Report v0.6.0",
        author="SIH26091 GramArtha implementation",
    )
    frame = Frame(document.leftMargin, document.bottomMargin, document.width, document.height)
    document.addPageTemplates([PageTemplate(id="report", frames=[frame], onPageEnd=header_footer)])
    document.build(story())
    print(OUTPUT)


if __name__ == "__main__":
    main()

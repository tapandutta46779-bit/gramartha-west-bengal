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
            spaceAfter=4 * mm,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "GA60Body",
            parent=base["BodyText"],
            fontSize=9.1,
            leading=13.2,
            textColor=INK,
            spaceAfter=2.2 * mm,
        ),
        "bullet": ParagraphStyle(
            "GA60Bullet",
            parent=base["BodyText"],
            fontSize=8.9,
            leading=12.5,
            leftIndent=5 * mm,
            firstLineIndent=-3.5 * mm,
            textColor=INK,
            spaceAfter=1.4 * mm,
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
        Spacer(1, 32 * mm),
        Paragraph("SIH26091 | GRAMARTHA", styles["subtitle"]),
        Paragraph("Master Technical Report", styles["title"]),
        Paragraph("Version 0.6.0 | Evidence, mathematics, product and audit", styles["subtitle"]),
        Spacer(1, 16 * mm),
        Paragraph(
            "Current/historical West Bengal geography, survey models, economic network repair, "
            "profile-constrained optimization, dairy, robust finance and customer product.",
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
        Spacer(1, 18 * mm),
        LongTable(
            [
                [
                    Paragraph("VERIFIED", styles["table_header"]),
                    Paragraph("BOUNDARY", styles["table_header"]),
                ],
                [
                    Paragraph(
                        "55 tests; 23 current districts; 40,474 current localities; "
                        "trained artifacts; customer PDF.",
                        styles["table"],
                    ),
                    Paragraph(
                        "Conditional planning evidence; no guaranteed income, lender approval "
                        "or complete current locality market census.",
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
        PageBreak(),
    ]
    paragraph = []
    first = True

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
            if not first:
                result.append(PageBreak())
            first = False
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

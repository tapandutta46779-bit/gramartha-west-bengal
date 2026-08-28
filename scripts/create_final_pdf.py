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
SOURCE = ROOT / "docs/FINAL_COMPLETION_REPORT_V0.3.0.md"
OUTPUT = ROOT / "output/pdf/SIH26091_Final_Completion_Report_v0.3.0.pdf"

NAVY = colors.HexColor("#17324D")
BLUE = colors.HexColor("#1D5D88")
PALE = colors.HexColor("#EAF2F7")
INK = colors.HexColor("#18222B")
MUTED = colors.HexColor("#51616F")


def rich(text: str) -> str:
    escaped = html.escape(text.strip())
    escaped = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", escaped)
    return escaped


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=29,
            textColor=NAVY,
            alignment=TA_CENTER,
            spaceAfter=10 * mm,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontSize=10,
            leading=14,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceAfter=4 * mm,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=19,
            textColor=BLUE,
            spaceBefore=5 * mm,
            spaceAfter=2.5 * mm,
            keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "H3",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11.5,
            leading=15,
            textColor=NAVY,
            spaceBefore=3.5 * mm,
            spaceAfter=1.5 * mm,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=13.2,
            textColor=INK,
            spaceAfter=2.1 * mm,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12.5,
            leftIndent=5 * mm,
            firstLineIndent=-3.5 * mm,
            bulletIndent=1 * mm,
            textColor=INK,
            spaceAfter=1.4 * mm,
        ),
        "table": ParagraphStyle(
            "Table",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.2,
            leading=9.2,
            textColor=INK,
        ),
        "table_header": ParagraphStyle(
            "TableHeader",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.3,
            leading=9.3,
            textColor=colors.white,
        ),
    }


def header_footer(canvas, document) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(colors.HexColor("#BDD0DD"))
    canvas.setLineWidth(0.5)
    canvas.line(18 * mm, height - 15 * mm, width - 18 * mm, height - 15 * mm)
    canvas.setFont("Helvetica-Bold", 7.5)
    canvas.setFillColor(NAVY)
    canvas.drawString(18 * mm, height - 11.5 * mm, "SIH26091 - Final Completion Report v0.3.0")
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(width - 18 * mm, 10 * mm, f"Page {document.page}")
    canvas.restoreState()


def table_from(lines: list[str], style_map: dict) -> LongTable:
    rows = []
    for index, line in enumerate(lines):
        cells = [item.strip() for item in line.strip().strip("|").split("|")]
        style = style_map["table_header"] if index == 0 else style_map["table"]
        rows.append([Paragraph(rich(cell), style) for cell in cells])
    columns = len(rows[0])
    available = A4[0] - 36 * mm
    if columns == 3:
        widths = [available * 0.25, available * 0.18, available * 0.57]
    elif columns == 4:
        widths = [available * 0.23, available * 0.17, available * 0.18, available * 0.42]
    else:
        widths = [available / columns] * columns
    table = LongTable(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#AEBFCB")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
            ]
        )
    )
    return table


def build_story() -> list:
    style_map = styles()
    lines = SOURCE.read_text().splitlines()
    story = [
        Spacer(1, 24 * mm),
        Paragraph("SIH26091", style_map["subtitle"]),
        Paragraph("Final Completion Report", style_map["title"]),
        Paragraph("West Bengal Hyper-Local Economic Network Repair", style_map["subtitle"]),
        Paragraph("Version 0.3.0 | Audited 28 August 2026", style_map["subtitle"]),
        Spacer(1, 22 * mm),
        Paragraph(
            "Evidence-first implementation, data-freshness audit, real survey model training, "
            "production integration, multi-district validation, mathematical audit and honest "
            "decision limitations.",
            ParagraphStyle(
                "CoverBody",
                parent=style_map["body"],
                fontSize=12,
                leading=18,
                textColor=NAVY,
                alignment=TA_CENTER,
            ),
        ),
        PageBreak(),
    ]
    index = 3  # skip Markdown title, blank line and audit-date line represented on cover
    paragraph = []

    def flush_paragraph() -> None:
        if paragraph:
            story.append(Paragraph(rich(" ".join(paragraph)), style_map["body"]))
            paragraph.clear()

    while index < len(lines):
        line = lines[index]
        if line.startswith("| "):
            flush_paragraph()
            table_lines = [line]
            index += 2  # skip Markdown separator
            while index < len(lines) and lines[index].startswith("|"):
                table_lines.append(lines[index])
                index += 1
            story.extend([table_from(table_lines, style_map), Spacer(1, 3 * mm)])
            continue
        if line.startswith("## "):
            flush_paragraph()
            story.append(Paragraph(rich(line[3:]), style_map["h2"]))
        elif line.startswith("### "):
            flush_paragraph()
            story.append(Paragraph(rich(line[4:]), style_map["h3"]))
        elif line.startswith("- "):
            flush_paragraph()
            story.append(
                Paragraph(rich(line[2:]), style_map["bullet"], bulletText="\u2022")
            )
        elif not line.strip():
            flush_paragraph()
        elif not line.startswith("# "):
            paragraph.append(line.strip())
        index += 1
    flush_paragraph()
    return story


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document = BaseDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=21 * mm,
        bottomMargin=21 * mm,
        title="SIH26091 Final Completion Report v0.3.0",
        author="SIH26091 Implementation Team",
        subject="West Bengal evidence, model, optimization and validation completion report",
    )
    frame = Frame(
        document.leftMargin,
        document.bottomMargin,
        document.width,
        document.height,
        id="content",
    )
    document.addPageTemplates(
        [PageTemplate(id="report", frames=[frame], onPageEnd=header_footer)]
    )
    document.build(build_story())
    print(OUTPUT)


if __name__ == "__main__":
    main()

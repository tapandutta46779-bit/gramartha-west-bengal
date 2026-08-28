from __future__ import annotations

import html
import re
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    LongTable,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/GRAMARTHA_DEEP_ENGINE_REPORT_V0.5.0.md"
OUTPUT = ROOT / "output/pdf/GramArtha_Deep_Engine_Product_Report_v0.5.0.pdf"
TMP = ROOT / "tmp/pdfs/gramartha_v050"

NAVY = colors.HexColor("#153A4A")
TEAL = colors.HexColor("#0E7C78")
GOLD = colors.HexColor("#E5A63B")
PALE = colors.HexColor("#EAF5F3")
INK = colors.HexColor("#17252A")
MUTED = colors.HexColor("#50666E")


def rich(text: str) -> str:
    value = html.escape(text.strip())
    value = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
    return value


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=25,
            leading=30,
            textColor=NAVY,
            alignment=TA_CENTER,
            spaceAfter=9 * mm,
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
            fontSize=16,
            leading=20,
            textColor=TEAL,
            spaceAfter=4 * mm,
            keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "H3",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11.5,
            leading=15,
            textColor=NAVY,
            spaceBefore=3 * mm,
            spaceAfter=1.5 * mm,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.1,
            leading=13.1,
            textColor=INK,
            spaceAfter=2.2 * mm,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.9,
            leading=12.5,
            leftIndent=5 * mm,
            firstLineIndent=-3.5 * mm,
            bulletIndent=1 * mm,
            textColor=INK,
            spaceAfter=1.5 * mm,
        ),
        "table": ParagraphStyle(
            "Table",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.1,
            leading=9.1,
            textColor=INK,
        ),
        "table_header": ParagraphStyle(
            "TableHeader",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.2,
            leading=9.2,
            textColor=colors.white,
        ),
    }


def header_footer(canvas, document) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(NAVY)
    canvas.rect(0, height - 9 * mm, width, 9 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 7.4)
    canvas.drawString(18 * mm, height - 6 * mm, "GRAMARTHA | DEEP ENGINE v0.5.0")
    canvas.setStrokeColor(colors.HexColor("#B8CFCC"))
    canvas.setLineWidth(0.45)
    canvas.line(18 * mm, 14 * mm, width - 18 * mm, 14 * mm)
    canvas.setFont("Helvetica", 7.4)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 9.5 * mm, "Verified local product report | 28 August 2026")
    canvas.drawRightString(width - 18 * mm, 9.5 * mm, f"Page {document.page}")
    canvas.restoreState()


def make_table(lines: list[str], style_map: dict[str, ParagraphStyle]) -> LongTable:
    rows = []
    for index, line in enumerate(lines):
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        style = style_map["table_header"] if index == 0 else style_map["table"]
        rows.append([Paragraph(rich(cell), style) for cell in cells])
    count = len(rows[0])
    available = A4[0] - 36 * mm
    if count == 2:
        widths = [available * 0.33, available * 0.67]
    elif count == 3:
        widths = [available * 0.24, available * 0.22, available * 0.54]
    elif count == 4:
        widths = [available * 0.30, available * 0.18, available * 0.17, available * 0.35]
    elif count == 7:
        widths = [available * 0.22] + [available * 0.13] * 6
    else:
        widths = [available / count] * count
    table = LongTable(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#A9BFBD")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
            ]
        )
    )
    return table


def screenshot(path: Path) -> Image:
    TMP.mkdir(parents=True, exist_ok=True)
    crop_path = TMP / f"{path.stem}_report_crop.png"
    with PILImage.open(path) as source:
        width, height = source.size
        if "finance" in path.stem:
            top = min(780, max(0, height - 1050))
        else:
            top = min(590, max(0, height - 1050))
        bottom = min(height, top + 1050)
        source.crop((0, top, width, bottom)).save(crop_path)
    image = Image(str(crop_path))
    max_width = A4[0] - 40 * mm
    max_height = 174 * mm
    scale = min(max_width / image.imageWidth, max_height / image.imageHeight)
    image.drawWidth = image.imageWidth * scale
    image.drawHeight = image.imageHeight * scale
    image.hAlign = "CENTER"
    return image


def build_story() -> list:
    style_map = styles()
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    story = [
        Spacer(1, 31 * mm),
        Paragraph("SIH26091 | GRAMARTHA", style_map["subtitle"]),
        Paragraph("Deep Engine and Product Completion Report", style_map["title"]),
        Paragraph("Version 0.5.0 | Audited 28 August 2026", style_map["subtitle"]),
        Spacer(1, 16 * mm),
        Paragraph(
            "West Bengal hyper-local venture planning, evidence freshness, trained models, "
            "finite optimization, joint uncertainty, robust choice, finance, and verified "
            "product behavior.",
            ParagraphStyle(
                "CoverBody",
                parent=style_map["body"],
                fontSize=12,
                leading=18,
                textColor=NAVY,
                alignment=TA_CENTER,
                leftIndent=12 * mm,
                rightIndent=12 * mm,
            ),
        ),
        Spacer(1, 14 * mm),
        LongTable(
            [
                [
                    Paragraph("VERIFIED", style_map["table_header"]),
                    Paragraph("BOUNDARY", style_map["table_header"]),
                ],
                [
                    Paragraph(
                        "Local HTTP product, 23 district smoke checks, 7 deep E2E cases, "
                        "50 tests, trained artifacts.",
                        style_map["table"],
                    ),
                    Paragraph(
                        "Conditional benchmark, not observed 2026 locality market or "
                        "lender approval.",
                        style_map["table"],
                    ),
                ],
            ],
            colWidths=[(A4[0] - 52 * mm) / 2] * 2,
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#A9BFBD")),
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
    paragraph: list[str] = []
    first_section = True

    def flush() -> None:
        if paragraph:
            story.append(Paragraph(rich(" ".join(paragraph)), style_map["body"]))
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
            story.extend([make_table(table_lines, style_map), Spacer(1, 3 * mm)])
            continue
        if line.startswith("## "):
            flush()
            if not first_section:
                story.append(PageBreak())
            first_section = False
            story.append(Paragraph(rich(line[3:]), style_map["h2"]))
            story.append(Spacer(1, 1.5 * mm))
        elif line.startswith("### "):
            flush()
            story.append(Paragraph(rich(line[4:]), style_map["h3"]))
        elif line.startswith("- "):
            flush()
            story.append(Paragraph(rich(line[2:]), style_map["bullet"], bulletText="-"))
        elif line.startswith("[[IMAGE:"):
            flush()
            relative = line[len("[[IMAGE:") : -2]
            story.extend([screenshot(ROOT / relative), Spacer(1, 3 * mm)])
        elif not line.strip():
            flush()
        elif not line.startswith("# ") and not line.startswith("Audit date:"):
            paragraph.append(line.strip())
        index += 1
    flush()
    return story


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document = BaseDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=17 * mm,
        bottomMargin=19 * mm,
        title="GramArtha Deep Engine and Product Completion Report v0.5.0",
        author="SIH26091 GramArtha implementation",
        subject="Verified West Bengal evidence, modelling, robustness and product report",
    )
    frame = Frame(
        document.leftMargin,
        document.bottomMargin,
        document.width,
        document.height,
        id="content",
    )
    document.addPageTemplates([PageTemplate(id="report", frames=[frame], onPageEnd=header_footer)])
    document.build(build_story())
    print(OUTPUT)


if __name__ == "__main__":
    main()

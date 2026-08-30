import re
import sqlite3
import unicodedata
from pathlib import Path

import uharfbuzz as hb

from backend.pipeline.sector_factors import REGISTRY
from backend.reporting.pdf_language import BENGALI_PDF_EXACT, translate_pdf_text

ROOT = Path(__file__).resolve().parents[1]
FONT_PATH = ROOT / "backend/reporting/fonts/NotoSerifBengali-Regular.ttf"
GEOGRAPHY_DB = ROOT / "data/sih26091_phase2.sqlite"
SECTOR_TEXT_FIELDS = (
    "customer_segments",
    "supplier_types",
    "channels",
    "equipment",
    "quality_controls",
    "operational_factors",
    "weather_factors",
    "insurance",
)
ALLOWED_TECHNICAL_TOKENS = (
    "ASUSE",
    "BSK",
    "CVaR",
    "FMCG",
    "FSSAI",
    "GST",
    "HHI",
    "INR",
    "IRR",
    "MVV",
    "NPV",
    "OSM",
    "PMMY",
)


def _unexpected_english_words(text: str) -> list[str]:
    checked = text
    for token in ALLOWED_TECHNICAL_TOKENS:
        checked = checked.replace(token, "")
    return re.findall(r"[A-Za-z]{2,}", checked)


def test_all_sector_registry_terms_have_complete_bengali_pdf_copy():
    terms = {
        value
        for factors in REGISTRY.values()
        for field in SECTOR_TEXT_FIELDS
        for value in getattr(factors, field)
    }
    assert len(terms) == 196
    incomplete = {
        term: translated
        for term in sorted(terms)
        if _unexpected_english_words(translated := translate_pdf_text(term, "bn"))
    }
    assert incomplete == {}


def test_screenshot_reported_bengali_phrases_are_human_reviewed():
    expected = {
        "MEDIUM": "মাঝারি",
        "HISTORICAL_BASELINE": "ঐতিহাসিক ভিত্তি",
        "STALE_FOR_DECISION": "সিদ্ধান্তে ব্যবহারের জন্য পুরোনো",
        "OSM POIs are volunteered proxy evidence and may be incomplete.": (
            "OSM-এর স্থানভিত্তিক তথ্য স্বেচ্ছায় সংযোজিত প্রক্সি প্রমাণ; তাই এটি অসম্পূর্ণ হতে পারে।"
        ),
    }
    for source, bengali in expected.items():
        assert translate_pdf_text(source, "bn") == bengali

    limitation_sources = [
        source
        for source in BENGALI_PDF_EXACT
        if source.startswith("Current ") or source.startswith("OSM POIs")
    ]
    assert len(limitation_sources) == 4
    for source in limitation_sources:
        assert not _unexpected_english_words(translate_pdf_text(source, "bn"))


def test_bengali_pdf_font_shapes_critical_copy_without_missing_glyphs():
    font_data = FONT_PATH.read_bytes()
    font = hb.Font(hb.Face(font_data))
    critical_text = " ".join(
        [
            "মাঝারি ঐতিহাসিক ভিত্তি সিদ্ধান্তে ব্যবহারের জন্য পুরোনো সীমাবদ্ধতা",
            *BENGALI_PDF_EXACT.values(),
        ]
    )
    buffer = hb.Buffer()
    buffer.add_str(critical_text)
    buffer.direction = "ltr"
    buffer.script = "beng"
    buffer.language = "bn"
    hb.shape(font, buffer)
    assert buffer.glyph_infos
    assert all(info.codepoint != 0 for info in buffer.glyph_infos)


def test_all_statewide_geography_names_are_safe_for_pdf_preservation():
    connection = sqlite3.connect(GEOGRAPHY_DB)
    rows = connection.execute(
        "SELECT canonical_name, current_district, entity_type FROM current_geo_entity"
    ).fetchall()
    connection.close()

    assert len(rows) == 40_971
    assert len({district for _, district, _ in rows}) == 23
    assert sum(entity_type == "WARD" for _, _, entity_type in rows) == 2_903
    assert sum(entity_type == "VILLAGE" for _, _, entity_type in rows) == 37_571

    failures = []
    for name, district, entity_type in rows:
        for field, value in (("name", name), ("district", district)):
            if not value or not unicodedata.is_normalized("NFC", value):
                failures.append((entity_type, field, value, "not NFC"))
                continue
            if "\u25cc" in value or "\ufffd" in value:
                failures.append((entity_type, field, value, "invalid display glyph"))
            if unicodedata.category(value[0]).startswith("M"):
                failures.append((entity_type, field, value, "starts with combining mark"))
            if any(unicodedata.category(character).startswith("C") for character in value):
                failures.append((entity_type, field, value, "contains control character"))
    assert failures == []

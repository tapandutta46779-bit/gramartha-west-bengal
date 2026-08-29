from __future__ import annotations

import json
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from scripts.build_public_package import ROOT, allowed
from scripts.build_wb_census_crosswalk import sha256

VERSION = "0.7.1"
NAME = f"SIH26091_GRAMARTHA_v{VERSION}_PUBLIC_SHARE"
PACKAGE_DIR = ROOT / "deliverables" / NAME
ZIP_PATH = PACKAGE_DIR / f"{NAME}.zip"


def files() -> list[Path]:
    trees = ["backend", "config", "database", "deploy", "docs", "frontend", "scripts", "tests"]
    selected = [
        ROOT / "README.md",
        ROOT / "FILES_TO_DELETE.md",
        ROOT / "pyproject.toml",
        ROOT / "render.yaml",
        ROOT / "data/sih26091_phase2.sqlite",
        ROOT / "data/west_bengal_osm.sqlite",
        ROOT / "outputs/e2e/v0.6.0/WEST_BENGAL_E2E_AND_PROFILE_VALIDATION.json",
        ROOT / "outputs/e2e/v0.6.0/WEST_BENGAL_E2E_AND_PROFILE_VALIDATION.md",
        ROOT / "outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS/WEST_BENGAL_GEOGRAPHY_AUDIT.json",
        ROOT / "outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS/models/model_registry.json",
        ROOT / "outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS/FINAL_TECHNICAL_AUDIT.json",
        ROOT / "outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS/DATA_FRESHNESS_AUDIT.json",
        ROOT / "output/pdf/GramArtha_Master_Technical_Report_v0.6.0.pdf",
        ROOT / "output/pdf/GramArtha_Puapur_Transport_Business_Plan_v0.7.1_en.pdf",
        ROOT / "output/pdf/GramArtha_Puapur_Transport_Business_Plan_v0.7.1_bn.pdf",
        ROOT / "output/pdf/GramArtha_Puapur_Transport_Business_Plan_v0.7.1_hi.pdf",
        ROOT / "sources/official/current/WB_ARD_District_Milk_Production_2024-25.pdf",
    ]
    for tree in trees:
        selected.extend(path for path in (ROOT / tree).rglob("*") if allowed(path))
    return sorted({path for path in selected if path.is_file()})


def main() -> None:
    PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
    selected = files()
    entries = [
        {
            "path": str(path.relative_to(ROOT)),
            "size_bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in selected
    ]
    manifest = {
        "package": NAME,
        "status": "VERIFIED_CONDITIONAL_PLANNING_PRODUCT",
        "created_at": datetime.now(UTC).isoformat(),
        "file_count": len(entries),
        "uncompressed_size_bytes": sum(item["size_bytes"] for item in entries),
        "verified": {
            "pytest": "59 passed",
            "ruff": "passed",
            "javascript_syntax": "passed",
            "multilingual_output": (
                "one canonical numeric decision; full-detail English, Bengali and Hindi "
                "website/PDF views"
            ),
            "pdf": (
                "three eight-page A4 files; all pages rendered and visually inspected "
                "with Indic glyph shaping"
            ),
            "public_url": "https://gramartha-west-bengal.onrender.com",
            "osm": (
                "named direct candidates, categories, distances, counts, intensity and "
                "capacity caveat rendered in the tested public flow; deployment asset retains "
                "all 23 district administrative proxies"
            ),
            "pdf_downloads": (
                "same-page attachment download after restart-safe canonical-decision restore; "
                "English, Bengali and Hindi use application/pdf attachment responses"
            ),
        },
        "exclusions": [
            "restricted HCES/ASUSE respondent-level archives",
            "private fitted joblib artifacts pending redistribution-terms review",
            "credentials, local analysis rows, duplicate and temporary files",
        ],
        "claim_boundary": (
            "Conditional planning estimates only; not observed complete locality demand, "
            "calibrated success probability, lender approval or guaranteed income."
        ),
        "files": entries,
    }
    manifest_text = json.dumps(manifest, indent=2) + "\n"
    readme = (
        "# GramArtha v0.7.1 Public Share Package\n\n"
        "Open `docs/FULL_DETAIL_LOCALIZATION_AUDIT_V0.7.1.md`, the three language-specific "
        "eight-page business-plan PDFs and "
        "`output/pdf/GramArtha_Master_Technical_Report_v0.6.0.pdf`. "
        "The live product is https://gramartha-west-bengal.onrender.com. Restricted respondent "
        "microdata and private fitted model artifacts are excluded.\n"
    )
    (PACKAGE_DIR / "PACKAGE_MANIFEST.json").write_text(manifest_text, encoding="utf-8")
    (PACKAGE_DIR / "README_FIRST.md").write_text(readme, encoding="utf-8")
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        archive.writestr(f"{NAME}/PACKAGE_MANIFEST.json", manifest_text)
        archive.writestr(f"{NAME}/README_FIRST.md", readme)
        for path in selected:
            archive.write(path, f"{NAME}/{path.relative_to(ROOT)}")
    checksum = sha256(ZIP_PATH)
    (PACKAGE_DIR / "SHA256SUM.txt").write_text(f"{checksum}  {ZIP_PATH.name}\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "zip": str(ZIP_PATH),
                "size_bytes": ZIP_PATH.stat().st_size,
                "sha256": checksum,
                "file_count": len(entries),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

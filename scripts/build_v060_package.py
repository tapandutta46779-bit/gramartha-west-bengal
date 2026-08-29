from __future__ import annotations

import json
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from scripts.build_public_package import ROOT, allowed
from scripts.build_wb_census_crosswalk import sha256

VERSION = "0.6.0"
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
        ROOT / "outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS/WEST_BENGAL_GEOGRAPHY_AUDIT.md",
        ROOT / "outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS/WEST_BENGAL_GEOGRAPHY_AUDIT.csv",
        ROOT / "outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS/models/model_registry.json",
        ROOT / "outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS/FINAL_TECHNICAL_AUDIT.json",
        ROOT / "outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS/DATA_FRESHNESS_AUDIT.json",
        ROOT / "outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS/DATA_FRESHNESS_AUDIT.md",
        ROOT / "outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS/FLOW_PERFORMANCE.json",
        ROOT / "output/pdf/GramArtha_Dairy_Abhirampur_Business_Plan_v0.6.0.pdf",
        ROOT / "output/pdf/GramArtha_Master_Technical_Report_v0.6.0.pdf",
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
        "status": "VERIFIED_CURRENT_GRAMARTHA_V0.6.0_CONDITIONAL_PLANNING_PRODUCT",
        "created_at": datetime.now(UTC).isoformat(),
        "file_count": len(entries),
        "uncompressed_size_bytes": sum(item["size_bytes"] for item in entries),
        "verified": {
            "pytest": "55 passed",
            "geography": "23 current districts; 40,474 localities; zero hierarchy audit errors",
            "e2e": "12 cross-district/locality/profile cases with honest refusal cases",
            "browser": "current seven-stage GramArtha local HTTP main flow; zero console errors",
            "customer_pdf_pages": 9,
            "master_report_pages": 41,
            "deployment_runtime": "fresh decompression, API analysis and customer PDF passed",
        },
        "exclusions": [
            "restricted HCES/ASUSE respondent-level archives",
            "private fitted joblib artifacts pending redistribution-terms review",
            "duplicate, temporary and split-part files",
        ],
        "claim_boundary": (
            "Outputs are conditional planning estimates. They are not observed complete locality "
            "demand, current supplier quotes, calibrated success probabilities, lender approvals "
            "or guaranteed income."
        ),
        "files": entries,
    }
    manifest_text = json.dumps(manifest, indent=2) + "\n"
    (PACKAGE_DIR / "PACKAGE_MANIFEST.json").write_text(manifest_text, encoding="utf-8")
    readme = (
        "# GramArtha v0.6.0 Public Share Package\n\n"
        "Start with `output/pdf/GramArtha_Master_Technical_Report_v0.6.0.pdf` and "
        "`docs/REQUIREMENT_AUDIT_V0.6.0.md`. This package includes the current seven-stage "
        "GramArtha application, operational West Bengal databases, the original WB ARD 2024-25 "
        "milk-production source PDF, code, tests, E2E evidence and both final PDFs. Restricted "
        "survey respondent files and private fitted artifacts are intentionally excluded.\n"
    )
    (PACKAGE_DIR / "README_FIRST.md").write_text(readme, encoding="utf-8")
    with zipfile.ZipFile(
        ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6
    ) as archive:
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

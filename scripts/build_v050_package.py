from __future__ import annotations

import json
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from scripts.build_public_package import ROOT, allowed
from scripts.build_wb_census_crosswalk import sha256

VERSION = "0.5.0"
NAME = f"SIH26091_GRAMARTHA_v{VERSION}_PUBLIC_SHARE"
PACKAGE_DIR = ROOT / "deliverables" / NAME
ZIP_PATH = PACKAGE_DIR / f"{NAME}.zip"


def files() -> list[Path]:
    trees = ["backend", "config", "database", "docs", "frontend", "scripts", "tests"]
    selected = [
        ROOT / "README.md",
        ROOT / "FILES_TO_DELETE.md",
        ROOT / "pyproject.toml",
        ROOT / "data/sih26091_phase2.sqlite",
        ROOT / "data/west_bengal_osm.sqlite",
        ROOT / "outputs/e2e/product_e2e_v0.5.0.json",
        ROOT / "outputs/e2e/all_district_smoke_v0.5.0.json",
        ROOT / "output/pdf/GramArtha_Deep_Engine_Product_Report_v0.5.0.pdf",
        ROOT / "output/screenshots/v0.5.0/gramartha_summary_kolkata.png",
        ROOT / "output/screenshots/v0.5.0/gramartha_finance_kolkata.png",
        ROOT
        / "outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS/models/model_registry.json",
        ROOT
        / "outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS/FINAL_TECHNICAL_AUDIT.json",
        ROOT
        / "outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS/DATA_FRESHNESS_AUDIT.json",
        ROOT
        / "outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS/DATA_FRESHNESS_AUDIT.md",
        ROOT
        / "outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS/FLOW_PERFORMANCE.json",
    ]
    for tree in trees:
        selected.extend(path for path in (ROOT / tree).rglob("*") if allowed(path))
    return sorted(set(selected))


def main() -> None:
    PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
    selected = files()
    missing = [str(path.relative_to(ROOT)) for path in selected if not path.is_file()]
    if missing:
        raise FileNotFoundError(missing)
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
        "status": "VERIFIED_LOCAL_PRODUCT_CONDITIONAL_BENCHMARK",
        "created_at": datetime.now(UTC).isoformat(),
        "file_count": len(entries),
        "uncompressed_size_bytes": sum(item["size_bytes"] for item in entries),
        "verified": {
            "pytest": "50 passed",
            "district_smoke": "23/23 HTTP 200; 22 conditional; 1 evidence-gated",
            "deep_e2e": "7/7 HTTP 200; 512 scenarios per case",
            "report_pages": 31,
        },
        "exclusions": [
            "restricted HCES/ASUSE respondent-level archives",
            "private fitted joblib artifacts pending redistribution-terms review",
            "temporary, duplicate and split-part files",
            (
                "public deployment because the local product is not deployed to the supplied "
                "Netlify URL"
            ),
        ],
        "evidence_limit": (
            "Generic sector outputs are low-confidence MODELLED_BENCHMARK planning cases, "
            "not observed current locality transactions or lender approvals."
        ),
        "files": entries,
    }
    manifest_path = PACKAGE_DIR / "PACKAGE_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    readme = PACKAGE_DIR / "README_FIRST.md"
    readme.write_text(
        "# GramArtha v0.5.0 Public Share Package\n\n"
        "Start with `output/pdf/GramArtha_Deep_Engine_Product_Report_v0.5.0.pdf`. "
        "The package includes the local application, operational West Bengal databases, "
        "configuration, documentation, tests, E2E records, screenshots, and public-safe model "
        "metrics. Restricted survey respondent records and private fitted joblib files are "
        "excluded. The product returns conditional planning benchmarks, not guaranteed current "
        "market or lender decisions.\n",
        encoding="utf-8",
    )
    with zipfile.ZipFile(
        ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6
    ) as archive:
        archive.writestr(
            f"{NAME}/PACKAGE_MANIFEST.json", json.dumps(manifest, indent=2) + "\n"
        )
        archive.writestr(f"{NAME}/README_FIRST.md", readme.read_text(encoding="utf-8"))
        for path in selected:
            archive.write(path, f"{NAME}/{path.relative_to(ROOT)}")
    checksum = sha256(ZIP_PATH)
    (PACKAGE_DIR / "SHA256SUM.txt").write_text(
        f"{checksum}  {ZIP_PATH.name}\n", encoding="utf-8"
    )
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

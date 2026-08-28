from __future__ import annotations

import json
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from scripts.build_wb_census_crosswalk import sha256

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "deliverables/SIH26091_v0.3.0_PUBLIC_SHARE"
ZIP_PATH = PACKAGE_DIR / "SIH26091_v0.3.0_PUBLIC_SHARE.zip"

TOP_LEVEL_FILES = [
    "README.md",
    "FILES_TO_DELETE.md",
    "pyproject.toml",
    "database/schema.sql",
    "data/sih26091_phase2.sqlite",
    "data/west_bengal_osm.sqlite",
    "output/pdf/SIH26091_Final_Completion_Report_v0.3.0.pdf",
]
TREES = ["backend", "config", "docs", "frontend", "scripts", "tests"]
PUBLIC_RAW_TREES = [
    "work/raw_stage/DS057_ALL_WEST_BENGAL",
    "work/raw_stage/DS071_WEST_BENGAL",
    "work/raw_stage/CENSUS_2011_LOCATION_DIRECTORY",
    "work/raw_stage/CENSUS_2011_PCA_WEST_BENGAL",
    "work/raw_stage/BAHS_2025",
    "work/raw_stage/HCES_2022_23_TECHNICAL",
    "work/raw_stage/HCES_2023_24_TECHNICAL",
    "work/raw_stage/ASUSE_2023_24_TECHNICAL",
    "work/raw_stage/ASUSE_2025_TECHNICAL",
]


def allowed(path: Path) -> bool:
    return (
        path.is_file()
        and path.name != ".DS_Store"
        and "__pycache__" not in path.parts
        and path.suffix not in {".pyc", ".joblib"}
        and not path.name.startswith(".")
        and ".part-" not in path.name
        and ".tail-" not in path.name
    )


def package_files() -> list[Path]:
    files = [ROOT / value for value in TOP_LEVEL_FILES]
    for directory in [*TREES, *PUBLIC_RAW_TREES]:
        files.extend(path for path in (ROOT / directory).rglob("*") if allowed(path))
    output = ROOT / "outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS"
    files.extend(
        path
        for path in output.rglob("*")
        if allowed(path) and path.name != "model_registry.json"
    )
    files.append(output / "models/model_registry.json")
    return sorted(set(files))


def build() -> dict:
    PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
    files = package_files()
    missing = [str(path.relative_to(ROOT)) for path in files if not path.is_file()]
    if missing:
        raise FileNotFoundError(missing)
    entries = [
        {
            "path": str(path.relative_to(ROOT)),
            "size_bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in files
    ]
    manifest = {
        "package": "SIH26091_v0.3.0_PUBLIC_SHARE",
        "created_at": datetime.now(UTC).isoformat(),
        "file_count": len(entries),
        "uncompressed_size_bytes": sum(item["size_bytes"] for item in entries),
        "exclusions": [
            "restricted HCES/ASUSE unit-record archives",
            "fitted joblib artifacts pending redistribution-terms review",
            "temporary, duplicate and split-part files",
        ],
        "files": entries,
    }
    manifest_path = PACKAGE_DIR / "PUBLIC_PACKAGE_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    readme = PACKAGE_DIR / "README_FIRST.md"
    readme.write_text(
        "# SIH26091 v0.3.0 Public Share Package\n\n"
        "This folder contains the versioned public-share ZIP, its exact manifest, and checksum. "
        "The ZIP includes the working application, tests, documentation, final PDF, aggregate "
        "survey outputs, operational West Bengal databases, and public source files.\n\n"
        "Restricted HCES/ASUSE unit records and fitted joblib files are intentionally excluded. "
        "See `docs/PRIVATE_APPLICANT_FILES_MANIFEST.md` inside the ZIP.\n"
    )
    root_name = "SIH26091_v0.3.0_PUBLIC_SHARE"
    with zipfile.ZipFile(
        ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6
    ) as archive:
        archive.writestr(
            f"{root_name}/PUBLIC_PACKAGE_MANIFEST.json",
            json.dumps(manifest, indent=2) + "\n",
        )
        archive.writestr(f"{root_name}/README_FIRST.md", readme.read_text())
        for path in files:
            archive.write(path, f"{root_name}/{path.relative_to(ROOT)}")
    checksum = sha256(ZIP_PATH)
    (PACKAGE_DIR / "SHA256SUM.txt").write_text(f"{checksum}  {ZIP_PATH.name}\n")
    manifest["zip_size_bytes"] = ZIP_PATH.stat().st_size
    manifest["zip_sha256"] = checksum
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


if __name__ == "__main__":
    result = build()
    print(
        json.dumps(
            {
                "file_count": result["file_count"],
                "uncompressed_size_bytes": result["uncompressed_size_bytes"],
                "zip_size_bytes": result["zip_size_bytes"],
                "zip_sha256": result["zip_sha256"],
                "zip": str(ZIP_PATH),
            },
            indent=2,
        )
    )

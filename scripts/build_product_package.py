from __future__ import annotations

import json
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from scripts.build_public_package import ROOT, allowed
from scripts.build_wb_census_crosswalk import sha256

VERSION = "0.4.0"
NAME = f"SIH26091_v{VERSION}_PRODUCT_PREVIEW"
PACKAGE_DIR = ROOT / "deliverables" / NAME
ZIP_PATH = PACKAGE_DIR / f"{NAME}.zip"


def files() -> list[Path]:
    roots = ["backend", "config", "database", "docs", "frontend", "scripts", "tests"]
    result = [
        ROOT / "README.md",
        ROOT / "pyproject.toml",
        ROOT / "data/sih26091_phase2.sqlite",
        ROOT / "data/west_bengal_osm.sqlite",
        ROOT / "outputs/e2e/product_e2e_v0.4.0.json",
    ]
    for item in roots:
        result.extend(path for path in (ROOT / item).rglob("*") if allowed(path))
    return sorted(set(result))


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
        "status": "PRODUCT_PREVIEW_NOT_FINAL_COMPLETION",
        "created_at": datetime.now(UTC).isoformat(),
        "file_count": len(entries),
        "uncompressed_size_bytes": sum(x["size_bytes"] for x in entries),
        "evidence_limit": "v0.4 sector outputs are MODELLED_BENCHMARK, not observed locality sales",
        "files": entries,
    }
    manifest_path = PACKAGE_DIR / "PACKAGE_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        archive.writestr(f"{NAME}/PACKAGE_MANIFEST.json", json.dumps(manifest, indent=2) + "\n")
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

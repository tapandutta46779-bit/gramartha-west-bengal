from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from scripts.build_wb_census_crosswalk import sha256

CATALOG_BY_2011_DISTRICT = {district: 6517 + district for district in range(1, 20)}


def _fetch(url: str) -> bytes:
    return subprocess.run(
        [
            "curl",
            "--location",
            "--fail",
            "--silent",
            "--show-error",
            "--max-time",
            "120",
            "--user-agent",
            "SIH26091-data-ingestor/1.0",
            url,
        ],
        check=True,
        capture_output=True,
    ).stdout


def download(destination: Path, manifest_path: Path) -> dict:
    destination.mkdir(parents=True, exist_ok=True)
    files = []
    blockers = []
    for district_number, catalog_id in CATALOG_BY_2011_DISTRICT.items():
        catalog_url = f"https://censusindia.gov.in/nada/index.php/catalog/{catalog_id}"
        try:
            html = _fetch(catalog_url).decode("utf-8", errors="replace")
            matches = re.findall(
                rf"https://censusindia\.gov\.in/nada/index\.php/catalog/{catalog_id}"
                r"/download/\d+/[^\"<]+\.xlsx",
                html,
            )
            if not matches:
                raise ValueError("No official PCA XLSX link found on catalog page")
            url = matches[0].replace("&amp;", "&")
            filename = f"WB_2011_PCA_TV_19{district_number:02d}.xlsx"
            path = destination / filename
            payload = _fetch(url)
            path.write_bytes(payload)
            files.append(
                {
                    "district_sequence_2011": district_number,
                    "catalog_id": catalog_id,
                    "catalog_url": catalog_url,
                    "download_url": url,
                    "filename": filename,
                    "size_bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )
        except Exception as error:
            blockers.append(
                {
                    "district_sequence_2011": district_number,
                    "catalog_id": catalog_id,
                    "catalog_url": catalog_url,
                    "error": f"{type(error).__name__}: {error}",
                }
            )
    result = {
        "dataset_id": "CENSUS2011-PCA-TV-WB-ALL-2011-DISTRICTS",
        "created_at": datetime.now(UTC).isoformat(),
        "publisher": "Office of the Registrar General & Census Commissioner, India",
        "observation_year": 2011,
        "files": files,
        "downloaded_count": len(files),
        "expected_count": len(CATALOG_BY_2011_DISTRICT),
        "blockers": blockers,
        "projection_warning": (
            "These are observed 2011 counts and must not be presented as observed 2026 population."
        ),
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Download official WB Census 2011 PCA files")
    parser.add_argument("destination", type=Path)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(download(args.destination, args.manifest), indent=2))


if __name__ == "__main__":
    main()

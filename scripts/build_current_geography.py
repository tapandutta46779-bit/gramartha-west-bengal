from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

from backend.evidence.current_geography import rebuild_current_geography


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the canonical current-product geography and historical crosswalk."
    )
    parser.add_argument("--sqlite", default="data/sih26091_phase2.sqlite")
    parser.add_argument(
        "--report",
        default=("outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS/CURRENT_GEOGRAPHY_BUILD_REPORT.json"),
    )
    args = parser.parse_args()
    connection = sqlite3.connect(args.sqlite)
    report = {
        "methodology_version": "CURRENT_PRODUCT_GEOGRAPHY_V1",
        "source_rule": (
            "DS057 post-split publisher hierarchy defines current product districts; "
            "Census-2011 remains historical and crosses only by exact compatible hierarchy."
        ),
        "official_lgd_status": (
            "NOT_ACQUIRED: official LGD bulk download is CAPTCHA-gated; product IDs are not "
            "represented as official LGD codes."
        ),
        **rebuild_current_geography(connection),
    }
    output = Path(args.report)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

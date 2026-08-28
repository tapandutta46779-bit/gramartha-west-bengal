from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi.testclient import TestClient

os.environ.setdefault("SIH26091_SQLITE_PATH", "data/sih26091_phase2.sqlite")

from backend.api.main import app, store  # noqa: E402, I001
from backend.evidence.districts import canonical_district  # noqa: E402, I001


def district_key(value: str) -> str:
    if value.casefold() in {"barddhaman", "bardhaman"}:
        return "Barddhaman"
    return canonical_district(value) or value


def main() -> None:
    client = TestClient(app)
    districts = store.list_districts()
    geographies = store.all_geographies()
    results = []
    for district in districts:
        geography = next(item for item in geographies if district_key(item.district) == district)
        response = client.post(
            "/analyze",
            json={
                "geo_id": geography.geo_id,
                "capital": 100_000,
                "business_category": "kirana",
                "analysis_mode": "quick",
            },
        )
        payload = response.json()
        results.append(
            {
                "district": district,
                "geo_id": geography.geo_id,
                "locality": geography.locality,
                "locality_type": geography.locality_type,
                "http_status": response.status_code,
                "decision_status": payload.get("status"),
                "selected_candidate": bool(payload.get("selected_venture")),
                "blocking_gates": [
                    gate["code"] for gate in payload.get("evidence_gates", []) if gate["blocking"]
                ],
            }
        )
    output = Path("outputs/e2e/all_district_smoke_v0.5.0.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps({"district_count": len(results), "results": results}, indent=2))
    if not all(item["http_status"] == 200 for item in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

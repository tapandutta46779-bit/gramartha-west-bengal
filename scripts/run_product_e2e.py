from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi.testclient import TestClient

os.environ.setdefault("SIH26091_SQLITE_PATH", "data/sih26091_phase2.sqlite")

from backend.api.main import app  # noqa: E402, I001


CASES = [
    ("Kolkata", "Kolkata", "kirana", 100_000),
    ("Barasat", "24 Paraganas North", "poultry", 100_000),
    ("Abad Bhagabanpur", "24 Paraganas South", "fishery", 125_000),
    ("Kharibari", "Darjiling", "food processing", 150_000),
    ("Anandapur", "Jalpaiguri", "transport", 120_000),
    ("Adina", "Maldah", "kirana", 80_000),
    ("Adra", "Purulia", "poultry", 90_000),
]


def main() -> None:
    client = TestClient(app)
    results = []
    for query, district_hint, sector, capital in CASES:
        matches = client.get("/localities/search", params={"q": query, "limit": 100}).json()
        match = next(
            (row for row in matches if district_hint.casefold() in row["district"].casefold()),
            matches[0] if matches else None,
        )
        if match is None:
            results.append({"query": query, "sector": sector, "error": "LOCALITY_NOT_FOUND"})
            continue
        response = client.post(
            "/analyze",
            json={
                "geo_id": match["geo_id"],
                "capital": capital,
                "business_category": sector,
                "language": "en",
            },
        )
        payload = response.json()
        selected = payload.get("selected_venture")
        twin = payload.get("digital_twin")
        results.append(
            {
                "query": query,
                "resolved_locality": match["locality"],
                "district": match["district"],
                "locality_type": match["locality_type"],
                "sector": sector,
                "capital_inr": capital,
                "http_status": response.status_code,
                "decision_status": payload.get("status"),
                "confidence": payload.get("confidence"),
                "estimate_status": (payload.get("demand") or {}).get("status"),
                "selected_candidate": selected.get("candidate_id") if selected else None,
                "project_cost_inr": selected.get("investment") if selected else None,
                "operating_break_even_month": (twin or {}).get("operating_break_even_month"),
                "investment_payback_month": (twin or {}).get("investment_payback_month"),
                "minimum_cash_inr": (twin or {}).get("minimum_cash"),
                "blocking_gates": [
                    gate["code"] for gate in payload.get("evidence_gates", []) if gate["blocking"]
                ],
                "methodology_version": payload.get("methodology_version"),
            }
        )
    output = Path("outputs/e2e/product_e2e_v0.4.0.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))
    if not all(
        item.get("selected_candidate") and item.get("http_status") == 200 for item in results
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

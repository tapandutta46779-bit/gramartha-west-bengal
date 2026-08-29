from __future__ import annotations

import json
import os
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from backend.api.contracts import AnalyzeRequest
from backend.evidence.store import EvidenceStore
from backend.service import analyze

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS"
CASES = [
    "CENSUS2011:19:801742",  # Kolkata
    "DS057:WB:RURAL:700ec711da5b",  # North 24 Parganas
    "DS057:WB:RURAL:65ad13d15ca9",  # South 24 Parganas
    "DS057:WB:RURAL:49df4b7f8b8a",  # Darjeeling
    "DS057:WB:RURAL:0f39088685b4",  # Jalpaiguri
    "DS057:WB:RURAL:f1e722937f0d",  # Maldah
    "DS057:WB:RURAL:921de164b677",  # Purulia
]


def run() -> dict:
    os.environ["SIH26091_OSM_SQLITE_PATH"] = str(ROOT / "data/west_bengal_osm.sqlite")
    store = EvidenceStore(ROOT / "data/sih26091_phase2.sqlite")
    results = []
    for geo_id in CASES:
        decision = analyze(
            AnalyzeRequest(
                geo_id=geo_id,
                capital=500_000,
                business_category="dairy",
                catchment_radius_km=5,
            ),
            store,
        )
        freshness = Counter(item.freshness_status.value for item in decision.evidence)
        results.append(
            {
                "geo_id": geo_id,
                "district": decision.geography.district if decision.geography else None,
                "locality": decision.geography.locality if decision.geography else None,
                "resolution": (
                    decision.geo_resolution.resolution_method.value
                    if decision.geo_resolution
                    else None
                ),
                "status": decision.status.value,
                "confidence": decision.confidence.value,
                "evidence_records": len(decision.evidence),
                "regional_survey_priors": sum(
                    item.source_id.startswith(("HCES", "ASUSE")) for item in decision.evidence
                ),
                "freshness_counts": dict(freshness),
                "demand_status": decision.demand.status if decision.demand else None,
                "graph_generated": decision.generated_graph is not None,
                "venture_selected": decision.selected_venture is not None,
                "catchment_entities": decision.catchment.get("entity_count"),
                "nearest_market_route_status": (
                    (decision.catchment.get("nearest_market_route") or {}).get("status")
                ),
                "blocking_gates": [gate.code.value for gate in decision.evidence_gates],
                "finance_screens": [
                    {
                        "scheme_id": item.scheme_id,
                        "eligible": item.eligible,
                        "freshness": item.freshness_status,
                        "effective_to": item.effective_to,
                    }
                    for item in decision.official_finance
                ],
            }
        )
    report = {
        "report_version": "wb-e2e-v2",
        "executed_at": datetime.now(UTC).isoformat(),
        "database": "data/sih26091_phase2.sqlite",
        "osm_database": "data/west_bengal_osm.sqlite",
        "cases": results,
        "truth_policy": (
            "No case may select a venture while current demand population, supply, price, "
            "capacity, route cost, venture cost or lender terms remain gated."
        ),
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "WEST_BENGAL_MULTI_DISTRICT_E2E.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    payload = run()
    print(
        json.dumps(
            [
                {
                    "district": item["district"],
                    "locality": item["locality"],
                    "status": item["status"],
                    "evidence": item["evidence_records"],
                    "catchment": item["catchment_entities"],
                }
                for item in payload["cases"]
            ],
            indent=2,
        )
    )

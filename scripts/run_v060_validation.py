from __future__ import annotations

import json
import os
import time
from datetime import UTC, datetime
from pathlib import Path

from backend.api.contracts import AnalyzeRequest
from backend.evidence.store import EvidenceStore
from backend.service import analyze

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs/e2e/v0.6.0"
CASES = [
    ("Kolkata", "Ward No.1", "kirana", {}),
    ("North 24 Parganas", "Abhirampur", "dairy", {}),
    ("Nadia", "Abhaynagar", "dairy", {"acceptable_debt": 0}),
    ("Darjeeling", "Abhiram", "dairy", {"mobility_km": 12}),
    ("Bankura", "Abantika", "dairy", {}),
    ("Purulia", "Akarbad", "food processing", {"assets": ["shop"]}),
    ("Malda", "Abhirampur", "fishery", {"assets": ["vehicle"]}),
    ("Purba Bardhaman", "Abhirampur", "mustard oil", {}),
    ("South 24 Parganas", "Abad Bhagabanpur", "transport", {}),
    ("North 24 Parganas", "Abhirampur", "kirana", {"minimum_monthly_income": 15000}),
    (
        "North 24 Parganas",
        "Abhirampur",
        "kirana",
        {"minimum_monthly_income": 1000000, "acceptable_debt": 0},
    ),
    (
        "North 24 Parganas",
        "Abhirampur",
        "transport",
        {"time_availability_hours_week": 10, "family_labour": 0},
    ),
]


def run() -> dict:
    os.environ["SIH26091_OSM_SQLITE_PATH"] = str(ROOT / "data/west_bengal_osm.sqlite")
    store = EvidenceStore(ROOT / "data/sih26091_phase2.sqlite")
    rows = []
    for index, (district, query, sector, profile) in enumerate(CASES, 1):
        matches = store.search_geographies(query, limit=1, district=district)
        if not matches:
            rows.append(
                {
                    "case": index,
                    "district": district,
                    "query": query,
                    "sector": sector,
                    "result": "LOCALITY_NOT_FOUND",
                }
            )
            continue
        geography = matches[0]
        started = time.perf_counter()
        decision = analyze(
            AnalyzeRequest(
                geo_id=geography.geo_id,
                capital=100_000,
                business_category=sector,
                analysis_mode="deep",
                catchment_radius_km=10,
                profile=profile,
            ),
            store,
        )
        elapsed = time.perf_counter() - started
        rows.append(
            {
                "case": index,
                "district": district,
                "locality": geography.locality,
                "geo_id": geography.geo_id,
                "sector": sector,
                "profile": profile,
                "status": decision.status.value,
                "selected_candidate": (
                    decision.selected_venture.candidate_id if decision.selected_venture else None
                ),
                "blocking_gates": [
                    gate.code.value for gate in decision.evidence_gates if gate.blocking
                ],
                "binding_constraints": decision.constraint_analysis.get("binding_constraints", []),
                "maximum_income_current_funding": decision.constraint_analysis.get(
                    "inverse_analysis", {}
                ).get("maximum_owner_income_with_current_funding"),
                "additional_own_capital_needed": decision.constraint_analysis.get(
                    "minimum_relaxation", {}
                ).get("additional_own_capital_needed"),
                "scenario_count": decision.robust_comparison.get("scenario_count", 0),
                "failure_boundary_count": len(decision.failure_boundaries),
                "sensitivity_count": len(decision.sensitivity_analysis),
                "runtime_seconds": elapsed,
            }
        )
    runtimes = [row["runtime_seconds"] for row in rows if "runtime_seconds" in row]
    report = {
        "version": "v0.6.0-validation-v1",
        "executed_at": datetime.now(UTC).isoformat(),
        "case_count": len(rows),
        "runtime": {
            "minimum_seconds": min(runtimes),
            "median_seconds": sorted(runtimes)[len(runtimes) // 2],
            "maximum_seconds": max(runtimes),
        },
        "cases": rows,
        "truth_policy": (
            "Conditional outputs are planning estimates. No case is interpreted as guaranteed "
            "income, observed complete locality demand, lender approval or calibrated success "
            "probability."
        ),
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "WEST_BENGAL_E2E_AND_PROFILE_VALIDATION.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# GramArtha v0.6.0 E2E and profile validation",
        "",
        f"Executed: {report['executed_at']}",
        "",
        "| Case | District / locality | Sector | Status | Selected | Runtime s |",
        "|---:|---|---|---|---|---:|",
    ]
    for row in rows:
        locality = row.get("locality") or row.get("query", "not found")
        lines.append(
            f"| {row['case']} | {row['district']} / {locality} | "
            f"{row['sector']} | {row.get('status', row.get('result'))} | "
            f"{'yes' if row.get('selected_candidate') else 'no'} | "
            f"{row.get('runtime_seconds', 0):.4f} |"
        )
    lines.extend(["", report["truth_policy"], ""])
    (OUTPUT / "WEST_BENGAL_E2E_AND_PROFILE_VALIDATION.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    return report


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))

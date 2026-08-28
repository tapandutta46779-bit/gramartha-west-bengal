from __future__ import annotations

import argparse
import json
import sqlite3
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "data/sih26091_phase2.sqlite"
OUTPUT = ROOT / "outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS"
AS_OF = date(2026, 8, 28)


DECISION_VARIABLES = [
    {
        "variable": "locality_population",
        "class": "STRUCTURAL_SLOW_CHANGING",
        "source": "Census 2011 PCA",
        "observation_date": "2011-03-01",
        "status": "HISTORICAL_BASELINE",
        "decision_use": "structure/baseline only; no 2026 projection loaded",
    },
    {
        "variable": "liquid_milk_consumption_rate",
        "class": "TIME_SENSITIVE_FAST_CHANGING",
        "source": "HCES 2023-24",
        "observation_date": "2023-08-01/2024-07-31 survey period",
        "status": "RECENT",
        "decision_use": "sampled district/sector prior, not exact locality demand",
    },
    {
        "variable": "enterprise_gva_assets_workers",
        "class": "TIME_SENSITIVE_FAST_CHANGING",
        "source": "ASUSE January-December 2025",
        "observation_date": "2025-01-01/2025-12-31 survey period",
        "status": "RECENT",
        "decision_use": "sampled district/sector/NIC prior, not incumbent capacity",
    },
    {
        "variable": "livestock_stock",
        "class": "TIME_SENSITIVE_FAST_CHANGING",
        "source": "20th Livestock Census",
        "observation_date": "2019",
        "status": "STALE_FOR_DECISION",
        "decision_use": "historical stock context only; cannot establish 2026 supply",
    },
    {
        "variable": "road_network",
        "class": "STRUCTURAL_SLOW_CHANGING",
        "source": "West Bengal OSM publisher extract",
        "observation_date": "publisher snapshot retrieved 2026-08-27",
        "status": "CURRENT",
        "decision_use": (
            "routing/catchment structure; completeness remains volunteered-data limited"
        ),
    },
    *[
        {
            "variable": variable,
            "class": "TIME_SENSITIVE_FAST_CHANGING",
            "source": None,
            "observation_date": None,
            "status": "UNKNOWN",
            "decision_use": "blocking gate; no current defensible value loaded",
        }
        for variable in (
            "milk_selling_price",
            "milk_procurement_price",
            "fuel_price",
            "transport_cost_per_litre",
            "incumbent_capacity",
            "venture_capex_opex",
            "local_wage",
            "commercial_rent",
            "weather_seasonality",
            "lender_interest_tenure_underwriting",
        )
    ],
    {
        "variable": "pmmy_scheme_categories",
        "class": "TIME_SENSITIVE_FAST_CHANGING",
        "source": "Department of Financial Services PMMY page",
        "observation_date": None,
        "effective_date": "Tarun Plus effective 2024-10-24; page updated 2026-02-05",
        "status": "CURRENT",
        "decision_use": "eligibility screening only; never lender approval",
    },
    {
        "variable": "ahidf_scheme_rules",
        "class": "TIME_SENSITIVE_FAST_CHANGING",
        "source": "DAHD AHIDF page and Department of Expenditure temporary extension",
        "observation_date": None,
        "effective_date": "2026-04-01 through 2026-09-30 or earlier superseding approval",
        "status": "CURRENT",
        "decision_use": (
            "conditional scheme-window screening; live portal and lender terms still required"
        ),
    },
]


def apply_database_labels(connection: sqlite3.Connection) -> dict[str, int]:
    as_of = AS_OF.isoformat()
    structural = connection.execute(
        """
        UPDATE evidence_record SET payload=json_set(
            payload,
            '$.data_change_class','STRUCTURAL_SLOW_CHANGING',
            '$.freshness_status','HISTORICAL_BASELINE',
            '$.freshness_as_of',?
        ) WHERE variable LIKE 'population_%' OR variable LIKE 'households_%'
        """,
        (as_of,),
    ).rowcount
    livestock = connection.execute(
        """
        UPDATE evidence_record SET payload=json_set(
            payload,
            '$.data_change_class','TIME_SENSITIVE_FAST_CHANGING',
            '$.freshness_status','STALE_FOR_DECISION',
            '$.freshness_as_of',?
        ) WHERE variable LIKE 'livestock_%'
        """,
        (as_of,),
    ).rowcount
    connection.commit()
    return {"structural_records_labelled": structural, "livestock_records_labelled": livestock}


def build_audit(*, apply: bool) -> dict:
    connection = sqlite3.connect(DATABASE)
    applied = apply_database_labels(connection) if apply else {}
    rows = connection.execute(
        "SELECT variable, json_extract(payload,'$.freshness_status'), count(*) "
        "FROM evidence_record GROUP BY variable, 2 ORDER BY variable"
    ).fetchall()
    regional_rows = connection.execute(
        "SELECT variable, json_extract(payload,'$.freshness_status'), count(*) "
        "FROM regional_prior GROUP BY variable, 2 ORDER BY variable"
    ).fetchall()
    counts = Counter()
    inventory = []
    for variable, freshness, count in rows:
        freshness = freshness or "UNKNOWN"
        counts[freshness] += count
        inventory.append({"variable": variable, "freshness_status": freshness, "records": count})
    regional_inventory = []
    for variable, freshness, count in regional_rows:
        freshness = freshness or "UNKNOWN"
        counts[freshness] += count
        regional_inventory.append(
            {"variable": variable, "freshness_status": freshness, "records": count}
        )
    connection.close()
    audit = {
        "audit_version": "data-freshness-v1",
        "as_of": AS_OF.isoformat(),
        "database": str(DATABASE.relative_to(ROOT)),
        "applied": applied,
        "database_freshness_counts": dict(counts),
        "database_variable_inventory": inventory,
        "regional_prior_inventory": regional_inventory,
        "decision_variable_audit": DECISION_VARIABLES,
        "projection_policy": (
            "No 2011 observation is relabelled as current. A 2026 population value requires an "
            "explicit base year, method, central/lower/upper estimate and uncertainty; none is "
            "currently loaded."
        ),
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "DATA_FRESHNESS_AUDIT.json").write_text(json.dumps(audit, indent=2) + "\n")
    lines = [
        "# SIH26091 Data Freshness Audit",
        "",
        f"As of: {AS_OF.isoformat()}",
        "",
        (
            "| Variable | Class | Source / version | Observation or effective date | "
            "Freshness | Decision use |"
        ),
        "|---|---|---|---|---|---|",
    ]
    for item in DECISION_VARIABLES:
        dates = item.get("observation_date") or item.get("effective_date") or "not available"
        lines.append(
            f"| {item['variable']} | {item['class']} | {item.get('source') or 'none'} | "
            f"{dates} | {item['status']} | {item['decision_use']} |"
        )
    lines.extend(["", audit["projection_policy"], ""])
    (OUTPUT / "DATA_FRESHNESS_AUDIT.md").write_text("\n".join(lines))
    return audit


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit and optionally label evidence freshness")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    result = build_audit(apply=args.apply)
    summary = {"counts": result["database_freshness_counts"], **result["applied"]}
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

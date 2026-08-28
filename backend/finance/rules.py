from __future__ import annotations

from backend.models.finance import SchemeEligibility

PMMY_SOURCE = "https://financialservices.gov.in/pradhan-mantri-mudra-yojana-pmmy"


def screen_pmmy(
    *, sector: str, requested_amount: float | None, previously_repaid_tarun: bool = False
) -> SchemeEligibility:
    amount = max(0.0, float(requested_amount)) if requested_amount is not None else None
    if amount is None:
        category = None
        maximum = 2_000_000.0
    elif amount <= 50_000:
        category = "Shishu"
        maximum = 50_000.0
    elif amount <= 500_000:
        category = "Kishore"
        maximum = 500_000.0
    elif amount <= 1_000_000:
        category = "Tarun"
        maximum = 1_000_000.0
    elif amount <= 2_000_000:
        category = "Tarun Plus"
        maximum = 2_000_000.0
    else:
        category = None
        maximum = 2_000_000.0
    eligible_sector = sector.casefold().strip() in {
        "dairy",
        "milk",
        "poultry",
        "fisheries",
        "kirana",
        "grocery",
        "transport",
        "food processing",
    }
    eligible = eligible_sector and amount <= maximum if amount is not None else None
    conditions = [
        "Income-generating micro-enterprise purpose must be accepted by the member lender.",
        "Term-loan and working-capital requirements are within PMMY purpose scope.",
    ]
    if category == "Tarun Plus":
        conditions.append(
            "Tarun Plus requires a previously availed and successfully repaid Tarun loan."
        )
        eligible = bool(eligible and previously_repaid_tarun)
    if amount is None:
        conditions.append("Project cost and requested finance are not yet established.")
    return SchemeEligibility(
        scheme_id="PMMY",
        scheme_name="Pradhan Mantri MUDRA Yojana",
        rule_version="DFS-PMMY-retrieved-2026-08-28",
        retrieved_at="2026-08-28T00:00:00+05:30",
        source_url=PMMY_SOURCE,
        category=category,
        eligible=eligible,
        maximum_loan_amount=maximum,
        interest_rate=None,
        tenure_months=None,
        collateral_required=False if eligible_sector else None,
        conditions=conditions,
        missing_for_financing=[
            *(["source-linked project cost and finance requirement"] if amount is None else []),
            "lender-specific interest rate",
            "lender-approved tenure and moratorium",
            "credit underwriting and actual sanction",
        ],
    )

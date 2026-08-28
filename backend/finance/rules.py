from __future__ import annotations

from backend.models.finance import SchemeEligibility

PMMY_SOURCE = "https://financialservices.gov.in/pradhan-mantri-mudra-yojana-pmmy"
AHIDF_SOURCE = "https://www.dahd.gov.in/schemes/programmes/ahidf"
AHIDF_EXTENSION_SOURCE = (
    "https://www.dahd.gov.in/sites/default/files/2026-07/TemporaryExtensionofSchemes.pdf"
)


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
        effective_from="2024-10-24",
        page_last_updated="2026-02-05",
        freshness_status="CURRENT",
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


def screen_ahidf(
    *, sector: str, requested_amount: float | None, organization_type: str | None = None
) -> SchemeEligibility:
    """Screen AHIDF rules without implying a lender sanction or universal borrower rate."""
    normalized_sector = sector.casefold().strip()
    normalized_org = (organization_type or "individual entrepreneur").casefold().strip()
    eligible_sector = normalized_sector in {
        "dairy",
        "milk",
        "dairy processing",
        "food processing",
        "meat processing",
        "animal feed",
        "breed improvement",
        "veterinary vaccine",
        "veterinary drugs",
        "animal waste",
        "wool processing",
    }
    eligible_org = normalized_org in {
        "individual",
        "individual entrepreneur",
        "private company",
        "msme",
        "fpo",
        "farmer producer organization",
        "section 8 company",
        "dairy cooperative",
    }
    amount = max(0.0, float(requested_amount)) if requested_amount is not None else None
    eligible = eligible_sector and eligible_org if amount is not None else None
    return SchemeEligibility(
        scheme_id="AHIDF",
        scheme_name="Animal Husbandry Infrastructure Development Fund",
        rule_version="DAHD-IDF-temporary-extension-2026-04-20",
        retrieved_at="2026-08-28T00:00:00+05:30",
        source_url=AHIDF_EXTENSION_SOURCE,
        effective_from="2026-04-01",
        effective_to="2026-09-30",
        page_last_updated="2026-08-28",
        freshness_status="CURRENT",
        category="Infrastructure Development Fund / AHIDF",
        eligible=eligible,
        maximum_loan_amount=None,
        interest_rate=None,
        tenure_months=None,
        collateral_required=None,
        interest_subvention_rate=0.03,
        maximum_project_finance_share=0.90,
        maximum_repayment_months=96,
        maximum_moratorium_months=24,
        status_wording=(
            "current rule-window eligibility screening through 2026-09-30; "
            "not lender approval or confirmation that the application window is "
            "accepting submissions"
        ),
        conditions=[
            "The temporary IDF continuation lasts through 2026-09-30 or an earlier "
            "superseding approval.",
            "The proposed activity must fall within an AHIDF infrastructure category.",
            "The lender may finance up to 90% of eligible project cost under its policy; "
            "this is not a guaranteed share.",
            "The 3% figure is interest subvention, not the borrower's final lending rate.",
        ],
        missing_for_financing=[
            *( ["source-linked project cost and finance requirement"] if amount is None else []),
            "live AHIDF portal application-window confirmation",
            "lender-specific gross and net interest rate",
            "eligible project-cost verification and borrower margin",
            "credit underwriting, security requirements and actual sanction",
        ],
    )

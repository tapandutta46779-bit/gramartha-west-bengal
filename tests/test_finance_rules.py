from backend.finance.rules import screen_ahidf, screen_pmmy


def test_pmmy_categories_and_tarun_plus_condition_are_not_approval() -> None:
    kishore = screen_pmmy(sector="dairy", requested_amount=100_000)
    assert kishore.category == "Kishore"
    assert kishore.eligible
    assert kishore.interest_rate is None
    assert "not lender approval" in kishore.status_wording

    tarun_plus = screen_pmmy(sector="dairy", requested_amount=1_500_000)
    assert tarun_plus.category == "Tarun Plus"
    assert not tarun_plus.eligible
    assert any("repaid" in condition for condition in tarun_plus.conditions)

    experienced = screen_pmmy(
        sector="dairy", requested_amount=1_500_000, previously_repaid_tarun=True
    )
    assert experienced.eligible

    unknown_need = screen_pmmy(sector="dairy", requested_amount=None)
    assert unknown_need.category is None
    assert unknown_need.eligible is None
    assert any("project cost" in item for item in unknown_need.missing_for_financing)


def test_ahidf_is_a_current_conditional_screen_not_a_promised_rate() -> None:
    screen = screen_ahidf(
        sector="dairy processing",
        requested_amount=1_500_000,
        organization_type="individual entrepreneur",
    )
    assert screen.eligible
    assert screen.effective_to == "2026-09-30"
    assert screen.freshness_status == "CURRENT"
    assert screen.interest_subvention_rate == 0.03
    assert screen.maximum_project_finance_share == 0.90
    assert screen.interest_rate is None
    assert "not lender approval" in screen.status_wording
    assert any("portal" in item for item in screen.missing_for_financing)

    unsupported = screen_ahidf(
        sector="kirana", requested_amount=500_000, organization_type="individual"
    )
    assert not unsupported.eligible

from backend.finance.rules import screen_pmmy


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

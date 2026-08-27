from __future__ import annotations

from pydantic import BaseModel, Field


class RobustSelectionResult(BaseModel):
    status: str
    selected_candidate_id: str | None
    maximum_regret: float | None
    candidate_regrets: dict[str, float] = Field(default_factory=dict)
    exact: bool = True
    objective: str = "minimize maximum regret over explicitly supplied scenarios"


def select_minimum_regret(
    scenario_values: dict[str, dict[str, float]],
    infeasible: set[tuple[str, str]] | None = None,
) -> RobustSelectionResult:
    """Select a candidate by exact minimax regret over a finite scenario table."""
    infeasible = infeasible or set()
    if not scenario_values:
        return RobustSelectionResult(
            status="INSUFFICIENT_SCENARIOS", selected_candidate_id=None, maximum_regret=None
        )
    candidates = sorted({candidate for values in scenario_values.values() for candidate in values})
    regrets: dict[str, float] = {}
    for candidate in candidates:
        candidate_regret = 0.0
        valid = True
        for scenario, values in scenario_values.items():
            feasible_values = {
                item: value for item, value in values.items() if (scenario, item) not in infeasible
            }
            if candidate not in feasible_values or not feasible_values:
                valid = False
                break
            candidate_regret = max(
                candidate_regret, max(feasible_values.values()) - values[candidate]
            )
        if valid:
            regrets[candidate] = candidate_regret
    if not regrets:
        return RobustSelectionResult(
            status="NO_CANDIDATE_FEASIBLE_IN_ALL_SCENARIOS",
            selected_candidate_id=None,
            maximum_regret=None,
        )
    selected = min(regrets, key=lambda candidate: (regrets[candidate], candidate))
    return RobustSelectionResult(
        status="MINIMAX_REGRET_OPTIMAL_OVER_SUPPLIED_TABLE",
        selected_candidate_id=selected,
        maximum_regret=regrets[selected],
        candidate_regrets=regrets,
    )

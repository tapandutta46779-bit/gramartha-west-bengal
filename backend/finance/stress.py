from __future__ import annotations

from collections.abc import Callable

from backend.models.finance import FailureBoundary, StressResult


def find_failure_boundary(
    variable: str,
    baseline_value: float,
    direction: str,
    step: float,
    evaluate: Callable[[float], bool],
    maximum_points: int = 100,
    criterion: str = "closing cash remains non-negative",
) -> FailureBoundary:
    if direction not in {"UP", "DOWN"} or step <= 0:
        raise ValueError("direction must be UP or DOWN and step must be positive")
    failure = None
    tested = 0
    for index in range(1, maximum_points + 1):
        candidate = baseline_value + (step * index if direction == "UP" else -step * index)
        if candidate < 0:
            candidate = 0.0
        tested += 1
        if not evaluate(candidate):
            failure = candidate
            break
        if direction == "DOWN" and candidate == 0:
            break
    return FailureBoundary(
        variable=variable,
        baseline_value=baseline_value,
        first_failure_value=failure,
        direction=direction,
        step=step,
        criterion=criterion,
        tested_points=tested,
    )


def summarize_stress(
    scenario_id: str,
    minimum_cash: float,
    default_month: int | None,
    boundaries: list[FailureBoundary],
) -> StressResult:
    return StressResult(
        scenario_id=scenario_id,
        survives=default_month is None,
        minimum_cash=minimum_cash,
        default_month=default_month,
        boundaries=boundaries,
    )

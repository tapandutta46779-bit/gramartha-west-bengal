# Minimum Viable Venture Algorithm

The current solver exhaustively evaluates every supplied/generated candidate, applies capital,
newly-served-demand and minimum-income constraints, runs the exact network counterfactual and
selects minimum investment with deterministic tie breaks. Its status is
`OPTIMAL_OVER_ENUMERATED_CANDIDATES` only. No global configuration or MILP optimality claim is made.


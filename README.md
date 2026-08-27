# SIH26091 Hyper-Local Economic Network Repair

Deterministic decision backend for evidence-backed rural micro-enterprise analysis in West Bengal.

The system separates four layers:

1. evidence and geographic identity;
2. transparent estimation with uncertainty;
3. economic graph, exact flow, bottleneck, counterfactual and Minimum Viable Venture search;
4. deterministic finance, monthly digital twin, stress boundaries, robust alternatives and multilingual explanation.

The LLM boundary is strict: AI may structure inputs and explain a frozen `VentureDecision`; it does not invent evidence, calculate finance, or silently choose a different venture.

Implementation status is tracked in `docs/IMPLEMENTATION_STATUS.md`. Data acquisition truth is separate from source catalogues: a URL is not an acquired dataset.

## Run locally

```sh
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/sih26091-ingest-livestock \
  outputs/SIH26091_KOLKATA_SOUTH_BENGAL/DS057_West_Bengal_Kolkata_South_Bengal_Livestock_Localities.xlsx \
  --sqlite data/sih26091.sqlite
SIH26091_SQLITE_PATH=data/sih26091.sqlite \
  .venv/bin/uvicorn backend.api.main:app --reload
```

Open `http://127.0.0.1:8000/ui/` for the evidence browser and
`http://127.0.0.1:8000/docs` for the API contract.

## Verify

```sh
.venv/bin/ruff check backend tests
.venv/bin/pytest
```

The current controlled suite covers exact allocation, bottleneck sensitivity, hidden connectors,
zero demand, counterfactual cannibalization, finite-candidate MVV optimality, amortization,
monthly cash flow, failure boundaries, minimax regret, evidence intervals, regional ingestion,
and the required API routes.

# SIH26091 Hyper-Local Economic Network Repair

Deterministic decision backend for evidence-backed micro-enterprise analysis across West Bengal.

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
  outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS/DS057_West_Bengal_All_Available_Livestock_Localities.xlsx \
  --sqlite data/sih26091_phase2.sqlite \
  --expected-sha256 c26a01f54c7c8107809905b921ac5c8a3a0a27d5c1defe03ce4286c900eb2255
SIH26091_SQLITE_PATH=data/sih26091_phase2.sqlite \
SIH26091_OSM_SQLITE_PATH=data/west_bengal_osm.sqlite \
  .venv/bin/uvicorn backend.api.main:app --reload
```

Open `http://127.0.0.1:8000/ui/` for the evidence browser and
`http://127.0.0.1:8000/docs` for the API contract.

## Verify

```sh
.venv/bin/ruff check backend scripts tests
.venv/bin/pytest
```

The ordinary `/analyze` request accepts location or `geo_id`, capital and sector. It automatically
resolves geography, retrieves evidence, builds spatial context, applies granular gates, and runs
the graph/flow/MVV/finance/twin layers only when their required inputs exist. It never converts
livestock stock, OSM counts, sampled priors or 2011 population into fabricated current values.

Reproducible acquisition and processing commands are documented in
`docs/DATA_ARCHITECTURE.md`; exact implementation boundaries are in
`docs/IMPLEMENTATION_STATUS.md`.

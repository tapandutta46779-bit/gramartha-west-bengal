# GramArtha v0.6.2 — West Bengal Hyper-Local Economic Network Repair

Deterministic decision backend for evidence-backed micro-enterprise analysis across West Bengal.

The system separates four layers:

1. evidence and geographic identity;
2. transparent estimation with uncertainty;
3. economic graph, exact flow, bottleneck, counterfactual and Minimum Viable Venture search;
4. deterministic finance, monthly digital twin, stress boundaries, robust alternatives and multilingual explanation.

The LLM boundary is strict: AI may structure inputs and explain a frozen `VentureDecision`; it does not invent evidence, calculate finance, or silently choose a different venture.

Implementation status is tracked in `docs/IMPLEMENTATION_STATUS.md`. Data acquisition truth is separate from source catalogues: a URL is not an acquired dataset.

## Run locally

On macOS, double-click **`Open GramArtha.command`**. It starts the required API with the
current GramArtha and West Bengal OSM databases and opens the correct served website. Do not open
`frontend/index.html` directly: a `file://` page cannot access the planning API.

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

The current product is visually identifiable by its seven stages: **Setup, Local market,
Opportunities, Risk, Plan, Finance and Action**. The v0.6.0 requirement audit is in
`docs/REQUIREMENT_AUDIT_V0.6.0.md`.

## Production deployment

`render.yaml` defines the permanent HTTPS web service and automatic deployment on commits. The
deployment assets in `deploy/assets/` are public-safe compressed runtime databases: they exclude
restricted respondent microdata, private fitted model artifacts and the full 511 MB road archive.
Run `bash deploy/start.sh` to reproduce the hosted runtime locally.

## Verify

```sh
.venv/bin/ruff check backend scripts tests deploy
.venv/bin/pytest
```

The ordinary `/analyze` request accepts location or `geo_id`, capital and sector. It automatically
resolves geography, retrieves evidence, builds spatial context, applies granular gates, and runs
the graph/flow/MVV/finance/twin layers only when their required inputs exist. It never converts
livestock stock, OSM counts, sampled priors or 2011 population into fabricated current values.

Reproducible acquisition and processing commands are documented in
`docs/DATA_ARCHITECTURE.md`; exact implementation boundaries are in
`docs/IMPLEMENTATION_STATUS.md`.

# Phase 2 Current-State Audit

Audit date: 2026-08-28 (Asia/Kolkata)

Baseline commit: `f834f99` (`Record verified Drive package objects`)

Baseline worktree: clean before Phase 2 changes.

Baseline verification:

- `ruff check backend tests`: passed.
- `pytest`: 14 passed; one upstream Starlette `httpx` deprecation warning.
- SQLite: 57,344,000 bytes; SHA-256
  `fab8ae185c19b55108eb3f31f0f1ae953c77a3f7ad7b66d573e24cfb115ab727`.
- SQLite rows: 9,163 geographic identities, 45,815 evidence records, zero analyses.
- West Bengal PBF: 113,098,966 bytes; SHA-256
  `b5b0c617e22d828954d8754c24aeb5b6440b483260bf040ef9cbbcdfd0e46cca`.
- The publisher companion MD5 conflict remains recorded; the PBF is not described as
  publisher-checksum verified.

## Subsystem classification

| Subsystem | Classification | Audit finding |
|---|---|---|
| Evidence types/provenance | EXISTING_AND_WORKING | Typed evidence, confidence, source references and quality flags persist in SQLite. |
| Regional livestock ingestion | EXISTING_AND_WORKING | Six-district workbook ingestion is checksum-gated and reproducible. It processes 18,326 sex-specific rows into 9,163 locality identities and 45,815 species totals. |
| All-West-Bengal livestock | MISSING | The regional workbook is deliberately filtered to six districts. The original national source is no longer local and must be reacquired to extract every available West Bengal row. |
| Geographic identity model | PARTIAL | Stores district/block/municipality/ward/PIN/coordinates/codes, but current records use DS057-derived IDs and lack an official LGD/Census crosswalk, coordinates and ambiguity-aware resolution. |
| Locality search | PARTIAL | Case-insensitive substring search works. It is not a resolver and cannot safely distinguish duplicate village names. |
| HCES | BLOCKED | No HCES microdata is present. Existing download scripts are catalogue download helpers, not an HCES transformation pipeline. Official microdata access may require registration/manual download. |
| ASUSE | BLOCKED | No ASUSE microdata or transform pipeline is present. |
| West Bengal OSM raw data | EXISTING_AND_WORKING | Regional PBF, polygon and verification metadata exist. |
| OSM extraction/routing/catchment | MISSING | No PBF parser, local POI/road extraction, spatial index, route engine or catchment service is connected. |
| Population/household foundation | MISSING | No Census/PCA locality population table or explicit projection model is ingested. |
| Infrastructure/facilities | MISSING | Mission Antyodaya, PMGSY, JJM, school and health layers are not integrated. |
| Price evidence | MISSING | No operational AGMARKNET/e-NAM/price ingestion or nearest-market distribution exists. |
| Transparent baseline | PARTIAL | Generic evidence-weighted envelope excludes synthetic evidence. It is not a sector demand, supply or price model. |
| ML/statistical models | BLOCKED | No defensibly labelled target is present. Correct fallback is transparent estimation plus `INSUFFICIENT_TRAINING_DATA`. |
| Economic graph model | EXISTING_AND_WORKING | Typed node/edge contracts and reference validation exist. |
| Automatic graph builder | MISSING | Ordinary analysis still requires the caller to supply `EconomicGraph`. |
| Exact flow solver | EXISTING_AND_WORKING | Successive shortest path lexicographically maximizes served demand then minimizes non-negative route cost. More conservation/multi-source tests and formal documentation are required. |
| Bottleneck engine | PARTIAL | Marginal edge-capacity relaxation works. Node, cost, storage, aggregation, concentration and fragility classes are absent. |
| Venture primitives | PARTIAL | Typed primitives exist, but candidate generation and a source-versioned cost library are absent. |
| Counterfactual/cannibalization | EXISTING_AND_WORKING | Candidate graph deltas trigger a full re-solve and distinguish newly served from displaced flow. Multi-path venture throughput semantics need further audit. |
| MVV enumerated oracle | EXISTING_AND_WORKING | Exact over the finite candidate list only. |
| MVV configuration/MILP | MISSING | No configuration variables, solver equivalence, pruning or digital-twin viability constraint. |
| Loan mathematics | EXISTING_AND_WORKING | Standard amortization works and real decisions reject unverified rules. |
| Official finance rules | BLOCKED | No current official, effective-date-versioned scheme dataset is loaded. No approval claim is made. |
| Digital twin | PARTIAL | Monthly operating cash is deterministic, but `break_even_month` conflates semantics and does not calculate investment payback, working-capital timing, principal/interest split or owner draw. |
| Stress | PARTIAL | Generic one-dimensional boundary helper exists; API currently tests only downward demand. |
| Robust selection | EXISTING_AND_WORKING | Exact finite-table minimax regret works; alternative objectives are absent. |
| Staged expansion | MISSING | Current stages are generic text, not computed configurations/triggers. |
| Canonical decision | PARTIAL | One object is persisted and consumed, but it lacks the full Phase 2 geography, demand/supply/price, catchment, graph summary, candidate set, finance, version and uncertainty fields. |
| API | PARTIAL | Seven routes exist and persist decisions. Normal `/analyze` still requires `geo_id` plus a supplied graph/candidates for non-refusal output. |
| Multilingual explanations | MISSING | English-only deterministic text. |
| Evidence-derived SWOT | MISSING | No structured SWOT generator. |
| UI | PARTIAL | Evidence search works, but the UI cannot submit the ordinary user analysis flow or display the full decision. |
| PostgreSQL/PostGIS | PARTIAL | Schema exists; no live migration/spatial integration test was run. |
| Reproducibility/versioning | PARTIAL | Method versions and evidence sources exist, but analyses do not yet capture complete dataset/model/finance/git versions. |
| Documentation/package | PARTIAL | Foundation status and a Drive package exist; the Phase 2 document set and final versioned package are incomplete. |

## Geographic baseline by district

| Source district label | Identities |
|---|---:|
| 24 Paraganas North | 2,236 |
| 24 Paraganas South | 2,230 |
| Hooghly | 2,207 |
| Howrah | 877 |
| Kolkata | 142 |
| Nadia | 1,471 |

The source spelling `Paraganas` is preserved. It is not silently rewritten to `Parganas`; aliases
and an official crosswalk must handle that relationship explicitly.

## Immediate implementation order

1. Reacquire and validate the full DS057 source, then ingest all available West Bengal coverage.
2. Add ambiguity-aware locality resolution and granular evidence gates.
3. Operationalize the regional PBF through bounded local extraction/catchment logic.
4. Introduce sector adapters, transparent demand/supply/price contracts and automatic graph build.
5. Generate evidence-gated ventures, strengthen finance/twin/stress, and extend the canonical API.
6. Expand real refusal-path tests, solver tests, performance benchmarks and documentation.

No working solver is scheduled for replacement without a confirmed correctness defect.

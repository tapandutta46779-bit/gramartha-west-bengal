# Implementation Status

Updated: 2026-08-28. Status values are `DONE`, `PARTIAL`, `BLOCKED`, `NOT_STARTED`.

| Component | Status | Verified state |
|---|---|---|
| Phase 2 audit | DONE | Baseline commit `f834f99`, original 14 tests and source/data state recorded in `PHASE2_CURRENT_STATE_AUDIT.md`. |
| All-WB livestock | DONE | 80,950 source rows, 40,475 DS057 identities, 202,375 observed species records, all 23 publisher district labels. |
| Census 2011 location codes | DONE | Official national LCD filtered to 41,154 WB rows; 31,747 DS057 identities reconciled and ambiguous names withheld. |
| Current LGD crosswalk | PARTIAL | Census codes and dataset/OSM IDs exist; current LGD village/PIN linkage remains unavailable in a captcha-free bulk path. |
| Census 2011 PCA | DONE | All 19 publisher district workbooks; 179,148 unique observed population/household/sex records. No current-year projection. |
| OSM extraction | DONE | 633,601 road ways, 17,212 POIs/places, R-tree indexes, radial catchment and local Dijkstra routing. |
| HCES 2022-23 / 2023-24 | BLOCKED | Layout/method files acquired; unit data require MoSPI login, email activation, application and data agreement. Tested importer is ready. |
| ASUSE 2023-24 | BLOCKED | Layout/readme acquired; unit data require MoSPI login/application. Tested weighted-prior importer is ready. |
| Demand engine | PARTIAL | Evidence interval contract and strict missing gate exist; HCES-derived locality priors are blocked on authenticated microdata. |
| Dairy supply engine | PARTIAL | Livestock stock is observed; conversion to productive/reachable milk supply is intentionally refused until sourced productive fraction/yield assumptions are loaded. |
| Price ingestion | NOT_STARTED | No verified local milk price distribution is loaded. |
| Competitor context | PARTIAL | Sector-specific OSM proxy counts and institutions are computed; incumbent capacity remains unknown. |
| Automatic graph | PARTIAL | Ordinary input invokes graph builder; a source-linked dairy graph is created only when demand, reachable supply, capacity and route-cost evidence all exist. |
| Exact flow / counterfactual | DONE | Maximum served demand then minimum economic cost; counterfactual and cannibalization retained. |
| Bottleneck | PARTIAL | Marginal edge-capacity sensitivity is exact under supplied graph; other requested bottleneck classes remain unimplemented. |
| Venture generation | PARTIAL | Dairy rented-transport primitive is automatically generated from four source-linked cost/capacity variables; broader library absent. |
| MVV | PARTIAL | Exact exhaustive oracle over enumerated candidates. Configuration MILP and pruning benchmarks are not implemented. |
| Official finance | PARTIAL | Current official PMMY category screening implemented; lender rate, tenure, underwriting and sanction remain unknown and are never called approved. |
| Digital twin | DONE | Operating break-even, cash break-even and owner-investment payback are distinct and unit-tested. |
| Stress / robustness | PARTIAL | Demand failure boundary and finite-table minimax regret work; expanded multi-shock engine is pending. |
| Canonical decision/API | DONE | Normal and advanced modes, granular gates, data/model/software versions, spatial context and persisted analysis. |
| Bengali/Hindi/English | DONE | Deterministic templates; calculations remain frozen. |
| Functional UI | DONE | Locality search, capital, sector, radius, language, decision gates, spatial/finance/source display. |
| ML | BLOCKED | No defensible labelled target; transparent baseline and `INSUFFICIENT_TRAINING_DATA` policy retained. |
| PostgreSQL/PostGIS runtime test | BLOCKED | Schema exists; no configured local/container PostGIS instance has been verified. |

The project does **not** yet produce a real venture recommendation for ordinary localities. It
correctly returns exact gates—typically demand, productive/reachable supply, price, incumbent
capacity, route cost, venture cost and lender-specific finance terms—while still returning the
evidence, Census/OSM context and audit trail it can defend.

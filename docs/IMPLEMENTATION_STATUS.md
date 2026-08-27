# Implementation Status

Updated: 2026-08-27

Status values: `DONE`, `PARTIAL`, `BLOCKED`, `NOT_STARTED`.

| Component | Status | Files / tests | Data / limitation |
|---|---|---|---|
| Specification review | DONE | Two pasted prompts; 12-page architecture PDF; 5-page data PDF read and visually checked | PDFs treated as reference specifications; official vs proposed content distinguished. |
| Repository audit | DONE | `docs/EXISTING_REPOSITORY_AUDIT.md` | Workspace has research artifacts but no pre-existing application code. |
| Dataset catalogue | PARTIAL | `outputs/SIH26091_data_foundation/` | 100 sources catalogued; most raw datasets are not acquired. Stale DS058/DS097 storage rows corrected after cleanup. |
| West Bengal regional data | PARTIAL | Verified livestock XLSX, two MSME PDFs, West Bengal OSM PBF | OSM size and repeat-download hash agree, but publisher MD5 conflicts and is explicitly flagged. HCES/ASUSE still require acquisition. |
| Database / migrations | DONE | `database/schema.sql`; `backend/evidence/store.py`; `data/sih26091.sqlite` | PostGIS production schema plus SQLite prototype store. SQLite: 9,163 localities and 45,815 evidence records. |
| Evidence/domain models | DONE | `backend/models/`; adapter and tests | Observed/sampled/estimated/inferred/modelled/synthetic types and source metadata preserved. |
| Geographic crosswalk | PARTIAL | DS057 adapter creates deterministic dataset-scoped IDs | No claim that generated IDs are official LGD/Census codes; full verified WB LGD/Census crosswalk still absent. |
| Demand/supply/price baselines | PARTIAL | `backend/learning/baselines.py` | Evidence-weighted envelope implemented and synthetic-only input refused; sector-specific training/calibration pending. |
| ML models | BLOCKED | Transparent baseline is active | No defensible labelled training tables yet; no fake trained model shipped. |
| Catchment / graph builder | PARTIAL | Verified regional PBF and graph contracts | OSM routing/catchment extraction is not yet connected to the economic graph builder. |
| Exact flow engine | DONE | `backend/engine/flow_engine.py`; controlled tests | Successive shortest-path maximum-served/minimum-cost allocation, exact under the supplied finite model. |
| Bottleneck engine | DONE | `backend/engine/bottleneck.py`; sensitivity test | Marginal capacity relaxation reruns exact allocation. |
| Venture primitives | PARTIAL | `backend/models/venture.py` | Typed primitives implemented; real costs/capacities still require sourced or labelled inputs. |
| Counterfactual engine | DONE | `backend/engine/counterfactual.py`; cannibalization test | Recomputes allocation after network delta and separates newly served from displaced flow. |
| MVV exhaustive oracle / search | DONE | `backend/engine/mvv.py`; exact finite-set test | Exact only over enumerated candidates; no global optimality claim. |
| Official finance calculator | BLOCKED | — | Current official rules/effective dates not yet verified. |
| Financial optimizer | PARTIAL | `backend/finance/calculator.py` | Deterministic amortization works; prudent-vs-legal optimizer awaits verified scheme rules and household buffers. |
| 36-month digital twin | DONE | `backend/finance/digital_twin.py`; hand-calculated test | Monthly revenue, costs, debt, cash, DSCR, break-even and default month. |
| Stress / failure boundaries | DONE | `backend/finance/stress.py`; API and test | Returns first measured failure value at explicit step resolution. |
| Robust selection / staged expansion | PARTIAL | `backend/engine/robust.py`; canonical staged-plan output | Exact finite-scenario minimax regret implemented; expansion triggers require real operating evidence. |
| Canonical VentureDecision | DONE | `backend/models/decision.py`; `backend/service.py` | API, persistence and UI consume the same object; browser performs no financial arithmetic. |
| API | DONE | `backend/api/`; API tests | All required endpoints exist; stress endpoint currently varies the monthly-demand boundary. |
| Browser interface | DONE | `frontend/`; live DB smoke test | Evidence browser served at `/ui/`; intentionally refuses to imply livestock counts alone justify a venture. |
| Multilingual explanation | NOT_STARTED | English deterministic text only | Bengali/Hindi deterministic templates remain to implement. |
| End-to-end West Bengal cases | PARTIAL | Real DS057 ingestion and locality/evidence API smoke case | Complete venture decisions remain blocked by demand, price, incumbent, route-cost and verified finance evidence. |
| Automated test suite | PARTIAL | 14 passing tests | Core controlled and ingestion/API cases pass; scale, property-based, PostgreSQL and full real-decision E2E coverage remain. |

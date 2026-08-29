# GramArtha v0.6.0 Requirement-by-Requirement Audit

Audit date: 2026-08-29. This document maps the actionable families in the final GramArtha
completion specification to implementation and verification evidence. `VERIFIED` means exercised
against real repository data or HTTP behavior. `PARTIAL` means useful work exists but the full
claim is not defensible. `BLOCKED` identifies the concrete external evidence or authorization gate.

| Requirement | Status | Implementation and verification evidence |
|---|---|---|
| Preserve the verified project; do not restart | VERIFIED | v0.6.0 extends commit `a1349d8`; prior versioned reports remain intact. |
| Current 23-district West Bengal product geography | VERIFIED | `current_geo_entity`: 23 districts, 474 subordinate entities and 40,474 localities. All 23 district search checks passed. |
| Separate current and historical geography | VERIFIED | Distinct current, historical and crosswalk tables/models; Census observations retain 2011. |
| Reorganization-safe crosswalk | VERIFIED/PARTIAL | 6,506 exact and 4,641 district-context links; 1,915 unsafe split-era rows deliberately remain unmapped. |
| Official LGD completeness | BLOCKED | LGD download is CAPTCHA-gated. The product layer is therefore labelled DS057-derived, never official-complete LGD. |
| Hierarchy, duplicates, containment and leakage audit | VERIFIED | Zero orphan nodes, wrong-parent districts, same-parent duplicate IDs or cross-district source leakage. |
| Locality search and disambiguation | VERIFIED | District-scoped exact/alias/prefix/token ranking, locality type and parent display tested in browser. |
| Observation/effective/retrieval dates and freshness labels | VERIFIED | Evidence records preserve dates, units, status and CURRENT/RECENT/HISTORICAL_BASELINE/PROJECTED/STALE/UNKNOWN labels. |
| Census observations never labelled current | VERIFIED | 2011 PCA is `HISTORICAL_BASELINE`; 2026 population is an explicit scenario projection with base year and bounds. |
| Current dynamic evidence must not be fabricated | VERIFIED | Current local price, rent, wage, lender quote, incumbent capacity and market share gaps remain visible gates/limitations. |
| HCES 2022-23 and 2023-24 processing | VERIFIED | Restricted archives integrity checked; district/rural-urban weighted priors produced. Raw respondent files remain private. |
| ASUSE 2023-24 and 2025 processing | VERIFIED | Latest 38,626 usable West Bengal enterprise rows and district/NIC priors integrated. |
| Actual statistical/ML training | VERIFIED | HCES RF/ridge/baseline on 18,120 rows; ASUSE RF/ridge/baseline on 38,626 rows; 23 geographic holdouts each. |
| Save fitted artifacts and model registry | VERIFIED | Private joblib artifacts, SHA-256 values, training metadata and holdout folds recorded in `model_registry.json`. |
| Honest production model selection | VERIFIED | Direct weighted survey estimators are used because ordinary locality requests lack respondent microfeatures; ML is not falsely invoked. |
| Demand, supply, price and capacity | VERIFIED/PARTIAL | Explicit intervals/status/methods. Generic sectors are benchmark models. Dairy uses HCES rate, population scenario and official district production; current local quotes remain gates. |
| Current official dairy production evidence | VERIFIED | WB ARD 2024-25 district PDF retained with exact source, size and SHA-256; all 23 district totals ingested. |
| Factor registry across sectors | VERIFIED | Typed factors cover dairy, poultry, fish, kirana, processing, flour, spice, oil, electronics, household and rural distribution. |
| Customers, suppliers and channels | VERIFIED | Per-sector structured groups/channels and local institution/market candidates appear in API, UI and PDF. |
| Competitor analysis | VERIFIED/PARTIAL | Direct/indirect OSM candidates, distance, count and proxy intensity are computed; real capacity, turnover, share and HHI remain unknown. |
| Catchment and routing | VERIFIED/PARTIAL | Full local build uses statewide OSM POIs and road routing; public runtime retains POIs and straight-line fallback but omits the 511 MB road archive. |
| Economic graph and flow | VERIFIED | Ordinary pipeline constructs graph inputs and runs exact min-cost maximum flow for supplied/modelled evidence. |
| Bottleneck and counterfactual | VERIFIED | Marginal capacity repair, newly served flow and displaced incumbent flow are separated and tested. |
| Automatic venture generation | VERIFIED | Sector adapters automatically enumerate five scale/configuration candidates from locality evidence and profile constraints. |
| Minimum Viable Venture oracle | VERIFIED | Exact exhaustive choice over the enumerated library; no general MILP claim. |
| Entrepreneur profile and null semantics | VERIFIED | Blank optional values remain null; debt is a ceiling; absent debt is conservatively zero. |
| Inverse optimization | VERIFIED | Maximum income at current funding, minimum own capital/debt for target and minimum constraint relaxation are returned. |
| Time, labour, mobility, skills and assets | VERIFIED/PARTIAL | Time, family labour, mobility and declared assets affect selection; skill suitability remains rule-based, not credential verification. |
| CAPEX, OPEX and working capital | VERIFIED | Structured breakdowns, cash-conversion assumptions, reserve guidance and cash buffer are exposed. |
| Finance and accounting | VERIFIED | 36-month monthly cash flow, contribution, operating break-even, payback, NPV/IRR and loan schedule remain distinct. |
| Current scheme screening | VERIFIED/PARTIAL | PMMY effective 2024-10-24/page 2026-02-05 and AHIDF extension 2026-04-01 to 2026-09-30 are encoded; lender rate/sanction and live portal status remain unknown. |
| Uncertainty propagation | VERIFIED | 512 deterministic triangular joint scenarios, VaR/CVaR, regret, Pareto selection and adaptive failure boundaries. |
| Sensitivity and stop rules | VERIFIED | Controlled ±5% elasticities plus adaptive downside/upside boundaries; missing/undefined elasticity is handled honestly. |
| Cannibalization and robustness | VERIFIED | Existing and new flow are separated; robust alternative ordering uses the exact scenario table. |
| SWOT and pre-mortem | VERIFIED | Computed business-economic SWOT and ranked failure causes/prevention, not static filler. |
| Seven-stage current UI | VERIFIED | Current GramArtha UI shows Setup, Local market, Opportunities, Risk, Plan, Finance and Action. |
| Visual market/price/risk summaries | VERIFIED | Demand/supply bars, price intervals, sensitivity tornado and structured competitor/channel/plan cards. |
| Analysis-specific customer PDF | VERIFIED | HTTP endpoint generated a valid 9-page A4 plan from a real deep dairy analysis. |
| 35-60 page master technical PDF | VERIFIED | v0.6.0 report is 41 rendered A4 pages; every page was visually checked for clipping/overlap. |
| Multi-district E2E including outside South Bengal | VERIFIED | 12 cases cover Kolkata, North/South 24 Parganas, Nadia, Darjeeling, Bankura, Purulia, Malda and Purba Bardhaman. |
| Honest refusal/evidence gates | VERIFIED | Bankura dairy and high-income profile cases return `NOT_FEASIBLE`; absent Malda locality returns `LOCALITY_NOT_FOUND`. |
| Local HTTP browser flow | VERIFIED | Current v0.6.0 GramArtha locality search and 512-scenario Abhirampur dairy result completed with zero console warnings/errors. |
| Deployment-size public runtime | VERIFIED | Clean runtime assets are 28,423,182 and 1,546,474 compressed bytes; fresh decompression, analysis and PDF tests passed. |
| Permanent public HTTPS and automatic updates | USER ACTION REQUIRED | Render GitHub authorization/service creation is an external account action. The repository and auto-deploy Blueprint are prepared; public verification must follow authorization. |
| Full automated suite | VERIFIED | Ruff, 55 pytest tests, JavaScript syntax, diff whitespace and both SQLite integrity checks pass. |
| Public-safe package | VERIFIED | Restricted respondent microdata and private fitted artifacts excluded; operational databases, code, reports and verification evidence included. |
| Shareable Drive delivery | PARTIAL | v0.6.0 package/PDF copy and byte/checksum verification are required after final packaging; public Drive permission state must be separately verified. |

## Non-negotiable claim boundaries

- A conditional scenario is not guaranteed income, calibrated business survival or lender approval.
- HCES/ASUSE support regional estimators, not exact village demand.
- Statewide geography is not statewide economic completeness.
- OSM is volunteered proxy evidence; a missing POI is not proof that no competitor exists.
- 2011 population and 2019 livestock observations are historical; current prices and supplier
  terms require a fresh local quote before investment.
- The public runtime contains derived regional priors, not restricted respondent-level files or
  private fitted model artifacts.

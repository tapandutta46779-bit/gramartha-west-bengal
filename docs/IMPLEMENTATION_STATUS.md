# Implementation Status

Updated: 2026-08-28. Product version: 0.5.0 / decision methodology v5.

| Component | Status | Verified state |
|---|---|---|
| West Bengal identity/evidence store | DONE | 53,537 geographic identities, 381,523 locality evidence records and 976 regional survey priors; SQLite integrity passes. |
| Census geography/PCA | DONE AS HISTORICAL BASELINE | Official Census 2011 codes and observations are never labelled current. When needed, v0.5 uses an explicit low-confidence 2026 rural/urban scenario projection with base year, rates and bounds. |
| Livestock | DONE AS HISTORICAL CONTEXT | 202,375 West Bengal species records from the 2019 livestock census; all labelled `STALE_FOR_DECISION`. |
| OSM spatial layer | DONE WITH PROXY CAVEAT | State extract, 633,601 road ways, 17,212 POIs/places, catchment and local routing; volunteered completeness caveat retained. |
| HCES processing | DONE | Restricted 2022-23 and 2023-24 archives integrity-tested; 18,136 and 18,120 West Bengal household samples transformed into zero-inclusive weighted milk priors. |
| ASUSE processing | DONE | Restricted 2023-24 and calendar-2025 archives integrity-tested; latest 39,029 West Bengal enterprise sample transformed into 1,558 district/sector/NIC2 prior groups. |
| Statistical/ML training | DONE | HCES 18,120 rows and ASUSE 38,626 rows; district-group holdout, baselines, ridge and random forest; fitted private artifacts, registry and real MAE/RMSE/calibration metrics saved. |
| Production survey integration | DONE | Ordinary requests automatically receive applicable district/sector HCES and ASUSE priors. Direct survey estimators are used because ordinary requests lack the microfeatures required by fitted models. |
| Data-freshness policy | DONE | Variable class, observation/effective date and explicit freshness labels are stored; stale/unknown dynamic values cannot unlock the graph or recommendation. |
| Demand | MODELLED / GATED BY PATH | Generic adapters use low-confidence ASUSE planning envelopes. Dairy may use HCES rate times an explicit population scenario but still requires current physical/price evidence. No exact village demand is claimed. |
| Supply / price / capacity / cost | GATED | No fabricated current value. Productive reachable supply, local price, incumbent capacity, route cost and source-linked venture costs are required. |
| Graph / exact flow / bottleneck | DONE WHEN INPUTS EXIST | Automatic dairy graph is built only with decision-ready variables; min-cost maximum flow and marginal edge-capacity bottleneck ranking are exact for the supplied graph. |
| Counterfactual / cannibalization | DONE | Baseline, newly served demand, venture flow and displaced incumbent flow are separated. |
| Venture generation / MVV | DONE FOR ENUMERATED LIBRARY | Ten generic sector adapters plus a separately gated dairy path. Starter/growth configurations carry operational and cash-conversion fields. Selection is exact only over the enumerated set; no general configuration MILP is claimed. |
| Finance | CURRENT SCREENING, REAL TERMS GATED | PMMY page updated 2026-02-05 and AHIDF temporary extension through 2026-09-30 are screened. Lender rates, underwriting, margin, portal window and sanction remain unknown. |
| Digital twin / stress / robustness | DONE FOR SUPPLIED ASSUMPTIONS | 36-month accounting, distinct break-even/payback, 512 seeded triangular joint scenarios, survival/payback rates, VaR/CVaR, Pareto filtering, exact scenario-table regret and numerical failure boundaries are tested. Scenario probabilities are not empirically calibrated. |
| Real West Bengal E2E | DONE | Seven diverse deep E2E cases return conditional benchmark plans. A 23-district smoke run returns HTTP 200 everywhere, with 22 conditional plans and one safe historical-boundary evidence gate. |
| HTTP/browser UI | DONE LOCALLY | Seven-step local UI, DB district dropdown, scoped search, ten-adapter comparison and result tabs tested over HTTP in Chromium; zero console warnings/errors. Public Netlify deployment is not claimed. |
| Test/audit/package | DONE | Ruff, 50 pytest tests, JavaScript syntax, deep E2E, all-district smoke, 31-page rendered PDF QA, and a versioned public-safe package. |

The strongest honest product is an operational local advisory and decision engine. Generic outputs
remain low-confidence `MODELLED_BENCHMARK` planning cases, not present-day village observations,
statewide economic completeness, empirical survival probabilities, or lender-approved investments.

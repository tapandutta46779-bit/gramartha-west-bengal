# Implementation Status

**Updated:** 2026-09-01  
**Current product version:** v0.7.2  
**Decision methodology:** evidence-backed economic-network repair with explicit AI containment

This is the current-status document. Older versioned audit reports remain in `docs/` for traceability and are indexed separately by [`docs/README.md`](README.md).

| Component | Status | Current verified / documented state |
|---|---|---|
| West Bengal identity/evidence store | DONE | **53,537** geographic identities, **381,523** locality evidence records and **976** regional survey priors in the audited implementation snapshot; deployment/runtime SQLite integrity is checked in CI. |
| Census geography/PCA | DONE AS HISTORICAL BASELINE | Official Census 2011 codes and observations are never labelled current. Scenario projections retain explicit base year, assumptions and confidence rather than being presented as observed 2026 village facts. |
| Livestock | DONE AS HISTORICAL CONTEXT | 202,375 West Bengal species records from the 2019 livestock census are retained as historical context and must not silently become current decision evidence. |
| OSM spatial layer | DONE WITH PROXY CAVEAT | State-scale OSM-derived road/POI context, catchment and local routing are implemented; volunteered-data completeness caveats remain explicit. The public runtime uses a prepared OSM SQLite asset. |
| HCES processing | DONE / RESTRICTED SOURCE BOUNDARY | Restricted 2022-23 and 2023-24 archives were integrity-tested and transformed into regional priors. Respondent microdata are not redistributed in the public release. |
| ASUSE processing | DONE / RESTRICTED SOURCE BOUNDARY | Restricted enterprise survey archives were integrity-tested and transformed into district/sector/NIC2 priors. Respondent microdata are not redistributed in the public release. |
| Statistical/ML training | DONE AS VALIDATION/RESEARCH LAYER | HCES/ASUSE training pipelines include baselines, ridge and random-forest models with geographic/group holdout evaluation and saved metrics/artifact registries. |
| Production survey integration | DONE WITH EXPLICIT MODEL BOUNDARY | Ordinary requests receive applicable regional survey priors. Direct survey estimators are used where ordinary requests lack the microfeatures required by fitted models; the production decision path does not pretend unavailable features exist. |
| Data-freshness policy | DONE | Variable class, observation/effective date and explicit freshness/confidence states are stored; stale or missing decision-critical values cannot silently become precise current evidence. |
| Demand | MODELLED / PATH-GATED | Generic adapters may use low-confidence planning envelopes. Sector-specific paths may combine historical/statistical priors with explicit scenario assumptions, but exact present-day village demand is not claimed without supporting evidence. |
| Supply / price / capacity / cost | GATED | No fabricated current value. Decision-ready paths require sufficient reachable supply, price/capacity/cost and source-linked assumptions according to the relevant adapter. |
| Graph / exact flow / bottleneck | DONE WHEN INPUTS EXIST | Economic graph construction, min-cost/max-flow mechanics, residual demand and structural bottleneck ranking are implemented for supplied decision-ready inputs. |
| Counterfactual / cannibalization | DONE | Baseline flow, newly served demand, venture flow and displaced incumbent flow are separated during repair analysis. |
| Venture generation / MVV | DONE FOR ENUMERATED LIBRARY | Generic sector adapters plus separately gated sector paths generate bounded venture configurations. Selection is exact over the enumerated candidate space; no general-purpose optimizer over every imaginable business configuration is claimed. |
| Finance | DONE WITH REAL-WORLD TERMS GATED | Scheme screening, loan arithmetic, break-even/payback and working-capital logic are implemented. Lender-specific underwriting, sanction, live portal availability and unknown commercial terms remain outside the deterministic claim. |
| Digital twin / stress / robustness | DONE FOR SUPPLIED ASSUMPTIONS | **36-month** monthly accounting, working-capital gaps, **512 deterministic seeded joint scenarios**, survival/payback summaries, VaR/CVaR, Pareto filtering, regret-based comparison and numerical failure boundaries are implemented/tested. Scenario probabilities are not claimed to be empirically calibrated. |
| AI boundary | DONE / ARCHITECTURAL CONSTRAINT | Language AI may structure intake or explain a frozen result. It must not invent evidence, perform hidden finance, silently replace the selected venture, or convert weak evidence into certainty. The core decision path remains evidence + explicit mathematics/rules. |
| Real West Bengal E2E | DONE / VERSIONED EVIDENCE | Versioned deep E2E and district smoke evidence is retained under `outputs/` and historical audit documents. The project preserves safe gating/qualification when current decision evidence is insufficient. |
| HTTP/browser UI | DONE + PUBLICLY HOSTED | Seven-stage browser product is implemented. Historical Chromium QA covers search, locality/evidence flows, analysis/result tabs and multilingual output. The current public product is linked from the README at `https://gramartha-west-bengal.onrender.com/ui/`. CI smoke-tests the reconstructed local runtime; it does not claim external-host uptime monitoring. |
| Multilingual output / PDF | DONE | English, Bengali and Hindi presentation/reporting are implemented, with versioned rendered/PDF QA artifacts retained under `output/validation/` and `output/pdf/`. |
| Test / CI quality | DONE | **68/68 tests passing** on the measured v0.7.2 baseline; **81.6% backend line coverage**, **61.4% branch coverage**, and a **75% minimum combined coverage gate**. CI also runs Ruff, Python compilation, frontend JS syntax, SQLite integrity, API health and repository-link/hygiene checks. |
| Security automation | DONE | CodeQL for Python/JavaScript, pip-audit, Bandit and Gitleaks are configured; dependency auditing is separated from normal CI. |
| Software release | DONE | `v0.7.2` is published as a verified software release with `GramArtha-v0.7.2-Judge-Package.zip`, public-runtime archive, wheel, source distribution, CycloneDX SBOM, release manifest and SHA-256 checksums. Platform launchers are included for macOS, Linux and Windows. |

## Strongest honest product claim

GramArtha is an operational **hyper-local business feasibility and financial-structuring decision-support system** whose distinguishing core is economic-network repair rather than one-shot text generation.

Its strongest claims are the implemented evidence/provenance layer, economic graph and flow/bottleneck logic, counterfactual/MVV search over an explicit candidate library, 36-month finance, deterministic stress/robustness analysis, multilingual product/reporting layer and auditable AI boundary.

## Boundaries that remain intentional

Generic outputs may still contain low-confidence `MODELLED_BENCHMARK` planning cases. GramArtha does **not** claim complete present-day village observations statewide, empirically calibrated survival probabilities, an unrestricted global venture optimizer, lender-approved investments, guaranteed business success, or that scheme eligibility equals sanction.

See [`LIMITATIONS.md`](LIMITATIONS.md), [`VALIDATION.md`](VALIDATION.md) and [`60_SECOND_JUDGE_VIEW.md`](60_SECOND_JUDGE_VIEW.md) for the shortest reviewer path.

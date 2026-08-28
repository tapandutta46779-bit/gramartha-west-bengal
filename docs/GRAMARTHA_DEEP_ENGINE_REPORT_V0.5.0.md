# GramArtha Deep Engine and Product Completion Report v0.5.0

Audit date: 2026-08-28 (Asia/Kolkata)

This report records the strongest honestly verified product at this checkpoint. It distinguishes observed data, historical baselines, projections, modelled benchmarks, and unknown current values. It does not claim an observed 2026 locality market, lender approval, guaranteed income, or a global optimum outside the enumerated venture configurations.

## 1. Executive outcome

GramArtha is now a working local web product and an evidence-aware analytical engine for West Bengal entrepreneurs. A user selects one of 23 database-supported district labels, searches only within that district, chooses a locality and catchment, optionally supplies an entrepreneur profile, and requests either a quick or deep analysis. The ordinary path can compare ten sector adapters, generate finite starter/growth venture configurations, calculate 36-month cash behavior, and explain opportunities, risks, financing, and next actions.

Deep mode adds 512 reproducible joint scenarios, survival and payback frequencies, downside cash, VaR/CVaR loss, Pareto filtering, exact regret over the simulated candidate table, numerical failure boundaries, and separate expected-value, survival-first, CVaR-aware, and minimax-regret winners. The selected output remains CONDITIONAL because its market envelope is a low-confidence benchmark derived from regional ASUSE priors rather than observed locality transactions.

Verified headline status:

- 50 automated Python tests pass; Ruff and JavaScript syntax checks pass.
- 23/23 district requests return HTTP 200; 22 produce conditional benchmark plans and one is safely gated.
- Seven diverse deep E2E cases run with 512 scenarios each.
- A real Chromium session completed the Kolkata best-opportunity flow with no console warning or error.
- The current public Netlify URL is not this local product and is not claimed as deployed.

## 2. User problem and decision contract

The product is designed for an ordinary entrepreneur who asks: what small venture might fit this place, my capital, and my risk tolerance; what would it cost; what could go wrong; and what should I verify before spending money? It is not a survey explorer or a raw model dashboard.

Every output follows an explicit contract. Historical evidence keeps its observation year. Modelled values are labelled MODELLED_BENCHMARK. Projected population retains base year, rate scenario, horizon, and uncertainty. Missing current evidence produces a caveat or evidence gate. Finance schemes are screens, not sanctions. Candidate selection is exact only over the configurations actually generated.

The response therefore separates four questions:

- Is the location identity and catchment technically resolved?
- Is there enough evidence to construct a planning benchmark?
- Which enumerated plan is most robust under stated shocks?
- What current facts must a person verify before committing money?

## 3. Product journey

The implemented browser journey is:

1. Area: West Bengal is fixed; district is loaded from the evidence database.
2. Locality: type-ahead is district-scoped and returns stable geographic identities.
3. Catchment: user selects 3, 5, 10, 15, or 20 km.
4. Profile: capital is required; income goal, debt ceiling, experience, skills, assets, and risk tolerance are optional.
5. Opportunity: choose a sector or ask GramArtha to compare the supported library.
6. Analysis: quick mode computes deterministic planning outputs; deep mode adds 512 uncertainty scenarios.
7. Decision: tabs present summary, local market, opportunities, risk and SWOT, business plan, finance, action plan, and technical evidence.

The UI intentionally leads with the business decision. Internal IDs, evidence-gate codes, formulas, and raw evidence remain available in a secondary disclosure instead of dominating the customer experience.

## 4. Verified statewide geographic coverage

| Layer | Verified extent | Interpretation |
|---|---:|---|
| Geographic identity store | 53,537 identities | West Bengal village, town, and ward identities from integrated official/proxy sources. |
| Census location directory | 41,154 WB rows | Official 2011 location codes; structural/historical use only. |
| Census PCA evidence | 179,148 records | Population, household and sex fields across 19 districts as defined in 2011. |
| Livestock identities | 40,475 localities | Publisher labels across 23 district groups. |
| Livestock species records | 202,375 | Historical 2019 stock context, not current productive supply. |
| OSM road ways | 633,601 | Statewide routing proxy. |
| OSM POIs/places | 17,212 | Volunteered facility/place proxy with completeness caveat. |
| OSM admin areas | 381 | Administrative proxy polygons/relations where present. |
| Survey district groups | 23 | HCES/ASUSE sampled regional priors, not exact locality observations. |

Statewide geographic coverage does not imply statewide economic completeness. District names also span historical and current publisher vocabularies. The all-district smoke test deliberately leaves undivided 2011 Barddhaman gated when a safe mapping to the current ASUSE prior cannot be established.

## 5. District-scoped locality resolution

The district dropdown is generated from the database rather than hard-coded in the browser. Search accepts a query, limit, and district filter. The evidence store normalizes the Bardhaman/Barddhaman spelling family for discovery while retaining distinct publisher identities where split-district semantics matter.

This design prevents a common failure: choosing a locality with the right name in the wrong district. The selected response returns stable geo_id, name, district, locality type, latitude/longitude where available, and evidence provenance. Search is a resolution layer, not proof that every identity has current economic evidence.

The 23-label smoke run produced HTTP 200 for every district. Twenty-two sample localities produced a conditional finite-set venture. Historical Barddhaman returned INSUFFICIENT_EVIDENCE with NO_DEMAND_EVIDENCE rather than borrowing a potentially wrong current district prior.

## 6. Data inventory and years

| Dataset | Observation/version | Freshness class | Decision use |
|---|---|---|---|
| Census geography/PCA | 2011 | HISTORICAL_BASELINE | Stable identity, settlement type, historical population anchor. |
| 20th Livestock Census | 2019 | STALE_FOR_DECISION | Historical species stock context only. |
| HCES comparison wave | 2022-23 | STALE_FOR_DECISION | Historical comparison. |
| HCES production wave | Aug 2023-Jul 2024 | RECENT | District/sector consumption rate prior. |
| ASUSE comparison wave | Oct 2023-Sep 2024 | historical comparison | Aggregate enterprise comparison. |
| ASUSE production wave | Jan-Dec 2025 | RECENT | District/sector/NIC2 enterprise benchmark. |
| BAHS | 2025 publication | RECENT state context | State-level yield context, not locality supply. |
| OSM extract | retrieved 2026-08-27 | CURRENT structural proxy | Roads, catchments and POI/place proxies. |
| PMMY official page | updated 2026-02-05 | CURRENT rule screen | Category/purpose/collateral screening only. |
| AHIDF temporary continuation | 2026-04-01 to 2026-09-30 | CURRENT rule screen | Conditional scheme screen subject to superseding approval. |

Unknown current locality variables include observed selling price, procurement price, rent, wage, electricity/fuel logistics cost, verified competitor capacity, supplier quotes, and lender-specific rate/underwriting. They are never silently replaced with an old observation.

## 7. Restricted source integrity

The four official survey archives were acquired under applicant access, retained privately, and excluded from public-share packaging. Full member CRC checks passed.

| Archive | Exact bytes | SHA-256 |
|---|---:|---|
| HCES 2022-23 CSV | 244,317,752 | 093a51d337eb07eede7d6e2a00ec55790d926bacf869be2cf2825abd629444ae |
| HCES 2023-24 CSV | 256,315,433 | acf7b9cc840676fb812c05c48f09fa034955fe2cad5112e6d9b6d852f5f2e267 |
| ASUSE 2023-24 CSV | 98,219,217 | 82a2e59aab71fee6dda7cd5f859c7cfbcf5e23ddf70b36a5a2962296b838de54 |
| ASUSE calendar-2025 CSV | 173,738,167 | f20b35abdb7ba97daaca24f4b927a277e95e1145fcbe86b2bd97304f771dc591 |

The aggregate priors, public-safe metrics, provenance, and code are shareable. Unit respondent records and fitted artifacts derived from restricted records remain private. This is a legal/data-governance boundary rather than a technical omission.

## 8. Freshness audit and evidence statuses

Every important evidence record can retain source, dataset/version, observation date, effective date, retrieval date, geography, units, estimate status, confidence, and freshness status. The supported freshness labels are CURRENT, RECENT, HISTORICAL_BASELINE, PROJECTED, STALE_FOR_DECISION, and UNKNOWN.

Structural variables can legitimately use an older authoritative baseline when the year is visible. Fast-changing variables must use a current source or remain uncertain. A recommendation may use a modelled planning range, but it cannot call that range an observed current locality value.

The audit policy is fail-closed for commodity-specific dairy decisions: current productive supply, price, incumbent capacity, route cost, and source-linked cost configuration must exist. Generic sector adapters are explicitly a lower-confidence planning path based on the most recent available ASUSE regional enterprise prior.

## 9. Population projection policy

Census 2011 is never relabelled as 2026. Where a generic calculation requires a population scale, the engine can create an explicit scenario projection with base year 2011 and horizon 15 years:

- Rural annual rates: 0.6 percent lower, 1.1 percent central, 1.6 percent upper.
- Urban annual rates: 1.0 percent lower, 1.7 percent central, 2.4 percent upper.
- Formula: P_2026 = P_2011 * (1 + g)^15.
- Status: PROJECTED; confidence: LOW.

The projection notes that boundary-change adjustment is unavailable. These scenario rates are planning assumptions, not official locality forecasts. The older v0.3 report correctly said no projection was stored at that checkpoint; v0.5 adds the explicit method and preserves the change in versioned documentation.

## 10. HCES model training

The HCES task predicts zero-inclusive monthly liquid-milk litres per household member. Training used 18,120 West Bengal household rows spanning 23 district groups; 7,560 targets were zero. Validation used leave-one-district-out geographic holdout.

| Model | MAE litres | RMSE litres | Result |
|---|---:|---:|---|
| Weighted category-mean baseline | 1.384585 | 1.748752 | Baseline |
| Ridge one-hot | 1.367413 | 1.733946 | Improved |
| Random forest | 1.353607 | 1.724402 | Holdout winner |

Random-forest weighted bias was 0.000133, mean calibration ratio 1.000082, and decile calibration MAE 0.131882. The fitted artifact is real and checksum-registered. Ordinary locality requests do not contain the household microfeatures required for valid inference, so production uses the direct weighted district/sector HCES prior instead of pretending to score an inapplicable row.

## 11. ASUSE model training

The ASUSE task predicts annualized enterprise gross value added in INR using official item 769 and the documented reference-period rule. Training used 38,626 West Bengal enterprise rows across 23 district groups; 40 targets were zero. Validation used leave-one-district-out holdout.

| Model | MAE INR | RMSE INR | Result |
|---|---:|---:|---|
| Weighted category-mean baseline | 97,124.15 | 259,004.56 | Baseline |
| Ridge one-hot | 68,004.76 | 197,753.34 | Improved |
| Random forest | 61,573.20 | 193,228.67 | Holdout winner |

Random-forest weighted bias was INR 22.54, mean calibration ratio 1.000151, and decile calibration MAE INR 2,528.68. Production again uses the direct weighted district/sector/NIC2 prior because the customer request lacks enterprise microfeatures. Training completion and production applicability are reported separately.

## 12. Sector adapter library

The generic planning library contains ten supported adapters mapped to the latest available ASUSE production priors:

| Adapter | NIC2 basis | Planning role |
|---|---:|---|
| Kirana/grocery | 47 | Small retail benchmark |
| Poultry input/egg aggregation | 46 | Wholesale/distribution benchmark |
| Fish collection/distribution | 46 | Cold-chain-light distribution benchmark |
| General food processing | 10 | Small manufacturing benchmark |
| Rural distribution/aggregation | 46 | Local logistics/wholesale benchmark |
| Flour mill | 10 | Staple processing benchmark |
| Spice processing | 10 | Value-add processing benchmark |
| Mustard oil extraction | 10 | Oilseed processing benchmark |
| Electronics/mobile retail | 47 | Durable retail benchmark |
| Household-goods distribution | 46 | Wholesale benchmark |

Each adapter declares unit, ASUSE mapping, demand/incumbent scaling, starter/growth capacities, CAPEX/working-capital split, fixed overhead, staffing, space, service radius, inventory/receivable/payable days, lifetime, residual value, licensing assumptions, and downside variables. Dairy remains the deeper physical-evidence path and is gated rather than approximated by a generic adapter.

## 13. Demand, supply, price and competition ladder

The estimation ladder prefers direct current locality evidence, then recent regional official priors, then explicit projections or modelled benchmarks, and finally a gate. It never silently treats a lower rung as a higher rung.

Generic demand is an ASUSE-scaled planning envelope, not exact household demand. Supply and incumbent service are benchmark envelopes, not verified competitor capacity. The browser displays ranges and confidence, not false point precision. OSM POIs can contextualize nearby activity but are not a complete business census.

Commodity-specific dairy demand may combine an HCES rate with an explicit projected population range. Physical supply requires current productive animal share, yield, seasonality, collection loss, and reachable capacity. Current selling/procurement price and route cost remain mandatory for a high-confidence dairy decision.

## 14. Catchment, graph and flow mathematics

The spatial layer resolves a catchment against the West Bengal OSM extract. A central Kolkata 5 km test returned 1,172 entities; a tested local route was 4.63 km. The graph represents sources, incumbent/venture transformations, transport links, and demand sinks when decision-ready evidence exists.

The flow objective is lexicographic:

- First maximize served demand F.
- Then minimize total economic cost sum_e(c_e * f_e) subject to the maximum F.
- Constraints: 0 <= f_e <= u_e and flow conservation at transshipment nodes.

Bottlenecks are ranked by marginal served-demand gain after an edge-capacity perturbation. Counterfactual output separates baseline served demand, newly served demand, venture flow, and incumbent flow displaced by the new venture. This prevents cannibalized flow from being mislabelled as newly created welfare.

## 15. Venture primitives and cash conversion

A venture primitive now carries operational structure, not merely cost and capacity:

- service radius and required space;
- operating days per month;
- inventory, receivable, and payable days;
- cash conversion cycle = inventory days + receivable days - payable days;
- lifetime and residual value;
- staff, CAPEX, working capital, overhead, and licensing assumptions.

The customer view exposes the practical meaning: premises, staff, licenses, stock cycle, service radius, startup cost, monthly operating burden, and the evidence to verify. Financial calculations preserve the distinction between startup investment, variable procurement, fixed operating cost, and financing.

## 16. MVV and finite-set optimization

For each adapter, the engine enumerates feasible starter/growth configurations. Minimum viable venture selection is exact over that finite list. A candidate must respect capital and any supplied income/debt constraints; the engine does not claim a continuous global optimum or a complete mixed-integer model of all possible business designs.

The opportunity table distinguishes useful roles:

- Lowest viable: minimum feasible project cost.
- Highest upside: strongest central cumulative cash result.
- Survival-first: highest scenario survival, then downside tie-breaks.
- Robust: minimax-regret winner over the explicit scenario table.

The Pareto frontier retains candidates not dominated on lower investment, higher survival, and higher median cumulative cash. This prevents one arbitrary weighted score from hiding tradeoffs.

## 17. Joint uncertainty model

Deep mode draws 512 reproducible scenarios from seeded triangular distributions. The seed is derived with SHA-256 from stable analysis/candidate identity inputs. Shocks cover demand, selling-price/revenue factor, variable cost, and fixed cost. Triangular distributions are used because they make lower, modal, and upper planning assumptions explicit and avoid an unjustified Gaussian claim.

For each candidate the engine records:

- survival rate over 36 months;
- target-income attainment rate when a goal is supplied;
- payback-within-36-month rate;
- p10 minimum cash and p10 cumulative cash;
- median cumulative cash;
- 95 percent value-at-risk loss and conditional value-at-risk loss.

Scenario survival is model survival under the stated shock envelope. It is not the empirical probability that a real business will survive.

## 18. Robust choice and regret

Let C_s(c) be cumulative cash for candidate c in scenario s. Scenario regret is max_j C_s(j) - C_s(c). Maximum regret is the worst scenario regret for a candidate. The minimax-regret choice is argmin_c max_s regret_s(c).

Expected-value, survival-first, CVaR-aware, and minimax-regret choices are computed separately. They may disagree, and the product exposes that disagreement instead of forcing one answer. The selected ordinary recommendation prioritizes scenario survival and downside cash before central upside where the user has not supplied a different explicit objective.

CVaR is presented as worst-tail cumulative cash, not as a confusing negative loss sign. The finance screen also distinguishes operating break-even, cash break-even, and investment payback.

## 19. Failure boundaries and sensitivities

The engine uses a 40-iteration numerical search to find boundaries for demand factor, selling-price/revenue factor, and variable-cost factor. If the entire tested range survives, the output says that no cash failure occurred within the tested 36-month range. It does not manufacture a near-zero threshold.

These boundaries answer questions such as: how far can demand fall before monthly cash becomes negative; how far can price/revenue fall; how far can variable cost rise? The browser pairs each boundary with scenario p10 cash, scenario survival, payback frequency, and tail cash so the user can see both one-variable and joint-shock behavior.

The current engine does not estimate an empirical correlation matrix from local time-series data. Scenario factors are planning assumptions. Therefore sensitivity findings are useful for stress design, not calibrated real-world probabilities.

## 20. Finance and accounting

The engine calculates project cost, own capital applied, external finance gap, monthly revenue/cost/cash, gross margin, operating margin, contribution margin per planning unit, break-even volume, payback, 36-month NPV, and annualized IRR.

Key formulas:

- Break-even volume = fixed cost / contribution margin per unit.
- NPV = sum_t CF_t / (1 + r_monthly)^t, with r_monthly = (1 + r_annual)^(1/12) - 1.
- IRR solves NPV(r) = 0 by bounded bisection and is annualized.
- Payback month is the first month cumulative venture cash recovers startup investment.

The displayed NPV uses a 12 percent annual planning discount rate. IRR and NPV are benchmark-adjusted outputs, not guaranteed investment returns. Input/output accounting avoids double-counting ASUSE procurement inputs in both margin and fixed OPEX.

## 21. Finance rules and effective dates

PMMY screening uses the Department of Financial Services page updated 2026-02-05. Categories are Shishu up to INR 50,000; Kishore above INR 50,000 through INR 5 lakh; Tarun above INR 5 lakh through INR 10 lakh; and Tarun Plus above INR 10 lakh through INR 20 lakh for a borrower who previously took and successfully repaid Tarun. The official rule does not establish one universal lender rate, tenure, underwriting result, or sanction.

AHIDF/IDF is temporarily continued from 2026-04-01 through 2026-09-30 or until an earlier superseding approval. Existing temporary-period terms include 3 percent interest subvention, lender finance up to 90 percent of eligible project cost, and up to eight years including up to two years of principal moratorium. Portal window, eligible cost, margin, gross/net lender rate, security, underwriting, and sanction must be confirmed live.

## 22. Computed SWOT and practical advice

SWOT is assembled from calculation outputs rather than generic template text. Strengths can include low financing dependence, positive contribution margin, or robust survival under the tested envelope. Weaknesses can include low confidence, long cash conversion, thin margin, or reliance on a regional benchmark. Opportunities can include an unserved modelled envelope or a lower-capital Pareto option. Threats can include downside failure boundaries, stale physical supply, unknown current prices, or scheme expiry.

The Action Plan tab converts these findings into stages: verify local demand and current prices; obtain supplier and premises quotations; validate licenses; run a small pilot; measure weekly revenue, margin, inventory days and repeat demand; expand only after stated triggers. A separate When Not To Start section identifies evidence or cash conditions that invalidate the plan.

## 23. Deep E2E validation

| Locality / district | Sector | Capital INR | Cost INR | Payback | Scenarios | Result |
|---|---|---:|---:|---:|---:|---|
| Kolkata / Kolkata | Kirana | 100,000 | 35,971 | 21 mo | 512 | CONDITIONAL |
| Barasat / North 24 Parganas | Poultry aggregation | 100,000 | 13,823 | 21 mo | 512 | CONDITIONAL |
| Abad Bhagabanpur / South 24 Parganas | Fish distribution | 125,000 | 57,047 | 32 mo | 512 | CONDITIONAL |
| Kharibari / Darjeeling | Food processing | 150,000 | 54,986 | 24 mo | 512 | CONDITIONAL |
| Anandapur / Jalpaiguri | Rural distribution | 120,000 | 14,027 | 15 mo | 512 | CONDITIONAL |
| Adina / Maldah | Kirana | 80,000 | 20,816 | 32 mo | 512 | CONDITIONAL |
| Adra / Purulia | Poultry aggregation | 90,000 | 49,500 | 26 mo | 512 | CONDITIONAL |

All seven returned HTTP 200 using methodology decision-v5. All reported modelled survival 1.0 under the configured envelope because starting capital left a material cash buffer; this is not interpreted as observed certainty. In every case the minimax-regret winner was the growth configuration while the ordinary finite MVV selected the starter configuration.

## 24. All-district smoke test

One database-supported locality was tested for every one of the 23 district labels. HTTP status was 200 in all 23 cases. Twenty-two produced a selected conditional kirana benchmark. The historical undivided Barddhaman case returned INSUFFICIENT_EVIDENCE and NO_DEMAND_EVIDENCE.

The smoke run covers Alipurduar, Bankura, Barddhaman, Birbhum, Dakshin Dinajpur, Darjiling, Haora, Hugli, Jalpaiguri, Jhargram, Kalimpong, Koch Bihar, Kolkata, Maldah, Murshidabad, Nadia, North Twenty Four Parganas, Paschim Barddhaman, Paschim Medinipur, Purba Medinipur, Puruliya, South Twenty Four Parganas, and Uttar Dinajpur.

This is endpoint and evidence-routing coverage, not an economic validation of every district or every locality.

## 25. Browser validation and product screenshots

[[IMAGE:output/screenshots/v0.5.0/gramartha_summary_kolkata.png]]

The local product was exercised over HTTP in a real Chromium browser. The test loaded exactly 23 district choices, selected Kolkata, ran Find Best across ten adapters in deep mode, completed in about three seconds on the test machine, switched result tabs, and inspected the Finance view. There were zero console warnings/errors.

The screenshot is evidence of rendered software behavior, not proof that the underlying benchmark is an observed market. Public Netlify deployment was not changed and remains outside the verified v0.5 completion claim.

## 26. Finance screen validation

[[IMAGE:output/screenshots/v0.5.0/gramartha_finance_kolkata.png]]

The browser Finance tab displayed project cost, own capital, financing gap, three break-even concepts, gross margin, break-even volume, NPV, IRR, cash chart, and current-scheme caveats. The Kolkata best-opportunity browser run selected poultry and egg aggregation and displayed a conditional benchmark, not a lender quote.

The UI labels NPV at a 12 percent planning discount and IRR as benchmark-adjusted. It does not infer a loan interest rate when none is available.

## 27. Verification matrix

| Verification | Current result |
|---|---|
| Python tests | 50 passed |
| Ruff | Passed |
| JavaScript syntax | Passed |
| District smoke | 23/23 HTTP 200; 22 conditional, 1 gated |
| Deep product E2E | 7/7 HTTP 200 with 512 scenarios |
| SQLite integrity | Previously audited ok |
| Registry integrity | 53/53 recorded files previously matched size and SHA-256 |
| Restricted ZIP CRC | 4/4 passed |
| Trained artifacts | Two random-forest winners plus ridge artifacts checksum-registered |
| Accounting identity | 1,551 ASUSE groups; max residual INR 3.725e-9 |
| Browser console | Zero warnings/errors in verified flow |

Flow benchmark results on chain graphs were 0.00007 s at 10 nodes, 0.00019 s at 50, 0.00210 s at 100, 0.00158 s at 500, and 0.00312 s at 1,000. Bottleneck perturbation was benchmarked through 100 nodes; larger reruns were intentionally omitted because the chain test is not a worst-case graph.

## 28. Requirement traceability

| Requirement family | v0.5 status |
|---|---|
| Fixed West Bengal, DB districts, scoped search | Implemented and browser-tested |
| Optional entrepreneur profile | Implemented |
| Multi-sector library | Ten generic adapters plus gated dairy |
| Freshness labels and explicit projections | Implemented |
| Actual model training and holdout metrics | Implemented; production applicability constrained |
| Catchment, graph, flow, bottleneck | Implemented when decision-ready evidence exists |
| Automatic venture generation and finite MVV | Implemented for enumerated configurations |
| Joint scenarios, Pareto, CVaR, regret | Implemented in deep mode |
| Failure boundaries | Implemented for demand, price/revenue and variable cost |
| Computed SWOT and action plan | Implemented |
| Statewide smoke and diverse E2E | Implemented with stated limits |
| Public deployment | Not completed or claimed |
| Current locality transactions/quotes | Not acquired; remains an evidence limit |

## 29. Remaining evidence and method limits

- Generic sector results are MODELLED_BENCHMARK, not observed locality demand, sales, competitors, or prices.
- HCES and ASUSE are sampled regional priors and cannot identify exact village demand or enterprise capacity.
- Census 2011 is a historical structural baseline; the 2026 population scenario is a low-confidence explicit projection.
- Current local price, procurement, rent, wage, electricity/fuel, supplier, and competitor-capacity evidence remains unknown.
- Scenario distributions and bounds are planning assumptions, not empirically calibrated survival probabilities.
- MVV and regret are exact only over the generated finite candidate list.
- The automatic library is not a complete universe of ventures and does not include a general configuration MILP.
- OSM is a volunteered spatial proxy and may omit roads, places, or businesses.
- Finance screens do not promise lender rate, eligibility, portal acceptance, sanction, or subsidy receipt.
- Restricted survey unit records and fitted artifacts cannot be included in a public package.
- The public URL presently shows a different site; only the local HTTP product is verified here.

## 30. Final decision and handoff

v0.5.0 is the strongest honest working product at this checkpoint: a usable local advisory interface backed by real West Bengal identity/spatial data, recent official survey priors, real trained model artifacts and geographic holdout metrics, a finite venture engine, robust joint-scenario analysis, finance/accounting calculations, and broad technical validation.

It is ready for local demonstrations and structured pilot discovery. It is not ready to be described as a high-confidence current-market recommendation service without integrating verified locality transactions, supplier/competitor capacity, current quotes, and lender terms. A safe pilot should collect those fields, compare realized results against the benchmark intervals, recalibrate scenario distributions, and preserve the existing versioned evidence/provenance chain.

The versioned package contains code, configuration, databases, documentation, public-safe outputs, tests, E2E records, screenshots, this report, and a SHA-256 manifest. Restricted respondent data remains outside the shareable archive by design.

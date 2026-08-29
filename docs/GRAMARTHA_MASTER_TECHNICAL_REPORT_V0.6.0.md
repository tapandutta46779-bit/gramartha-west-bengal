# GramArtha SIH26091 Master Technical Report v0.6.0

Audit date: 2026-08-29 (Asia/Kolkata)

This report records the strongest honestly verified GramArtha product at v0.6.0. It separates historical observations, recent observations, projections, benchmark-adjusted estimates and unknown current facts. It does not claim exact locality demand from survey microdata, complete statewide economic coverage, lender approval, guaranteed income, or a continuous global optimum.

## 1. Executive summary and honest completion boundary

GramArtha is a working West Bengal business-planning web product. A user resolves a current product locality, supplies capital and optional profile constraints, selects a sector or asks for a comparison, and receives an evidence-aware plan spanning local market, network repair, minimum viable venture, finance, uncertainty, SWOT, pre-mortem and action stages.

Version 0.6.0 adds an explicit current-versus-historical geography layer, exact crosswalk records, current district audit, desired-income/debt inverse analysis, adaptive failure boundaries, a typed Sector Factor Registry, deeper competitor/customer/channel outputs, a working dairy planning path, richer customer UI and downloadable per-analysis business-plan PDF.

Verified at this report checkpoint:

- 23 current display districts and 40,474 current product localities.
- 55 automated tests pass; Ruff and JavaScript syntax checks pass.
- Every current district passes locality search and a conditional kirana smoke analysis.
- Dairy returns complete conditional plans in tested Nadia, North 24 Parganas and Darjeeling localities, while safely declining a tested Bankura case with no incremental central flow.
- Trained HCES and ASUSE artifacts and geographic holdout metrics remain registered.
- Permanent public hosting is not claimed unless separately verified after this report build.

## 2. SIH26091 problem and GramArtha philosophy

SIH26091 asks for hyper-local business opportunity discovery rather than a generic business-plan template. The product must connect a specific locality and entrepreneur profile to real evidence, an economic network, missing-link diagnosis, viable configuration, finance and risk.

The design philosophy is evidence first. Every important value should carry source, dataset/version, observation or effective date, retrieval date, geography, unit, evidence class, freshness label and confidence. Missing current evidence becomes an uncertainty statement, a validation task or a blocking gate; it is never silently fabricated.

The second principle is decision usefulness. The ordinary user sees capital actually deployed, retained reserve, finance required, modelled income, market gap, competition, top risks and an action plan. Technical identifiers and calculation trace remain available in an expandable audit panel.

## 3. Customer workflow and seven-stage product journey

The implemented journey preserves seven stages:

1. Setup: West Bengal, district, locality, capital, sector, radius, Quick/Deep and language.
2. Local market: demand, reachable supply, gap, prices/unit value, customers, suppliers, competitors and channels.
3. Opportunities: finite cross-configuration and cross-sector comparison.
4. Risk and SWOT: scenarios, CVaR, sensitivity, failure boundaries and pre-mortem.
5. Business plan: equipment, staff, space, stock cycle, CAPEX, OPEX, licences and quality controls.
6. Finance: own contribution, financing requirement, scheme screen, break-even, payback, NPV, IRR and 36-month cash.
7. Action: before-starting checks, week 1, month 1, months 2-3, months 4-6 and stop rules.

The analysis progress panel measures real elapsed time. It does not intentionally delay a fast computation or invent server stages that were not observed by the client.

## 4. West Bengal scope and exact statewide geographic coverage

| Layer | Verified count | Meaning |
|---|---:|---|
| Current product districts | 23 | Present-day display set; unique. |
| Current subordinate units | 474 | DS057-derived block/municipal parent entities. |
| Current product localities | 40,474 | Searchable villages/wards/localities. |
| Historical Census entities | 13,062 | Explicit 2011 historical layer. |
| Exact locality crosswalks | 6,506 | Exact normalized locality plus compatible hierarchy. |
| District-context crosswalks | 4,641 | Compatible contextual mappings. |
| Unsafe split-era entities left unmapped | 1,915 | Deliberately not guessed. |

Statewide geography is not statewide economic completeness. Coordinates, OSM POIs, exact historical crosswalks and current dynamic market observations remain partial by locality.

The official LGD bulk download is the desired canonical authority, but the available official bulk workflow was CAPTCHA-gated during this implementation. Product IDs are therefore DS057-derived stable internal IDs and are never represented as official LGD codes.

## 5. Current versus historical geography architecture

The database now separates three concepts:

- `current_geo_entity`: product-facing current district, parent and locality entities.
- `historical_geo_entity`: source-native Census 2011 names, parents and observation year.
- `geo_crosswalk`: explicit source-to-current relation, confidence, effective dates and notes.

Search uses the current product layer when it exists. Census 2011 remains a historical structural baseline. A product response can retain Census codes and source IDs without pretending that a 2011 district boundary or name is a present-day observation.

The 23 current display districts are Alipurduar, Bankura, Birbhum, Cooch Behar, Dakshin Dinajpur, Darjeeling, Hooghly, Howrah, Jalpaiguri, Jhargram, Kalimpong, Kolkata, Malda, Murshidabad, Nadia, North 24 Parganas, Paschim Bardhaman, Paschim Medinipur, Purba Bardhaman, Purba Medinipur, Purulia, South 24 Parganas and Uttar Dinajpur.

## 6. Geographic crosswalk methodology and Bardhaman split case

Crosswalk creation is conservative. Exact normalized locality name is necessary but not sufficient: parent and current-successor district context must also be compatible. Name-only joins across district splits are prohibited.

The Bardhaman case is the central safety test. Historical Census `Barddhaman` is not automatically rewritten to a current successor. Post-split DS057 `Bardhaman`, when published alongside a distinct Paschim Bardhaman group, maps to current Purba Bardhaman. Historical rows require an explicit locality-level successor crosswalk; 1,915 unsafe split-era rows remain unmapped.

The statewide geography audit reports zero orphan nodes, zero wrong-parent district assignments, zero same-parent duplicates and zero cross-district source leakage in the current product layer.

## 7. Data inventory, source governance and restricted files

Core source years are:

| Source | Observation/version | Product use |
|---|---|---|
| Census geography and PCA | 2011 | Historical identity and population anchor. |
| 20th Livestock Census | 2019 | Historical species stock context only. |
| HCES | 2022-23, 2023-24 | Consumption comparison and production prior. |
| ASUSE | 2023-24, calendar 2025 | Enterprise comparison, production benchmark and trained targets. |
| WB ARD milk production | 2024-25 | Official productive district milk output. |
| OSM West Bengal extract | retrieved 2026 | Road, place and POI structural proxy. |
| Official finance pages | effective/retrieved 2026 | Conditional scheme screening. |

Restricted HCES/ASUSE respondent files remain private. Public packages may contain code, aggregate priors, model metrics and public-safe artifacts, but not respondent-level records or restricted derived artifacts. Preserving raw source files does not authorize redistribution.

## 8. Freshness architecture and evidence ladder

Supported freshness labels are `CURRENT`, `RECENT`, `HISTORICAL_BASELINE`, `PROJECTED`, `STALE_FOR_DECISION` and `UNKNOWN`.

Structural values may use an older authoritative source when observation year remains visible. Fast-changing values - prices, procurement costs, fuel, transport, wages, rent, finance rates, scheme rules and venture quotes - require a current source or an explicit evidence limitation.

The ladder is: direct current locality evidence; recent official regional evidence; explicit projection; benchmark-adjusted estimate; then unknown/gate. A lower rung never inherits the label of a higher rung.

## 9. HCES methodology, zero consumers and production estimator

The HCES training target is zero-inclusive monthly liquid-milk litres per household member. Zero consumers remain in the data; they are not deleted to make average consumption look larger.

Training used 18,120 West Bengal household rows across 23 district groups, including 7,560 zero targets. Validation used geographic leave-one-district-out holdout.

| Model | MAE litres | RMSE litres | Selection |
|---|---:|---:|---|
| Weighted category mean | 1.384585 | 1.748752 | Baseline. |
| Ridge one-hot | 1.367413 | 1.733946 | Improved. |
| Random forest | 1.353607 | 1.724402 | Holdout winner. |

The trained model is real, but ordinary locality requests do not supply its household microfeatures. Production therefore uses the direct weighted HCES district/sector prior rather than pretending to score an unavailable household row.

## 10. ASUSE methodology, enterprise model and production choice

The ASUSE target is annualized enterprise gross value added using the official reference-period rule. Training used 38,626 West Bengal enterprise rows across 23 district groups, with 40 zero targets and geographic leave-one-district-out validation.

| Model | MAE INR | RMSE INR | Selection |
|---|---:|---:|---|
| Weighted category mean | 97,124.15 | 259,004.56 | Baseline. |
| Ridge one-hot | 68,004.76 | 197,753.34 | Improved. |
| Random forest | 61,573.20 | 193,228.67 | Holdout winner. |

The fitted random forest is registry-selected for the research task. Production uses direct weighted district/sector/NIC2 priors because a customer request does not contain the enterprise microfeatures required for defensible inference.

## 11. Model registry, holdout metrics and rejected alternatives

The model registry stores artifact path, checksum, target, training rows, holdout design, MAE, RMSE, bias, calibration and selection reason. Fitted artifacts are not equated with production applicability.

HCES random forest weighted bias was 0.000133, mean calibration ratio 1.000082 and decile calibration MAE 0.131882. ASUSE random forest weighted bias was INR 22.54, mean calibration ratio 1.000151 and decile calibration MAE INR 2,528.68.

Ridge and category means are retained as comparisons. They were rejected as the holdout winner, but the direct weighted regional prior is still preferred for ordinary production because it matches the available query features and avoids invalid microfeature reconstruction.

## 12. Population estimator and uncertainty preservation

Census 2011 population is never labelled current. Where required, the engine creates an explicit 2026 scenario projection:

`P_2026 = P_2011 * (1 + g)^15`

Rural annual growth scenarios are 0.6%, 1.1% and 1.6%; urban scenarios are 1.0%, 1.7% and 2.4%. Output stores lower, central, upper, base year, projection year, method and limitations.

These are planning scenarios, not official forecasts. Boundary changes are not fully adjusted and lower confidence is retained.

## 13. Demand engine and customer segmentation

Generic sectors use an ASUSE-scaled opportunity envelope labelled `MODELLED_BENCHMARK`, not exact household demand. Dairy demand uses HCES 2023-24 liquid-milk quantity per person multiplied by current/projected locality population.

`D_milk = Population * monthly_quantity_per_capita`

Customer segmentation comes from the Sector Factor Registry. It identifies defensible groups - households, retailers, restaurants, institutions and business users as relevant - but does not invent local percentage shares without measured data.

## 14. Supply engine and productive dairy output

Total livestock stock is never converted directly to milk supply. The preferred conceptual equation is:

`S_milk = Stock * ProductiveFraction * LactationFraction * Yield * MarketedSurplus * Accessibility`

Version 0.6 uses a stronger available source: West Bengal ARD's official district productive milk-output estimate for 2024-25. Local reachable supply scales official productive output to locality population and applies explicit combined marketed-surplus/accessibility scenarios of 8% lower, 16% central and 30% upper.

The result is `MODELLED_ACCESSIBLE_SUPPLY`, not an observed locality collection volume. Route time, chilling and marketed surplus remain local validation tasks.

## 15. Price engine and current-value boundary

Dairy's planning unit value is HCES 2023-24 expenditure divided by quantity. It is `RECENT_SURVEY_UNIT_VALUE`, not a current locality retail quote. Contribution per litre combines this unit value with the ASUSE NIC46 enterprise-margin prior.

Generic sectors use ASUSE output/input margin shares. Current local selling price, farmgate/procurement price, wholesale price and route cost remain explicitly missing where no current source is linked.

A recommendation therefore includes a pre-spend requirement to collect customer prices and at least two supplier quotations. It never calls the survey unit value a 2026 observed price.

## 16. Competitor intelligence, markets and channels

OSM entities are classified as direct or indirect competitors by sector. The result includes counts, nearest candidate names/categories/distances, qualitative proxy density, nearest markets, institutional candidates and a caveat.

Competitor capacity, sales and market shares remain unknown unless separately observed. Count is not treated as capacity, and HHI is not calculated without shares.

Channels are ranked primary/secondary using sector logic over reach, margin, working capital, reliability and complexity. Confidence remains low and assumption-based when no local transaction evidence exists.

## 17. Sector Factor Registry

The typed registry supplies customer segments, supplier types, direct/indirect OSM categories, channels, equipment, quality controls, operational factors, weather factors, insurance options and cost shares.

Implemented registry families include dairy, poultry, fish, kirana, food processing, flour mill, spice processing, mustard oil, electronics/mobile retail, household-goods distribution and rural distribution.

Weather appears only when causally relevant. Dairy includes heat, spoilage, chilling and flood-route risk; fish includes temperature, ice and flood risk; electronics retail does not receive invented weather sensitivity.

## 18. Multi-sector adapter architecture and practical venture library

Every visible production sector has a real adapter rather than a dropdown-only shell. An adapter defines unit, survey mapping, graph commodity, benchmark scaling, CAPEX/working-capital logic, staffing, space, stock cycle, licences and stress variables.

Generic adapters enumerate micro, starter, balanced, growth and expanded configurations. Existing shop or vehicle assets can reduce relevant setup assumptions. Candidate labels state that ASUSE is a weighted regional benchmark and local quotes are required.

Dairy compares micro collection, rented delivery, route distribution, collection/chilling and institutional supply configurations, plus a source-linked advanced configuration when caller evidence supplies exact current costs.

## 19. Dairy end-to-end repair and perishability

Dairy uses physical litres/month for demand and flow. Productive district output creates the potential producer source; the central marketed/accessibility estimate creates incumbent reachable capacity. New collection, delivery, storage or supply edges can repair flow only up to physical source and customer bounds.

Perishability is represented through equipment and validation requirements: food-grade cans, insulated transport, collection-time log, temperature/acidity check, rejection/spoilage log and route-time verification. Current chilling availability remains unknown unless observed.

Verified real samples: Abhaynagar in Nadia, Abhirampur in North 24 Parganas and Abhiram in Darjeeling returned complete conditional dairy plans. Abantika in Bankura returned no feasible incremental plan because the central reachable-supply model did not create new flow; this is correct refusal, not a crash.

## 20. Local economic graph and exact flow

The graph contains producer/supplier nodes, customer nodes and incumbent/venture edges. Each entity carries commodity, unit, capacity or demand, confidence and evidence IDs.

The lexicographic flow objective is:

`maximize F = sum served demand`

then, at maximum `F`:

`minimize sum_e(c_e * f_e)`

subject to `0 <= f_e <= u_e` and flow conservation at transshipment nodes. The implementation uses an exact min-cost-flow solver for the represented network.

## 21. Bottleneck, min-cut sensitivity and network reliability

Unserved demand is:

`U_q(G) = D_q - Served_q(G)`

Bottlenecks are ranked by the additional served demand after a controlled capacity perturbation. This marginal test is more decision-useful than simply sorting edges by capacity.

Version 0.6 retains the min-cost-flow basis and exposes bottleneck/counterfactual trace. Full probabilistic edge reliability calibration is not claimed; route and supplier reliability remain scenario or validation inputs rather than fabricated probabilities.

## 22. Counterfactual repair, cannibalization and welfare accounting

For venture `b`:

`Benefit(b) = Served(G + DeltaG_b) - Served(G)`

The counterfactual separates baseline served flow, counterfactual served flow, newly served demand, added venture flow, incumbent flow displaced and economic cost change.

Cannibalized incumbent flow is never labelled new welfare. This prevents a new business that merely reroutes existing demand from being presented as creating an equivalent new market.

## 23. Facility location, routing and inventory scope

The OSM spatial layer supports radial catchments, nearest markets/institutions and route proxies where verified/proxy coordinates exist. Straight-line distance is labelled separately from routed distance.

Facility location is currently enumerated over the selected locality/catchment and venture configurations; it is not a statewide continuous facility-location optimum. Routing is a planning proxy and current fuel, vehicle and route-time quotes remain necessary.

Inventory scope includes inventory, receivable and payable days. Cash conversion is:

`CCC = InventoryDays + ReceivableDays - PayableDays`

## 24. MVV formulation and exact finite oracle

Minimum viable venture selection minimizes investment over the generated finite candidate set subject to useful new flow, funding, desired income, debt ceiling, mobility and time constraints.

`min I(x)` subject to `NewlyServed(x) >= threshold`, `I(x) <= C + Dmax`, `Income(x) >= target` and active profile limits.

The exhaustive evaluator is exact over the enumerated configurations. It does not claim a continuous global optimum, a complete MILP of every business design or branch-and-bound over an unbounded design space.

## 25. Desired income, debt ceiling and inverse optimization

Debt is a ceiling, not a target. Funding ceiling is:

`I_max(C,D) = C + Dmax`

Debt required by a configuration is `max(I - C, 0)`. With no debt value supplied, the conservative debt ceiling is zero.

Inverse output reports maximum owner income under current funding, minimum own capital for a requested income, and minimum debt ceiling for that income over the enumerated set.

## 26. Constraint relaxation and infeasible-profile advice

When no candidate satisfies all constraints, the result is not a generic error. It names binding constraints and calculates the smallest enumerated relaxation.

The UI reports best achievable income under current limits, income shortfall, smallest additional own capital and smallest additional debt ceiling. It can also identify mobility or time limits.

The scope statement remains explicit: exact over generated candidate configurations, not all imaginable ventures.

## 27. Pareto optimization, robust ranking and regret

Deep comparison reports expected-value, survival-first, CVaR-aware and minimax-regret winners. A Pareto frontier retains candidates not dominated on lower investment, higher survival and higher median cash.

For scenario `s`, regret of candidate `b` is:

`R(b,s) = max_j Value(j,s) - Value(b,s)`

The minimax-regret candidate minimizes `max_s R(b,s)` over the explicit shared scenario table. Shared scenarios make comparisons internally consistent.

## 28. CAPEX, OPEX, working capital and unit economics

Project cost separates CAPEX and working capital. CAPEX is allocated to equipment/fixtures, installation/setup, premises/basic fit-out and licensing/contingency. The allocation is benchmark-adjusted, not a current quotation.

Monthly OPEX separates fixed overhead from month-12 variable cost. Sector cost shares prevent a generic cost mix from being applied to every business.

The customer view reports minimum working capital, a recommended 15% buffer, cash-conversion cycle, gross margin, break-even volume and the requirement to replace benchmark costs with local quotes.

## 29. Digital twin and accounting correctness

The 36-month twin models demand growth, ramp-up, capacity, unit price, variable cost, fixed cost, debt payment, operating cash flow and closing cash.

It distinguishes operating break-even, cash break-even and investment payback. Initial investment, owner capital and loan disbursement are accounted separately. Fixed OPEX is no longer multiplied by an undocumented factor; the full candidate fixed-overhead value enters the twin and uncertainty engine.

Month-level outputs support quarterly tables and a cash chart. The result remains a planning simulation, not audited financial statements.

## 30. Finance rules, scheme fit and effective dates

The finance layer screens PMMY and AHIDF from official rule records. Output stores rule version, retrieval date, effective date/window, category, maximum amount, conditions and missing underwriting facts.

Scheme results say potentially eligible or illustrative screening; they never say approved. Lender-specific interest rate, tenure, margin, moratorium, collateral interpretation and repayment capacity require a current lender quote.

Debt optimization respects the entrepreneur's maximum acceptable debt. A lower-cost venture does not automatically borrow the unused ceiling.

## 31. Monte Carlo/LHS scope and scenario calibration

Deep mode uses 512 reproducible joint triangular scenarios seeded from stable analysis identity. Factors cover demand, selling price, variable cost and fixed cost.

The current implementation is Monte Carlo-style triangular sampling, not Latin hypercube sampling. It does not claim LHS where LHS was not run.

Scenario distributions are planning assumptions and are explicitly `NOT_EMPIRICALLY_CALIBRATED`. Scenario survival is not the probability that a real business succeeds.

## 32. CVaR, downside cash and robust decision

For cumulative-cash loss `L`, VaR95 is the empirical 95th percentile. CVaR95 is the mean loss in the tail at or beyond VaR95.

The engine reports survival rate, target-income rate, payback-within-36-month rate, p10 minimum cash, p10 cumulative cash, median cumulative cash, VaR95 and CVaR95.

Robust winners and central winners may differ. The UI presents the distinction instead of collapsing every objective into one opaque score.

## 33. Controlled sensitivity and adaptive failure boundaries

Sensitivity applies controlled +/-5% perturbations to demand, selling price, variable cost and fixed OPEX. It reports low, central and high month-12 cash, derivative and elasticity, ranked by absolute cash effect.

Failure-boundary search is adaptive. Demand and price expand toward zero; variable and fixed cost expand up to ten times the central value; minimum surviving opening cash is searched independently.

When failure is not found, wording states the tested bound, such as no cash failure up to the tested deterioration. It never reports a false infinite safety margin.

## 34. Computed SWOT, entry difficulty and pre-mortem

SWOT is derived from business economics: payback, stock cycle, month-12 cash, working-capital intensity, staffing, benchmark status, unserved flow, channel diversification, sensitivity and competitor evidence.

Entry difficulty is a rule-based score over capital utilization, cash-conversion cycle, approvals, staffing and evidence confidence. It lists reasons rather than presenting an unexplained label.

The pre-mortem ranks plausible failure causes from sensitivity, competition and benchmark translation, and attaches a prevention action to each cause.

## 35. Niche discovery and staged expansion

Niche discovery comes from network gaps, sector factors, customer groups, supplier structure, mapped alternatives and channel options. A niche is a planning hypothesis until paid demand is observed.

Staged expansion begins with shared/rented assets and a paid pilot. Stage 1 deploys the selected minimum configuration while preserving reserve. Stage 2 requires a computed utilization-plus-cash trigger. If that trigger is not reached in 36 months, the plan explicitly says not to expand.

Stop rules reuse adaptive demand/cash boundaries and pre-mortem prevention actions.

## 36. Customer-facing UI, visualizations and accessibility

The UI retains the seven tabs while improving typography, spacing, cards, responsive behavior, errors and empty states. Summary leads with project cost, own capital deployed, finance required, revenue, owner-income band, payback, survival, gap and entry difficulty.

Meaningful visualizations include demand-versus-supply bars, cash-flow columns, sensitivity tornado, CAPEX allocation bars and the supplier-to-bottleneck-to-venture-to-customer network path. Text tables remain available for exact values.

The interface does not fabricate customer shares, competitor capacities, HHI or map completeness. Keyboard focus states and responsive single-column layouts are implemented.

## 37. Customer PDF and shareable decision artifact

Every selected analysis can be downloaded from `/analysis/{analysis_id}/pdf`. The generated A4 report includes recommendation, market, customers, suppliers, competitors, channels, setup, CAPEX, OPEX, working capital, finance, quarterly cash flow, scenario risk, failure boundaries, sensitivity, SWOT, pre-mortem, action plan, evidence freshness and sources.

A representative North 24 Parganas dairy report was rendered to PNG and visually inspected across nine pages. No clipping, overlap, unreadable table or broken footer was found.

The PDF repeats the decision boundary: planning estimate, not guaranteed income, lender sanction or a substitute for current supplier/customer/licence validation.

## 38. Real West Bengal E2E cases and profile matrix

The current geography audit searches and analyzes one sample in every present-day product district. All 23 search samples pass and all 23 kirana smoke analyses return conditional benchmark plans.

Deep product tests cover urban, semi-urban, rural, northern, southern, western and hill contexts where data permits. Dairy v0.6 verification includes Nadia, North 24 Parganas, Bankura and Darjeeling behavior.

Profile logic is tested for blank income, desired income, debt ceiling, infeasible target, zero debt, mobility, time, shop and vehicle effects. Infeasible profiles return exact enumerated inverse/relaxation advice rather than a crash.

## 39. Testing, performance and browser verification

The automated suite contains 55 passing tests covering API, geography, current/historical separation, flow, bottleneck, MVV, finance, freshness, survey import/model assumptions, sectors, uncertainty and counterfactual accounting.

Ruff and JavaScript syntax checks pass. Statewide hierarchy audit reports zero orphan, wrong-parent, duplicate or cross-district leakage findings.

Browser verification and HTTP endpoint checks are part of the release gate. Permanent public deployment is a separate infrastructure outcome and must not be inferred from local browser success or a temporary tunnel.

## 40. Mathematical audit, limitations and future India expansion

The mathematical audit confirms units and accounting must match the sector graph. Generic sectors use monetary flow with a margin share; dairy uses litres with INR/litre contribution. The uncertainty engine now accepts explicit unit price and variable cost so physical dairy flow is not normalized incorrectly.

Remaining limitations include partial coordinate/OSM coverage, incomplete official LGD acquisition, incomplete historical crosswalks, no complete locality enterprise census, unknown current prices/rents/wages/routes in many areas, proxy competitor coverage, uncalibrated scenario distributions and finite candidate enumeration.

India expansion should begin only after an authoritative current geography layer, state-specific official datasets, freshness audit and regression suite are available. The architecture can generalize; the current evidence claims remain West Bengal only.

Coverage of the requested master topics is complete across Sections 1-40: executive/problem/philosophy/workflow (1-3), geography/crosswalk/Bardhaman (4-6), data/freshness/evidence (7-8), HCES/ASUSE/models (9-11), population/demand/supply/price/customer/competitor/factors/weather (12-17), sectors/dairy (18-19), graph/flow/bottleneck/min-cut/reliability/counterfactual (20-22), facility/routing/inventory (23), MVV/exact oracle/inverse/relaxation/Pareto (24-27), costs/unit economics/digital twin/finance (28-30), scenarios/CVaR/sensitivity/failure boundaries (31-33), SWOT/pre-mortem/niche/staging (34-35), UI/visuals/customer PDF/cases/tests/performance/limits/expansion (36-40).

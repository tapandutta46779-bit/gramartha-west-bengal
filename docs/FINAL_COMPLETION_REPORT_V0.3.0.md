# SIH26091 Final Completion Report — v0.3.0

Audit date: 2026-08-28 (Asia/Kolkata)

## Outcome

The product is a working West Bengal evidence, spatial-network, optimization and finance-screening
system with real survey processing, trained model artifacts, geographic holdout metrics, production
survey priors, HTTP UI, and fail-closed decision gates. It does not issue a 2026 venture
recommendation when current business-critical evidence is unavailable.

## Exact geographic coverage

- Operational identity store: 53,537 West Bengal village/town/ward identities.
- Census 2011 Location Code Directory: 41,154 West Bengal rows from state code 19.
- Census PCA: all 19 West Bengal districts as defined in 2011; 179,148 population/household/sex
  evidence records.
- Livestock: 40,475 source identities and 202,375 species records across all 23 publisher district
  labels present in the West Bengal extract.
- OSM: statewide regional extract with 633,601 road ways, 17,212 POIs/places and 381 admin areas.
- HCES/ASUSE: district/sector survey priors cover 23 current-survey district groups. They are
  regional sampled estimates and are not exact locality observations.

Statewide geography and routing coverage must not be read as statewide economic completeness.

## Datasets, periods and freshness

| Dataset / variable | Period | Status | Permitted decision use |
|---|---|---|---|
| Census geography and PCA | 2011 | `HISTORICAL_BASELINE` | Structural identity and historical population only. |
| 20th Livestock Census | 2019 | `STALE_FOR_DECISION` | Historical stock context; not current reachable milk supply. |
| HCES | 2022-23 | `STALE_FOR_DECISION` | Comparison wave only. |
| HCES | Aug 2023-Jul 2024 | `RECENT` | District/rural-urban consumption prior; never exact village demand. |
| ASUSE | Oct 2023-Sep 2024 | historical comparison | Aggregate comparison priors. |
| ASUSE | Jan-Dec 2025 | `RECENT` | District/sector/NIC2 enterprise prior; not competitor capacity. |
| BAHS | 2025 publication | `RECENT` state context | State yield context only; not locality supply. |
| OSM publisher snapshot | retrieved 2026-08-27 | `CURRENT` structural proxy | Catchments/routing/POI proxies with completeness caveat. |
| PMMY | Tarun Plus effective 2024-10-24; page updated 2026-02-05 | `CURRENT` | Category/sector/collateral screening only. |
| AHIDF / IDF | temporary continuation 2026-04-01 to 2026-09-30 | `CURRENT` | Conditional scheme screen; portal/lender confirmation required. |
| Current local selling/procurement price | unavailable | `UNKNOWN` | Blocking. |
| Fuel/transport cost and incumbent capacity | unavailable | `UNKNOWN` | Blocking. |
| CAPEX/OPEX, wage and rent | unavailable | `UNKNOWN` | Blocking. |
| Current locality population/projection | unavailable | `UNKNOWN` | Blocking; no 2011 value is relabelled as 2026. |
| Current lender rate/tenure/underwriting | lender-specific and unavailable | `UNKNOWN` | Blocking. |

No 2026 population projection is stored. Therefore no projection method, central/lower/upper value
or uncertainty is claimed.

## Restricted raw archives

| Archive | Bytes | SHA-256 |
|---|---:|---|
| HCES 2022-23 CSV | 244,317,752 | `093a51d337eb07eede7d6e2a00ec55790d926bacf869be2cf2825abd629444ae` |
| HCES 2023-24 CSV | 256,315,433 | `acf7b9cc840676fb812c05c48f09fa034955fe2cad5112e6d9b6d852f5f2e267` |
| ASUSE 2023-24 CSV | 98,219,217 | `82a2e59aab71fee6dda7cd5f859c7cfbcf5e23ddf70b36a5a2962296b838de54` |
| ASUSE calendar-2025 CSV | 173,738,167 | `f20b35abdb7ba97daaca24f4b927a277e95e1145fcbe86b2bd97304f771dc591` |

All four passed full member CRC checks. They remain applicant-only and are not included in the
public-share package.

## Models actually trained and validated

Validation is leave-one-district-out across 23 West Bengal district groups.

### HCES household liquid-milk target

- Rows: 18,120; zero targets: 7,560.
- Target: zero-inclusive monthly liquid-milk litres per household member.
- Weighted category-mean baseline: MAE 1.384585; RMSE 1.748752.
- Ridge one-hot: MAE 1.367413; RMSE 1.733946.
- Random forest: MAE 1.353607; RMSE 1.724402; weighted bias 0.000133;
  mean calibration ratio 1.000082; decile calibration MAE 0.131882.
- Holdout winner: random forest.

### ASUSE enterprise annual-GVA target

- Rows: 38,626; zero targets: 40.
- Target: annualized enterprise GVA in INR using official item 769 and reference-period rule.
- Weighted category-mean baseline: MAE INR 97,124.15; RMSE INR 259,004.56.
- Ridge one-hot: MAE INR 68,004.76; RMSE INR 197,753.34.
- Random forest: MAE INR 61,573.20; RMSE INR 193,228.67; weighted bias INR 22.54;
  mean calibration ratio 1.000151; decile calibration MAE INR 2,528.68.
- Holdout winner: random forest.

The fitted random forests won the comparison, but both ML inference paths are withheld from normal
locality requests because those requests lack the household/enterprise microfeatures used in
training. Production uses the direct weighted district/sector or district/sector/NIC2 survey
estimator. This is a deliberate applicability decision, not a claim that no model was trained.

## Production algorithm and MVV status

Ordinary flow is locality → stored evidence and regional priors → freshness gates → demand/supply/
price/capacity → OSM catchment → graph → exact min-cost maximum flow → bottleneck → automatic
candidate → exact finite-candidate MVV → finance screen → digital twin/stress when assumptions exist.

- Flow: exact maximum served demand, then minimum economic cost.
- Counterfactual: newly served demand and cannibalized incumbent flow separated.
- MVV: exact exhaustive oracle over supplied candidates; minimum investment with demand/income/
  capital constraints.
- Automatic library: one dairy rented-transport primitive when all source-linked costs/capacities
  exist. No general configuration MILP or complete venture library is claimed.
- Uncertainty: survey confidence intervals and endpoint multiplication are retained. Full correlated
  probabilistic propagation is not implemented.
- Robustness: demand failure boundary and exact minimax regret over an explicit finite table.

## Finance rules and effective dates

- PMMY: official Department of Financial Services page updated 2026-02-05; Tarun Plus up to INR
  20 lakh for successful prior Tarun borrowers, effective 2024-10-24. No universal lender rate,
  tenure or sanction is inferred.
- AHIDF/IDF: temporarily continued from 2026-04-01 through 2026-09-30 or earlier superseding
  approval. Existing terms include 3% interest subvention, lender finance up to 90% of eligible
  cost, and up to eight years including two-year principal moratorium. These are ceilings, not
  promised borrower terms. Live portal, margin, gross/net rate, security and sanction remain gates.

## Real E2E and browser validation

Tested localities: Kolkata; Amdanga (North 24 Parganas); Abad Bhagabanpur (South 24 Parganas);
Kharibari CT (Darjeeling); Anandapur (Jalpaiguri); Adina (Maldah); Adra CT (Purulia).

Each resolved an exact stored geo ID, attached relevant HCES/ASUSE priors, computed a 5 km OSM
catchment and returned `INSUFFICIENT_EVIDENCE` with no graph-generated venture. The UI was also
tested through HTTP in a real Chromium browser using Kolkata: search, evidence loading, freshness,
analysis, finance and source rendering all worked; browser console warnings/errors were zero.

## Final verification

- Ruff: pass.
- Pytest: 36 passed.
- Dataset registry: 53/53 files match byte size and SHA-256.
- Restricted ZIP CRC: 4/4 pass.
- SQLite integrity: pass.
- Model artifact integrity/load: pass.
- ASUSE output-input=GVA: 1,551 groups, max residual `3.725290298461914e-09` INR.
- E2E truth gate: 7/7 cases safe.

## Remaining evidence gates

The product cannot honestly make a real 2026 locality venture recommendation until current local
population/projection, demand calibration, productive/reachable supply, selling/procurement price,
incumbent capacity, transport cost, venture configuration cost, and lender terms are supplied.
It therefore returns uncertainty and explicit gates rather than fabricating those values.

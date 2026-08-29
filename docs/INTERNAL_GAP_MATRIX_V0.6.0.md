# GramArtha v0.6 Internal Gap Matrix

Audit checkpoint: commit `a1349d8`, 2026-08-29 Asia/Kolkata.

This is an implementation control document, not a completion claim. `DONE` means verified in the
current repository. `PARTIAL` means useful behavior exists but the master specification requires a
stronger implementation or evidence base. `GATED` means the requested claim is not scientifically
defensible with current evidence.

| Requirement family | Checkpoint evidence | Gap / required action | Initial status |
|---|---|---|---|
| Repository integrity | Clean `main`; 50 pytest; Ruff and JS syntax pass | Preserve commits and prior releases | DONE |
| Current geography | 53,537 mixed-era identities; 35 source district spellings | Add explicit current, historical and crosswalk layers | IN PROGRESS |
| Current districts | 23 displayed labels include old Barddhaman and omit Purba Bardhaman | Canonical 23 current districts, exactly once | DEFECT |
| Bardhaman split | Old district is blocked instead of crosswalked | Crosswalk safe exact parent/locality matches; never guess ambiguous rows | DEFECT |
| Other reorganizations | Aliases exist but no era-aware mapping | Audit Alipurduar, Kalimpong, Jhargram and spelling changes | PARTIAL |
| Subordinate hierarchy | Block/municipality fields live inside payload only | Build parent entities and audit orphans/duplicates/conflicts | PARTIAL |
| Search | District-scoped substring search | Ranked exact/alias/prefix/token/fuzzy with type filter and parent card | PARTIAL |
| Coordinate safety | 3,320 containment-validated OSM matches; 6,952 withheld | Preserve anti-name-only rules and audit canonical layer | DONE WITH COVERAGE GAP |
| Evidence freshness | Explicit statuses and version metadata exist | Add BENCHMARK_ADJUSTED consistently and expose estimate level | PARTIAL |
| Population | Explicit 2011-to-2026 scenario projection exists | Connect provenance and current-geography level in every response | PARTIAL |
| Profile parsing | Blank inputs become zero; optional dict is accepted | Reproduce desired-income/debt cases; make blank null and constraints explicit | DEFECT RISK |
| Income/debt optimization | MVV checks income and available capital | Debt ceiling, binding constraints, inverse maxima/minima and relaxation missing | PARTIAL |
| Sector library | Ten real benchmark adapters plus gated dairy | Add farming/fishery/textile/CSC/last-mile only with real adapter factors | PARTIAL |
| Dairy | Physical/current evidence gates remain | Strongest defensible estimated planning path plus explicit user inputs; no fake current price | GATED/PARTIAL |
| Factor registry | Factors embedded in prose/config | Create typed per-sector registry and integrate risk/plan output | MISSING |
| Competitors | OSM proxy count/categories | Direct/indirect candidates, distances, dedupe, intensity and confidence | PARTIAL |
| Markets/channels | Nearest market and route exist | Supplier/institution/channel scoring and output | PARTIAL |
| Flow/bottleneck | Exact min-cost maximum flow and marginal bottleneck tests | Add reliability/min-cut output only where graph supports it | PARTIAL |
| Venture/MVV | Exact exhaustive selection over starter/growth candidates | Add structured scale/config search and oracle comparison; avoid false MILP claim | PARTIAL |
| Working capital/unit economics | CCC fields, margin, BE volume, NPV/IRR exist | WC stress buffer, DSCR/interest coverage when loan inputs exist | PARTIAL |
| Uncertainty | 512 seeded triangular joint scenarios, CVaR/regret/Pareto | Convergence benchmark, assumption labels, adaptive boundaries, sensitivities | PARTIAL |
| SWOT/advice | Computed section exists but some metadata wording remains | Business-economic SWOT, pre-mortem, channels and stop thresholds | DEFECT |
| UI | Seven stages and deep results tabs | Real progress semantics, richer visuals, constraints/errors and multilingual copy | PARTIAL |
| Customer PDF | Master report exists only | Generate analysis-specific downloadable PDF | MISSING |
| Master PDF | 31-page v0.5 report visually verified | New 35-60 page v0.6 report after implementation and final audit | MISSING |
| Statewide validation | 23 HTTP smoke checks; seven deep cases | Canonical geography audit plus profile/asset/zero-debt/dairy cases | PARTIAL |
| Deployment | Temporary Cloudflare quick tunnel only | Permanent hosting needs a hosting-account connection and suitable data storage | HUMAN AUTH GATE |
| Drive delivery | Drive contains v0.3 package, not v0.5 | Upload and verify new v0.6 package and sharing state | MISSING |

## Scientific non-negotiables

- LGD download currently presents a CAPTCHA. Until an official current LGD extract is acquired,
  the canonical product layer must be labelled a current product crosswalk derived from the
  post-split DS057 publisher hierarchy, not an official complete LGD hierarchy.
- Restricted HCES/ASUSE respondent records and private fitted artifacts remain outside public
  packages.
- Generic sector cases remain `MODELLED_BENCHMARK`; scenario survival is model survival under
  stated assumptions, not real business success probability.
- Current local prices, rents, wages, supplier capacity and lender quotes cannot be fabricated.

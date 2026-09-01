# SIH26091 Judge Walkthrough — GramArtha

This page is the shortest five-minute path through the repository and product. It is designed for a reviewer who wants to distinguish implemented engineering from presentation claims.

> **Only have one minute?** Start with [`60_SECOND_JUDGE_VIEW.md`](60_SECOND_JUDGE_VIEW.md): **Start with reality → Repair the network → Test financial survival.**

## The one-sentence idea

**GramArtha models a rural micro-enterprise as a repair to a local economic network, then searches for the smallest financially survivable venture configuration that closes a measured structural gap.**

The language layer may structure intake or explain a completed result. The decision core is evidence-backed and deterministic/explicitly modelled: geography → evidence → economic graph → exact flow/bottleneck → counterfactual repair → Minimum Viable Venture → finance/digital twin → uncertainty/robust selection.

## What to inspect first

| Time | Show | What this proves |
|---:|---|---|
| 0:00–0:40 | Repository README hero and product/release entry points | The project has a concrete hosted + downloadable product, measurable evidence scale and a defined technical core |
| 0:40–1:20 | Product **Setup** + canonical locality selection | Decisions begin from a resolved West Bengal geography, not a free-text place name |
| 1:20–2:00 | **Local Market** / evidence view | Evidence and spatial context are visible before the recommendation |
| 2:00–3:10 | Run **Deep — 512 scenarios** and open the recommendation | The result is generated through graph/venture/finance/risk modules rather than a one-shot text answer |
| 3:10–4:10 | Finance + downside/failure information | A venture is tested month by month; affordability is not reduced to a static EMI calculation |
| 4:10–5:00 | **How did GramArtha decide?** audit panel + validation docs | Provenance, assumptions, limitations and methodology remain reviewable |

## The seven product stages and the computation underneath

| UI stage | Entrepreneur-facing purpose | Engine computation |
|---|---|---|
| **1 · Setup** | Select locality, capital and planning profile | Canonical geographic identity + entrepreneur constraints |
| **2 · Local Market** | Inspect local evidence and spatial context | Provenance/freshness/confidence + OSM/catchment evidence + readiness gates |
| **3 · Opportunities** | See candidate gaps/opportunities | Economic graph + exact flow + residual demand + bottleneck + candidate repairs |
| **4 · Risk** | Understand downside and failure conditions | 512 deterministic seeded scenarios + VaR/CVaR + regret + failure boundaries |
| **5 · Plan** | Get the smallest viable operating configuration | Counterfactual recomputation + cannibalization accounting + enumerated MVV search |
| **6 · Finance** | See scheme fit and monthly cash reality | Scheme/rule checks + loan arithmetic + 36-month financial digital twin |
| **7 · Action** | Launch in stages using measurable triggers | Frozen decision + staged triggers + multilingual/web/PDF presentation |

This mapping is the fastest way to show that the seven-screen workflow is not decorative navigation: every user-facing stage corresponds to a specific computation or evidence boundary.

## The four questions GramArtha answers

### 1. What is actually known about this locality?

GramArtha resolves a canonical geography and preserves evidence provenance, observation/freshness context and confidence. It does not intentionally collapse stale, estimated, sampled or conflicting information into a fabricated present-day fact.

Repository locations:

- `backend/evidence/`
- `backend/spatial/`
- `docs/DATA_ARCHITECTURE.md`
- `docs/DATA_SOURCES_ACQUIRED.md`
- `docs/LIMITATIONS.md`

### 2. Where is the structural economic gap?

The engine models economic relationships rather than using “few nearby competitors” as a sufficient opportunity signal. It evaluates reachable supply/demand, flow and bottlenecks, and can recompute the local graph after a candidate repair is inserted.

Repository locations:

- `backend/engine/`
- `backend/pipeline/`

Key concepts to ask about:

- exact flow
- residual unserved demand
- bottleneck ranking
- counterfactual recomputation
- venture primitives / graph repair

### 3. What is the smallest venture worth attempting?

GramArtha searches an enumerated venture space for a **Minimum Viable Venture (MVV)** rather than assuming full-scale launch on day one. The target is a configuration that captures sufficient local opportunity while respecting entrepreneur and financial constraints.

This is what differentiates “start a transport business” from a structured recommendation such as a bounded operating scale, required assets, served clusters and cash buffer.

### 4. Does the venture survive financial reality?

The finance layer goes beyond scheme eligibility and EMI arithmetic. It includes a 36-month cash-flow digital twin, working-capital analysis, stress conditions, failure boundaries and robust/minimum-regret comparison across deterministic scenarios.

Repository locations:

- `backend/finance/`
- robustness/uncertainty components under `backend/engine/`

## Current repository-verifiable proof

| Item | Current proof |
|---|---|
| Geographic identities | 53,537 in the audited implementation snapshot |
| Locality evidence records | 381,523 in the audited implementation snapshot |
| Regional priors | 976 |
| Deep uncertainty run | 512 deterministic seeded triangular joint scenarios |
| Financial horizon | 36 months |
| Languages | English, Bengali and Hindi output/reporting |
| Automated tests | 68 passing on current CI |
| Runtime checks | public runtime preparation, SQLite integrity and `/health` smoke test |
| Release | verified `v0.7.2` software release + downloadable Judge Package |
| Security checks | CodeQL, pip-audit, Bandit and Gitleaks |

## SIH26091 mapping

| Requirement family | Where GramArtha addresses it |
|---|---|
| Multilingual business advisory | presentation/reporting layer; English/Bengali/Hindi outputs |
| Hyper-local feasibility | canonical geography + evidence + OSM spatial context + economic graph |
| Smart financial calculator | deterministic finance calculations and 36-month digital twin |
| Government scheme routing | explicit scheme/rule layer |
| Catchment / competitor mapping | OSM-derived local context with completeness caveats |
| Actionable recommendation | MVV + staged launch/expansion triggers |
| AI-enabled experience | optional language structuring/explanation around a non-LLM decision core |

## Recommended judge questions

These are useful questions because the answer can be checked against source code rather than marketing copy:

1. **Where exactly can the LLM change the selected venture?** It should not be able to silently replace the frozen decision.
2. **What happens when evidence is missing or stale?** Look for qualification/gating rather than fabricated precision.
3. **How is an opportunity different from “low competitor count”?** Ask for residual demand, flow or bottleneck reasoning.
4. **What does counterfactual recomputation do?** Ask how the graph changes after inserting a candidate venture.
5. **Why MVV instead of maximum loan / full-scale launch?** Ask which constraints bound the chosen configuration.
6. **What does the digital twin reveal that EMI does not?** Look for monthly cash/working-capital failure.
7. **What is empirically calibrated versus scenario-based?** The project should preserve that distinction.

## Reproduce locally

For the fastest evaluator path, use the downloadable `v0.7.2` Judge Package from the repository release. For development from source:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
bash deploy/start.sh
```

Open `http://127.0.0.1:10000/ui/`.

Verification:

```bash
ruff check backend scripts tests deploy
pytest
python -m compileall -q backend scripts deploy
node --check frontend/app.js
```

## Where to go deeper

- `docs/60_SECOND_JUDGE_VIEW.md` — one-minute concept + user-stage/engine-stage map
- `docs/IMPLEMENTATION_STATUS.md` — implemented vs incomplete surfaces
- `docs/VALIDATION.md` — validation methodology and cases
- `docs/LIMITATIONS.md` — evidence/model/product caveats
- `docs/DATA_ARCHITECTURE.md` — data/rebuild architecture
- `DATA_LICENSES.md` — third-party licensing boundaries
- `SECURITY.md` — security reporting

---

**The intended evaluation standard is simple: do not reward GramArtha because the README sounds sophisticated. Follow one decision from locality evidence through graph repair, finance and auditability, and verify that the source code supports the story.**

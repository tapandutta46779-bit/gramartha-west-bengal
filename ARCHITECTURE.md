# GramArtha Architecture & System Maps

> **Purpose:** these diagrams explain the implemented business-decision architecture and economic-network system. They are **system maps**, not a future-development roadmap.

[🚀 Open the public app](https://gramartha-west-bengal.onrender.com/ui/) · [🎯 5-minute SIH judge walkthrough](docs/SIH_JUDGE_WALKTHROUGH.md) · [✅ Validation](docs/VALIDATION.md) · [🔎 Limitations](docs/LIMITATIONS.md)

---

## 1. Business & Decision Architecture

This map shows how GramArtha connects its core philosophy, technical layers, entrepreneur journey, AI boundary, robustness layer, and SIH26091-facing requirements.

```mermaid
flowchart LR
    GA["🌾 GramArtha"]

    GA --> CP["Core Philosophy"]
    CP --> CP1["Economic Network Repair"]
    CP --> CP2["Minimum Viable Venture (MVV)"]
    CP --> CP3["Evidence-Backed Engine"]
    CP --> CP4["Deterministic Decision Core"]

    GA --> TL["Technical Layers"]
    TL --> EG["Evidence & Geography"]
    EG --> EG1["Canonical Identity"]
    EG --> EG2["Source Provenance"]
    EG --> EG3["Freshness Monitoring"]
    EG --> EG4["Confidence States"]

    TL --> EM["Economic Modeling"]
    EM --> EM1["Flow Graph Analysis"]
    EM --> EM2["Structural Bottlenecks"]
    EM --> EM3["Residual Demand"]
    EM --> EM4["Reachable Supply"]

    TL --> VS["Venture Synthesis"]
    VS --> VS1["Venture Primitives"]
    VS --> VS2["Counterfactual Repair"]
    VS --> VS3["Search Algorithms"]
    VS --> VS4["Feasibility Constraints"]

    TL --> FE["Financial Engineering"]
    FE --> FE1["36-Month Digital Twin"]
    FE --> FE2["Scheme Routing"]
    FE --> FE3["Stress Test Scenarios"]
    FE --> FE4["Working Capital Analysis"]

    GA --> UJ["7-Stage User Journey"]
    UJ --> UJ1["1. Setup & Profile"]
    UJ --> UJ2["2. Local Market Evidence"]
    UJ --> UJ3["3. Opportunity Detection"]
    UJ --> UJ4["4. Risk & Failure Boundaries"]
    UJ --> UJ5["5. Operating Plan"]
    UJ --> UJ6["6. Financial Roadmap"]
    UJ --> UJ7["7. Staged Action Triggers"]

    GA --> AI["AI Boundary"]
    AI --> AI1["Multilingual Explanation"]
    AI --> AI2["NLP Input Structuring"]
    AI --> AI3["Deterministic Logic Lock"]
    AI --> AI4["Hallucination Prevention"]

    GA --> RR["Risk & Robustness"]
    RR --> RR1["Minimum-Regret Selection"]
    RR --> RR2["Staged Expansion"]
    RR --> RR3["VaR / CVaR Analysis"]
    RR --> RR4["Failure Boundary Testing"]

    GA --> PS["SIH26091 Requirements"]
    PS --> PS1["Business Feasibility Study"]
    PS --> PS2["Smart Financial Calculator"]
    PS --> PS3["Multilingual PDF Output"]
    PS --> PS4["Competitor Mapping"]

    classDef root fill:#123f32,stroke:#55c9a8,color:#fff,stroke-width:3px;
    classDef group fill:#dbeafe,stroke:#60a5fa,color:#0f172a,stroke-width:2px;
    classDef layer fill:#ccfbf1,stroke:#5eead4,color:#0f172a;
    classDef item fill:#dcfce7,stroke:#86efac,color:#0f172a;
    class GA root;
    class CP,TL,UJ,AI,RR,PS group;
    class EG,EM,VS,FE layer;
    class CP1,CP2,CP3,CP4,EG1,EG2,EG3,EG4,EM1,EM2,EM3,EM4,VS1,VS2,VS3,VS4,FE1,FE2,FE3,FE4,UJ1,UJ2,UJ3,UJ4,UJ5,UJ6,UJ7,AI1,AI2,AI3,AI4,RR1,RR2,RR3,RR4,PS1,PS2,PS3,PS4 item;
```

### What this map communicates

- **Core philosophy:** GramArtha repairs a local economic-network gap rather than generating a generic business list.
- **Evidence discipline:** canonical identity, provenance, freshness, and confidence remain explicit inputs to the decision.
- **Venture synthesis:** candidate ventures are treated as graph repairs and tested under feasibility constraints.
- **Finance:** the recommendation is carried into a 36-month digital twin, scheme routing, stress tests, and working-capital analysis.
- **AI containment:** language AI is used for intake/explanation while the decision core remains deterministic or explicitly modelled.
- **Robustness:** the final recommendation is compared under failure boundaries, VaR/CVaR-style downside summaries, staged expansion, and minimum-regret logic.

---

## 2. Economic Network & Implementation System Map

This map focuses on how evidence becomes a local economic graph, then a differentiated venture decision and financial action.

```mermaid
flowchart LR
    GA["🌾 GramArtha: Economic Network Repair"]

    GA --> PA["Project Architecture"]
    PA --> PA1["Evidence & Geographic Identity"]
    PA --> PA2["Transparent Estimation with Uncertainty"]
    PA --> PA3["Economic Graph & Flow Analysis"]
    PA --> PA4["Deterministic Finance & Digital Twin"]

    GA --> PS["Official PS Requirements · SIH26091"]
    PS --> PS1["Multilingual NLP Business Advisory"]
    PS --> PS2["Hyper-Local Feasibility Study"]
    PS --> PS3["Smart Financial Calculator"]
    PS --> PS4["Government Scheme Routing"]
    PS --> PS5["Catchment / Competitor Mapping"]

    GA --> DC["Differentiating Decision Core"]
    DC --> DC1["Economic Network Flow Modeling"]
    DC --> DC2["Structural Bottleneck Detection"]
    DC --> DC3["Minimum Viable Venture (MVV) Search"]
    DC --> DC4["Venture Primitives & Graph Repairs"]
    DC --> DC5["Robust Minimum-Regret Selection"]

    GA --> WF["System Workflow Stages"]
    WF --> WF1["Setup"]
    WF --> WF2["Local Market"]
    WF --> WF3["Opportunities"]
    WF --> WF4["Risk"]
    WF --> WF5["Plan"]
    WF --> WF6["Finance"]
    WF --> WF7["Action"]

    GA --> DEM["Data & Evidence Model"]
    DEM --> ES["Entrepreneur State"]
    ES --> ES1["Available Margin Capital"]
    ES --> ES2["Skills & Assets"]
    ES --> ES3["Experience & Risk Tolerance"]

    DEM --> EI["Evidence Integrity"]
    EI --> EI1["Source Provenance"]
    EI --> EI2["Confidence Status: Observed · Estimated · Stale"]

    DEM --> GN["Economic Graph Nodes"]
    GN --> GN1["Producer & Customer Clusters"]
    GN --> GN2["Markets & Processing Points"]
    GN --> GN3["Transport & Storage"]

    GA --> FDL["Financial Decision Layer"]
    FDL --> FDL1["Official Scheme Eligibility"]
    FDL --> FDL2["Monthly Cash Flow Simulation"]
    FDL --> FDL3["Stress Testing Failure Boundaries"]
    FDL --> FDL4["Staged Expansion Triggers"]
    FDL --> FDL5["Working Capital Gap Analysis"]

    GA --> SM["Software Modules"]
    SM --> SM1["NLP Intake & Clarification"]
    SM --> SM2["Evidence & Graph Builder"]
    SM --> SM3["Flow & Bottleneck Engines"]
    SM --> SM4["Repair Generator & MVV Optimizer"]
    SM --> SM5["Explanation & Monitoring Service"]

    classDef root fill:#123f32,stroke:#55c9a8,color:#fff,stroke-width:3px;
    classDef group fill:#dbeafe,stroke:#60a5fa,color:#0f172a,stroke-width:2px;
    classDef layer fill:#ccfbf1,stroke:#5eead4,color:#0f172a;
    classDef item fill:#dcfce7,stroke:#86efac,color:#0f172a;
    class GA root;
    class PA,PS,DC,WF,DEM,FDL,SM group;
    class ES,EI,GN layer;
    class PA1,PA2,PA3,PA4,PS1,PS2,PS3,PS4,PS5,DC1,DC2,DC3,DC4,DC5,WF1,WF2,WF3,WF4,WF5,WF6,WF7,ES1,ES2,ES3,EI1,EI2,GN1,GN2,GN3,FDL1,FDL2,FDL3,FDL4,FDL5,SM1,SM2,SM3,SM4,SM5 item;
```

### Decision path in one line

**Entrepreneur state + qualified local evidence → economic graph → exact flow / bottleneck → counterfactual venture repair → MVV → 36-month finance + stress → robust staged action.**

---

## Where the implementation lives

| Layer | Main repository areas |
|---|---|
| Evidence, geography, freshness | `backend/evidence/`, `backend/spatial/` |
| Economic graph, flow, bottlenecks, counterfactuals | `backend/engine/` |
| Venture synthesis / pipeline | `backend/engine/`, `backend/pipeline/` |
| Financial decision layer | `backend/finance/` |
| Multilingual presentation & reporting | `backend/presentation/`, `backend/reporting/` |
| API and product workflow | `backend/api/`, `frontend/` |
| Validation | `tests/`, `docs/VALIDATION.md` |

## Related technical references

- [`README.md`](README.md) — product-first overview and live app
- [`docs/SIH_JUDGE_WALKTHROUGH.md`](docs/SIH_JUDGE_WALKTHROUGH.md) — judge-oriented 5-minute demo path
- [`docs/IMPLEMENTATION_STATUS.md`](docs/IMPLEMENTATION_STATUS.md) — implemented vs. limited surfaces
- [`docs/DATA_ARCHITECTURE.md`](docs/DATA_ARCHITECTURE.md) — provenance and rebuild path
- [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md) — evidence and modelling caveats
- [`DATA_LICENSES.md`](DATA_LICENSES.md) — data/asset licensing boundaries

# GramArtha documentation index

This index separates the **current judge/reviewer path** from implementation references and historical audits. Start here instead of browsing the documentation directory alphabetically.

## Start here

| Document | Purpose |
|---|---|
| [`../README.md`](../README.md) | Product overview, live app, proof surfaces and quick start |
| [`../ARCHITECTURE.md`](../ARCHITECTURE.md) | Complete business, decision and implementation system maps |
| [`SIH_JUDGE_WALKTHROUGH.md`](SIH_JUDGE_WALKTHROUGH.md) | Five-minute SIH evaluation route |
| [`IMPLEMENTATION_STATUS.md`](IMPLEMENTATION_STATUS.md) | Implemented, partial and intentionally bounded surfaces |
| [`VALIDATION.md`](VALIDATION.md) | Automated, E2E and geographic validation evidence |
| [`LIMITATIONS.md`](LIMITATIONS.md) | Evidence, calibration and product limitations |
| [`RELEASING.md`](RELEASING.md) | Verified software release policy, SBOM/checksum/runtime-boundary process |

## Evidence, geography and data

- [`DATA_ARCHITECTURE.md`](DATA_ARCHITECTURE.md) — provenance-preserving data architecture and rebuild path.
- [`DATA_SOURCES_ACQUIRED.md`](DATA_SOURCES_ACQUIRED.md) — acquired-source inventory.
- [`MICRODATA_IMPORT.md`](MICRODATA_IMPORT.md) — restricted survey import boundary.
- [`WEST_BENGAL_GEO_CROSSWALK.md`](WEST_BENGAL_GEO_CROSSWALK.md) — geography crosswalk notes.
- [`DATA_GAPS.md`](DATA_GAPS.md) — known evidence gaps.
- [`PHASE2_CURRENT_STATE_AUDIT.md`](PHASE2_CURRENT_STATE_AUDIT.md) — current-state evidence audit.
- [`CATCHMENT_ROUTING.md`](CATCHMENT_ROUTING.md) and [`COMPETITOR_CAPACITY.md`](COMPETITOR_CAPACITY.md) — spatial/capacity methodology.

## Decision engine references

- [`FLOW_MODEL.md`](FLOW_MODEL.md) — exact flow model.
- [`BOTTLENECK_MODEL.md`](BOTTLENECK_MODEL.md) — structural bottleneck definition.
- [`MVV_ALGORITHM.md`](MVV_ALGORITHM.md) — Minimum Viable Venture search boundary.
- [`VENTURE_GENERATION.md`](VENTURE_GENERATION.md) — venture primitive generation.
- [`DEMAND_MODEL.md`](DEMAND_MODEL.md), [`SUPPLY_MODEL.md`](SUPPLY_MODEL.md), [`PRICE_MODEL.md`](PRICE_MODEL.md) — core modelled quantities.
- [`DIGITAL_TWIN.md`](DIGITAL_TWIN.md) — 36-month monthly financial simulation.
- [`STRESS_ENGINE.md`](STRESS_ENGINE.md) — downside/stress mechanics.
- [`ROBUST_SELECTION.md`](ROBUST_SELECTION.md) — robust/minimum-regret selection.
- [`FINANCE_ENGINE.md`](FINANCE_ENGINE.md) and [`FINANCE_RULES.md`](FINANCE_RULES.md) — financial calculations and scheme rules.

## Product and API

- [`API.md`](API.md) — API surface.
- [`PERFORMANCE.md`](PERFORMANCE.md) — performance notes.
- [`design-qa/README.md`](design-qa/README.md) — current visual/interaction QA evidence.

## Versioned and historical audits

These files are retained for traceability. Their version numbers are historical and **must not be read as the current v0.7.2 implementation status**:

- `FINAL_COMPLETION_REPORT_V0.3.0.md`
- `PRODUCTIZATION_V0.4.0.md`
- `GRAMARTHA_DEEP_ENGINE_REPORT_V0.5.0.md`
- `GRAMARTHA_MASTER_TECHNICAL_REPORT_V0.6.0.md`
- `INTERNAL_GAP_MATRIX_V0.6.0.md`
- `REQUIREMENT_AUDIT_V0.6.0.md`
- `FINAL_POLISH_REQUIREMENT_AUDIT_V0.7.0.md`
- `FULL_DETAIL_LOCALIZATION_AUDIT_V0.7.1.md`
- `OSM_RUNTIME_REGRESSION_FIX_V0.7.1.md`
- `EXISTING_REPOSITORY_AUDIT.md`
- `WEST_BENGAL_DATA_IMPLEMENTATION_PLAN.md`

Historical public-share package manifests remain under `deliverables/` for auditability; the live repository and tagged release workflow are the authoritative current software surfaces.

## Licensing and security

Licensing and security policy intentionally live at repository root because GitHub surfaces them directly:

- [`../LICENSE`](../LICENSE) — MIT license for original GramArtha source code.
- [`../DATA_LICENSES.md`](../DATA_LICENSES.md) — third-party data/asset licensing boundaries.
- [`../NOTICE.md`](../NOTICE.md) — attribution notices.
- [`../SECURITY.md`](../SECURITY.md) — vulnerability reporting and security boundaries.

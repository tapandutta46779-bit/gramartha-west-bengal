# Validation

**Current product:** GramArtha v0.7.2  
**Current-status refresh:** 2026-09-01

This page separates the **current continuously verified software baseline** from earlier deep audit snapshots. Historical validation remains useful evidence, but its old version number must not be mistaken for the current product version.

## Current v0.7.2 verification baseline

The current repository quality/release path verifies the following:

- **68/68 automated tests passing** on the measured v0.7.2 CI baseline.
- **81.6% backend line coverage** and **61.4% branch coverage** on that measured baseline.
- CI enforces a **minimum 75% combined coverage gate**.
- Ruff and Python compilation run in CI.
- Frontend JavaScript syntax is checked with Node.
- Public runtime databases are reconstructed from committed deployment assets and checked with SQLite `PRAGMA integrity_check`.
- FastAPI is booted against the reconstructed public runtime and `/health` is smoke-tested.
- Repository hygiene and important local Markdown links are validated automatically.
- Security automation includes **CodeQL for Python and JavaScript, pip-audit, Bandit and Gitleaks**.
- The verified `v0.7.2` release pipeline builds the Python wheel and source distribution, installs the built wheel in a clean environment, creates the judge-ready runtime package, scans the archive boundary, generates a CycloneDX SBOM, and publishes SHA-256 checksums and a release manifest.

The current evaluator product is available both as the hosted web application and as the verified `GramArtha-v0.7.2-Judge-Package.zip` release asset.

## Deep geographic / data audit evidence retained from earlier versions

A detailed validation run on 2026-08-28 established the following evidence. These results remain historical audit records rather than a claim that the current CI reruns every expensive acquisition/audit step on each push:

- All 53 registry objects in that audit matched their recorded byte size and SHA-256.
- Four restricted HCES/ASUSE ZIP archives passed full member CRC checks.
- SQLite `PRAGMA integrity_check` returned `ok` for **53,537 geographies**, **381,523 locality evidence records** and **976 regional priors**.
- Both trained-task artifact sets loaded successfully and matched their registry checksums.
- ASUSE weighted `annual_output - annual_input = annual_GVA` held over 1,551 groups; maximum absolute floating residual was `3.725290298461914e-09` INR.
- Real E2E localities included Kolkata (Kolkata), Amdanga (North 24 Parganas), Abad Bhagabanpur (South 24 Parganas), Kharibari CT (Darjeeling), Anandapur (Jalpaiguri), Adina (Maldah) and Adra CT (Purulia).
- In the earlier strict evidence-gating audit, all seven cases resolved exact geo IDs, received regional survey priors and computed OSM catchments; where required current evidence was absent, the engine refused to silently fabricate a decision-ready venture.
- The HTTP UI was exercised in Chromium for search, locality selection, evidence, analysis, freshness labels, evidence gates and PMMY/AHIDF screens; UI/OpenAPI endpoints returned HTTP 200 and the recorded browser run contained zero console warnings/errors.

Later versioned E2E, localization, OSM and PDF-QA evidence is retained under `outputs/`, `output/validation/` and the versioned audit documents indexed by [`docs/README.md`](README.md).

## What the validation does **not** prove

Passing software tests do not prove that every locality has complete current market observations, that scenario probabilities are empirically calibrated, that a recommended venture is guaranteed to survive, or that government/lender scheme screening implies sanction. Those boundaries are documented in [`LIMITATIONS.md`](LIMITATIONS.md) and [`IMPLEMENTATION_STATUS.md`](IMPLEMENTATION_STATUS.md).

Machine-readable historical evidence includes `FINAL_TECHNICAL_AUDIT.json`, `WEST_BENGAL_MULTI_DISTRICT_E2E.json`, the committed validation outputs, and `models/model_registry.json` where available in the relevant audit/package context.

# Existing Repository Audit

Audit date: 2026-08-27 (Asia/Kolkata)

## Executive finding

This workspace is a research and data-acquisition foundation, not yet a runnable SIH26091 software repository. It has no Git metadata, application package, backend, frontend source, database migrations, or automated test suite. Useful research and acquired West Bengal artifacts must be preserved and integrated into a new deterministic backend.

## Classification

| Path / asset | Classification | Evidence and action |
|---|---|---|
| `outputs/SIH26091_data_foundation/dataset_registry.csv` and `.json` | KEEP + REFACTOR | 100-source catalogue with provenance and use mappings. Migrate into `data/metadata`; correct stale acquisition state after storage cleanup. |
| `outputs/SIH26091_data_foundation/storage_manifest.csv` | KEEP + REFACTOR | Exact sizes/checksums for earlier acquisitions, but DS058 and DS097 still say acquired even though their Drive bytes were intentionally deleted during regional cleanup. Add current-state/event semantics. |
| `outputs/SIH26091_data_foundation/scripts/` | KEEP + REFACTOR | Reusable downloader patterns, dry-run defaults, verification and storage recording. Move reusable logic into project `scripts/`/adapters; do not duplicate compiled caches. |
| `outputs/SIH26091_data_foundation/*.md` and report PDF | KEEP | Source catalogue, data-to-algorithm map, gap analysis, geographic and storage plans. Reference documentation, not proof of data ingestion. |
| `outputs/SIH26091_KOLKATA_SOUTH_BENGAL/DS057_West_Bengal_Kolkata_South_Bengal_Livestock_Localities.xlsx` | KEEP | Validated 18,326-row regional locality/ward extract; exact local and Drive size 755,765 bytes; source hash and filter recorded. First real evidence adapter target. |
| `work/raw_stage/DS046/raw_originals/*west*` and `*SIP_ WB*` | KEEP | Two authentic official West Bengal MSME profile PDFs with recorded hashes and matching Drive sizes. |
| `work/raw_stage/DS071_WEST_BENGAL/west_bengal.pbf` | REFACTOR / INCOMPLETE | Interrupted regional OSM download, 113,098,966 bytes of expected 120,732,312; must resume and verify against publisher MD5 before use. |
| `work/raw_stage/DS071_WEST_BENGAL/west_bengal.poly` and `.md5` | KEEP | Region boundary and publisher checksum companion files. |
| `work/raw_stage/DS033/` | CORRUPT / METADATA-ONLY | RBI downloads failed with empty replies. Failure manifests are useful; no source workbooks were acquired. |
| `work/raw_stage/DS057`, `DS071`, `DS098` metadata remnants | KEEP AS AUDIT METADATA | Preserve blocker/cleanup evidence; do not treat as raw data. |
| `outputs/SIH26091_COMPLETE_SHARE_PACKAGE/research_foundation/` | DUPLICATE / STALE | Snapshot predates regional cleanup and current acquisition state. Do not use as canonical input; rebuild any future share package from live metadata. |
| `work/pdf_render.*`, `work/spec_pdf_review/` | UNUSED AFTER REVIEW | Temporary QA renders/extractions. Safe to remove after specifications are represented in durable docs. |
| `.DS_Store`, `__pycache__` | UNUSED | Generated local metadata/caches; exclude from version control. |
| Netlify URL | EXTERNAL REFERENCE | The deployed site was analyzed earlier, but no frontend source exists in this workspace. Backend API integration will remain clean and frontend-independent. |

## Storage audit already completed

- `FILES_TO_DELETE.md` was created before cleanup.
- 195 local out-of-scope/duplicate files (5,363,883,914 bytes) were removed.
- 53 full-India OSM Drive parts (1,488,977,920 bytes) were removed.
- Two out-of-scope national reports (65,139,804 bytes total) were removed from Drive; empty folders were quarantined.
- The national livestock workbook was deleted locally only after a six-district regional extract was built, visually verified, uploaded, and Drive byte-size verified.

## Risks and required corrections

1. Acquisition registries currently conflate historical acquisition with current storage presence. Add event/current-state fields.
2. The partial West Bengal PBF must not be ingested until its publisher MD5 matches.
3. HCES and ASUSE microdata require registration/interactive acquisition; adapters must represent `EXTERNAL_AUTH_REQUIRED`, never fabricated data.
4. Government source URLs may change or return deceptive HTTP-200 error pages. Validate file signatures and schemas.
5. Official scheme calculations must remain blocked until current rules/effective dates are verified from authoritative sources.

## Immediate implementation boundary

Build a Python backend with Pydantic domain models, SQLite development storage plus a PostgreSQL/PostGIS schema, deterministic graph/flow/counterfactual/MVV/finance/twin/stress engines, evidence adapters, a canonical `VentureDecision`, FastAPI endpoints, and controlled/real-data tests. Preserve transparent baselines and label assumptions explicitly.

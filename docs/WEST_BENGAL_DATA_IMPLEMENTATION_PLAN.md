# West Bengal Data Implementation Plan

## Scope

Maintain one West Bengal evidence store. Build locality/catchment subgraphs at query time; never run one state-wide economic optimization graph. Kolkata, North 24 Parganas, South 24 Parganas, Howrah, Hooghly and Nadia are deep-validation regions, not hardcoded product limits.

## Acquisition rule

Catalogue broadly; download only implementation inputs. Prefer West Bengal extracts, district files, bounding boxes, or API queries. Preserve source URL, version, retrieval time, checksum, coverage, evidence type, schema, processing status, confidence and missing portions. Never call a link or metadata record an acquired dataset.

## Priority pipeline

1. Geographic identity: LGD, Census village/ward identifiers, PIN and administrative crosswalk.
2. Population and infrastructure: Census PCA, Mission Antyodaya, JJM, electricity and institutional facilities.
3. Accessibility and POIs: verified West Bengal OSM PBF plus Overpass queries; PMGSY roads.
4. Demand priors: HCES 2023-24 and 2022-23 microdata after authorized acquisition; district/sector-aware inference only.
5. Enterprise priors: ASUSE 2025 and 2023-24 after authorized acquisition.
6. Supply: DAHD regional livestock extract, district crops, horticulture and fisheries.
7. Prices: AGMARKNET/e-NAM plus WPI/CPI adjustment inputs; indexes are not direct demand.
8. Weather and route risk: West Bengal spatial/temporal subset only.
9. Finance/project evidence: current official scheme rules and dated model project profiles.

## Data states

- `DISCOVERED`: metadata/URL only.
- `BLOCKED_AUTH`: registration, CAPTCHA or credential required.
- `DOWNLOADED_UNVERIFIED`: bytes present but checksum/schema incomplete.
- `ACQUIRED_VERIFIED`: source bytes, coverage, size and checksum recorded.
- `PROCESSED_VERIFIED`: transformation manifest, input hash, output hash and validation counts recorded.
- `DELETED_BY_SCOPE`: historically acquired but intentionally removed; registry retains the event.

## Current verified inputs

- DS057 regional livestock locality workbook: 18,326 selected rows, six South Bengal districts, exact source/output hashes, Drive size verified.
- DS046 West Bengal MSME profiles: two official PDFs with SHA-256 and Drive byte-size verification.
- DS024/DS025 WPI bundles: small national reference series retained for price-index joins.

## Current blockers

- HCES/ASUSE: `EXTERNAL_AUTH_REQUIRED` via MoSPI NADA registration/download workflow.
- LGD: interactive/CAPTCHA download; pursue official API/alternate public export and retain manual-import adapter.
- Census downloads: portal/TLS and interactive formats require a robust official-source adapter.
- RBI handbook binaries: official server returned empty replies in automated curl tests; retain browser/manual import path.
- West Bengal OSM: partial regional file exists; resume and verify publisher MD5 before ingestion.

## Validation

Every adapter must test file signature, schema, geographic filter, row counts, missingness and key uniqueness. Derived estimates must reference evidence IDs and return central/lower/upper/confidence/method version. If labels are insufficient, return `INSUFFICIENT_EVIDENCE` or a wide explicit prior—never synthetic observations.

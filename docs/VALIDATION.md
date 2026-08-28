# Validation

Version 0.3.0 was validated on 2026-08-28.

- Ruff passed and 36 pytest tests passed.
- All 53 registry objects matched recorded byte size and SHA-256.
- Four restricted HCES/ASUSE ZIP archives passed full member CRC checks.
- SQLite `PRAGMA integrity_check` returned `ok` for 53,537 geographies, 381,523 locality
  evidence records and 976 regional priors.
- Both trained-task artifact sets loaded successfully and matched their registry checksums.
- ASUSE weighted `annual_output - annual_input = annual_GVA` held over 1,551 groups; maximum
  absolute floating residual was `3.725290298461914e-09` INR.
- Real E2E localities: Kolkata (Kolkata); Amdanga (North 24 Parganas); Abad Bhagabanpur
  (South 24 Parganas); Kharibari CT (Darjeeling); Anandapur (Jalpaiguri); Adina (Maldah);
  Adra CT (Purulia).
- All seven cases resolved exact geo IDs, received regional survey priors, computed OSM
  catchments and refused venture selection because required current evidence was missing.
- The HTTP UI was exercised in a real Chromium browser: search, locality selection, evidence,
  analysis, freshness labels, six evidence gates and both PMMY/AHIDF screens rendered. The UI and
  OpenAPI endpoints returned HTTP 200 and the browser logged zero warnings/errors.

Machine-readable evidence is in `FINAL_TECHNICAL_AUDIT.json`,
`WEST_BENGAL_MULTI_DISTRICT_E2E.json`, and `models/model_registry.json`.

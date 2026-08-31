## What changed?

Describe the change and the problem/requirement it addresses.

## Verification

- [ ] `ruff check backend scripts tests deploy`
- [ ] `pytest`
- [ ] `python -m compileall -q backend scripts deploy`
- [ ] `node --check frontend/app.js` (when frontend code changed)
- [ ] Relevant E2E/data audit run when required

## GramArtha integrity checklist

- [ ] No secrets, credentials, private model artifacts or restricted respondent microdata were added.
- [ ] New/changed data has source, date, provenance, license/terms and freshness information.
- [ ] No stale, sampled or modelled value is presented as an observed current local fact.
- [ ] Decision gates are not bypassed by missing evidence.
- [ ] LLM/explanation code cannot silently change finance or the canonical selected venture.
- [ ] Uncertainty/scenario claims remain accurately qualified.
- [ ] Tests cover any change to decision behavior.
- [ ] README/docs/version metadata were updated where necessary.

## Decision impact

Does this change alter `VentureDecision`, evidence gates, financial calculations, uncertainty, or venture ranking? If yes, explain exactly how.

## Screenshots / evidence

Add UI screenshots, audit output, benchmark output or source references when relevant.

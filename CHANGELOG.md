# Changelog

All notable repository-level changes are documented here. Historical technical reports in `docs/` keep the version they originally audited.

## [Unreleased]

### Added

- CI coverage measurement with branch coverage, a 75% combined coverage floor and downloadable HTML/XML coverage artifacts.
- Automated repository-hygiene and local Markdown-link validation.
- Documentation index separating current reviewer material from historical audits.
- Sanitized design-QA index under `docs/design-qa/`.
- Release policy documenting versioned software artifacts separately from SIH demo media.
- Verified release pipeline outputs for wheel, source distribution, public-runtime bundle, CycloneDX SBOM, release manifest and SHA-256 checksums.
- GitHub Actions CI for linting, compilation, runtime integrity and API smoke testing.
- CodeQL, dependency audit, Bandit and advisory secret scanning.
- Security policy, contribution guide, CODEOWNERS, issue templates, PR integrity checklist and Dependabot.
- Contributor acknowledgement for `@tapandutta46779`.

### Changed

- README rewritten around live-product, judge and engineering-audit paths with measured test coverage.
- Dependency workflow renamed from “Dependency Review” to the technically accurate “Dependency Audit”.
- MIT license normalized to the standard license text so GitHub recognizes SPDX `MIT`; third-party boundaries remain in `DATA_LICENSES.md` and `NOTICE.md`.
- Release workflow now reruns the coverage gate, audits dependencies, smoke-installs the built wheel and checks the public-runtime archive boundary.
- Repository documentation now points readers through `docs/README.md` instead of mixing current and historical audits.

### Removed

- Root `FILES_TO_DELETE.md` cleanup inventory.
- Root `design-qa.md` containing local implementation-path details; relevant QA evidence is now documented under `docs/design-qa/`.
- Duplicate `docs/ARCHITECTURE.md`; the authoritative system maps remain at root `ARCHITECTURE.md`.

## [0.7.2] - 2026-08-30

Current application/package version represented by `pyproject.toml` and the FastAPI application.

For detailed methodology and historical implementation changes, see the versioned reports and audits under `docs/`.

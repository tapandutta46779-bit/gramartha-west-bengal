# GramArtha release policy

GramArtha separates **demo/presentation media** from **versioned software releases**.

The existing `sih2026-demo-videos-v1` GitHub Release is presentation media. It should not be interpreted as the current software-version artifact.

## Versioned software releases

Software releases use semantic version tags matching `pyproject.toml`, for example `v0.7.2` for package version `0.7.2`.

A release tag should be created only from a green `main` commit after CI, Security and Dependency Audit have completed successfully.

## Automated release verification

A `v*.*.*` tag triggers `.github/workflows/release.yml`. The workflow:

1. checks Ruff and Python compilation;
2. reconstructs the public runtime databases;
3. runs the test suite with branch coverage and a 75% combined coverage floor;
4. checks SQLite integrity;
5. verifies tag/package-version equality;
6. audits installed third-party dependencies;
7. builds Python wheel and source distribution;
8. installs the built wheel in a fresh virtual environment and imports the application;
9. builds a public-safe runtime archive;
10. rejects archive paths that indicate raw/restricted evidence surfaces;
11. generates a CycloneDX JSON dependency SBOM;
12. emits a release manifest and SHA-256 checksums;
13. uploads all artifacts and, for tag-triggered runs, publishes the GitHub Release.

## Expected release artifacts

A normal versioned release contains:

- `sih26091_network_repair-<version>-py3-none-any.whl`
- `sih26091_network_repair-<version>.tar.gz`
- `gramartha-<version>-public-runtime.tar.gz`
- `gramartha-<version>-sbom.cdx.json`
- `RELEASE-MANIFEST.txt`
- `SHA256SUMS.txt`

## Public-data boundary

The versioned runtime artifact must not package raw restricted respondent microdata, private fitted model artifacts, working directories or source acquisition archives. Third-party data/asset licensing remains governed by `DATA_LICENSES.md` and `NOTICE.md`.

## Maintainer release sequence

```bash
git checkout main
git pull --ff-only
git tag -a v0.7.2 -m "GramArtha v0.7.2"
git push origin v0.7.2
```

Replace `0.7.2` with the current `pyproject.toml` version for future releases. The workflow intentionally fails if the tag and package version differ.

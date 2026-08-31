# Security Policy

Security matters in GramArtha because the project combines an HTTP API, downloadable reports, environment-based configuration, public runtime databases and data-processing pipelines.

## Supported versions

| Version | Supported |
|---|---|
| `main` | Yes |
| `0.7.x` | Yes |
| `< 0.7` | Best effort only |

## Reporting a vulnerability

Please **do not publish exploit details, credentials, tokens, personal data, restricted survey records or private model artifacts in a public GitHub issue**.

Preferred reporting path:

1. Use GitHub's private vulnerability reporting / Security Advisory interface for this repository if it is enabled.
2. If private reporting is not available, open a minimal public issue stating only that you need a private security contact channel. Do not include the vulnerability details in that issue.

Please include, privately when possible:

- affected path/component and version or commit;
- reproduction steps;
- expected versus observed behavior;
- realistic impact;
- proof-of-concept only when necessary and safe;
- suggested mitigation, if known.

## Security-sensitive areas

Reports are especially useful for:

- API input validation and denial-of-service conditions;
- path traversal or unsafe file handling;
- arbitrary code execution or command injection;
- environment-variable / secret exposure;
- accidental inclusion of restricted microdata or private model artifacts;
- unsafe PDF/report generation;
- dependency or supply-chain vulnerabilities;
- cross-site scripting or unsafe browser behavior;
- integrity failures that let stale/modelled evidence bypass decision gates;
- LLM integration that can mutate deterministic finance or venture selection.

## Public data boundary

Do not commit or attach:

- API keys, credentials or `.env` files containing secrets;
- restricted HCES/ASUSE respondent microdata;
- personally identifying respondent records;
- private fitted model artifacts that are intentionally excluded from the public package;
- proprietary or redistribution-restricted source files without permission.

See `DATA_LICENSES.md` and `docs/MICRODATA_IMPORT.md`.

## Automated security checks

The repository is configured for:

- CodeQL analysis for Python and JavaScript;
- `pip-audit` dependency vulnerability scanning;
- high-severity Bandit static analysis;
- Gitleaks advisory secret scanning;
- pull-request dependency review;
- Dependabot updates for Python and GitHub Actions.

Automated checks supplement review; they do not prove the application is vulnerability-free.

## Disclosure

Maintainers should acknowledge a valid private report, reproduce it when practical, develop a minimal fix, add a regression test where appropriate, and publish release notes once disclosure is safe.

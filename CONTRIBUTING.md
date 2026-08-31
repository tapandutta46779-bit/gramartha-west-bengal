# Contributing to GramArtha

Contributions are welcome when they preserve the project's central integrity rule: **never present stale, sampled, missing or modelled evidence as an observed current local fact.**

## Development setup

GramArtha requires Python 3.12+.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

Run the baseline checks before opening a pull request:

```bash
ruff check backend scripts tests deploy
pytest
python -m compileall -q backend scripts deploy
node --check frontend/app.js
```

To reproduce the public-safe runtime:

```bash
bash deploy/start.sh
```

## Branches and commits

Prefer focused branches such as:

- `feat/<short-name>`
- `fix/<short-name>`
- `data/<source-or-audit>`
- `docs/<short-name>`
- `chore/<short-name>`

Keep commits scoped and explain *why* a methodological or evidence change is necessary.

## Decision-integrity rules

A contribution must not:

1. fabricate current demand, supply, price, capacity, cost or route evidence;
2. silently upgrade stale or sampled evidence into a decision-ready observation;
3. allow an LLM to calculate hidden finance or change the canonical selected venture;
4. label scenario probabilities as empirically calibrated unless they actually are;
5. describe an enumerated MVV search as a general optimizer;
6. remove source provenance, observation dates, freshness labels or explicit uncertainty without a justified replacement.

## Data contributions

For new or changed evidence sources, document:

- publisher and source URL/stable identifier;
- acquisition date;
- observation/effective date;
- geographic granularity;
- license/terms and redistribution status;
- checksum or manifest where practical;
- transformation/ingestion command;
- freshness class and decision gate implications.

If source redistribution is restricted or unclear, do not commit the raw file to the public repository.

## Tests

Behavior changes should include a regression test. Data-pipeline changes should include an integrity or reproducibility check where practical.

Particularly important test areas are:

- evidence freshness and provenance;
- geography resolution;
- flow/bottleneck/counterfactual invariants;
- finance calculations;
- uncertainty and robust-selection determinism;
- multilingual output;
- API contracts;
- public-runtime reconstruction.

## Pull requests

Use the repository PR template. A reviewer should be able to answer:

- What changed?
- Which claim or requirement does it support?
- How was it tested?
- Did any data provenance or licensing boundary change?
- Could the change alter a `VentureDecision`?
- Does documentation/versioning need an update?

## Security

Do not report vulnerabilities or secrets in ordinary issues. Follow [`SECURITY.md`](SECURITY.md).

## Licensing

By contributing original code or documentation, you agree that your contribution can be distributed under the repository's MIT license. Third-party data/assets must keep their original terms; see [`DATA_LICENSES.md`](DATA_LICENSES.md).

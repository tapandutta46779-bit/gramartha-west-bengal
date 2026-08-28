# Architecture

The service is layered: source files -> provenance-preserving adapters -> SQLite evidence and
geographic identities -> transparent sector adapter -> economic graph -> exact flow and
counterfactual engines -> enumerated MVV -> finance/twin/stress -> one persisted
`VentureDecision`. The browser renders that object and performs no finance arithmetic.

Ordinary requests do not supply a graph. Advanced requests may supply one for controlled tests,
but every demand/supply/capacity edge must reference available evidence. Missing dependencies
produce named gates rather than inferred values.


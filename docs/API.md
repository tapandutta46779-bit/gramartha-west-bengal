# API

`POST /analyze` accepts `state`, `district`, `locality` or `geo_id`, `capital`,
`business_category`, optional `profile`, language and catchment radius. A supplied graph remains an
advanced/testing mode. Other retained endpoints are `/health`, `/localities/search`,
`/evidence/{geo_id}`, `/analysis/{id}`, `/compare` and `/stress`.

The response is the persisted canonical `VentureDecision`, including resolution method,
evidence/gates, intervals, OSM context, graph/flow/MVV when possible, finance screening, twin,
limitations, sources and version trace.

# GramArtha v0.7.1 full-detail localization audit

Audit date: 2026-08-30. Scope: full Bengali/Hindi detailed website output, complete
language-specific PDF reports, canonical-number preservation and public deployment verification.

## Requirement status

| Requirement | Status | Verification evidence |
|---|---|---|
| One canonical numeric decision across English, Bengali and Hindi | IMPLEMENTED + VERIFIED | Language selection only re-renders the stored `VentureDecision`; no analysis request is issued by the switch. Automated tests assert one analysis ID and unchanged canonical numbers. |
| Full detailed website localization | IMPLEMENTED | All seven result tabs, headings, labels, explanations, caveats, evidence wording, action text and audit headings use the deterministic detailed presentation attached to the stored decision. |
| Full PDF localization | IMPLEMENTED + VERIFIED | English, Bengali and Hindi reports each contain eight A4 pages: summary plus seven localized technical pages. |
| Bengali and Hindi Unicode shaping | VERIFIED | Noto Sans Bengali/Devanagari and HarfBuzz shaping; every page rendered to PNG and visually inspected for broken glyphs, clipping and overflow. |
| Scientific and numerical invariance | VERIFIED | Locality, values, units, statuses, evidence dates, confidence and uncertainty remain sourced from the same canonical decision. Translation does not mutate calculation data. |
| Provenance preservation | VERIFIED | Official dataset titles, source URLs, record identifiers, locality/proper names and scientific acronyms remain unchanged where translation would damage traceability. |
| Language switching without rerunning | IMPLEMENTED + VERIFIED | Frontend reuses `currentDecision`; switching output language performs no POST to `/analyze`. |
| OSM competition detail | IMPLEMENTED + VERIFIED | Ordinary result pages show names when available, mapped category, straight-line distance, direct/indirect counts, intensity, coordinate/index provenance and the explicit capacity/sales/market-share caveat. |
| PDF download resilience | IMPLEMENTED + VERIFIED | Same-tab download avoids blank popup tabs. If a deployment invalidates the server lookup, the browser posts the unchanged stored decision to rebuild the PDF without rerunning the analysis. GET and fallback POST return `application/pdf`, attachment filenames, explicit lengths, no-store and nosniff headers. |
| Automated regression suite | VERIFIED | Ruff passed, JavaScript syntax passed, 58 pytest tests passed. |
| Independent professional linguistic review | NOT PERFORMED | Deterministic Bengali/Hindi copy was visually and functionally reviewed; no external professional translator signed off the wording. |

## PDF page inventory

1. Entrepreneur-first summary and recommendation.
2. Recommendation, canonical geography, demand, supply and customer/supplier groups.
3. OSM competition, catchment, channels, operational and weather factors.
4. Minimum viable setup, CAPEX/OPEX, working capital, equipment, controls and licences.
5. Finance, break-even, NPV/IRR, 36-month cash checkpoints and current scheme screening.
6. Scenario analysis, SWOT, failure boundaries and sensitivity.
7. Pre-mortem, phased action plan and stop/reconsider rules.
8. Evidence freshness, confidence, limitations and source provenance.

## Translation boundary

User-facing prose is localized. Official scheme and dataset names, OSM/locality/proper names,
URLs, analysis IDs, variable/source identifiers and scientific abbreviations such as OSM, MVV,
NPV, IRR, CVaR and HHI are deliberately preserved. This is not missing localization: preserving
those strings prevents ambiguous attribution and keeps the report auditable.

## Claim boundary

GramArtha provides conditional planning estimates, not observed complete locality demand, audited
shop sales, calibrated business-success probabilities, lender approval or guaranteed income. OSM
features are proxy evidence and do not reveal competitor capacity, sales or market share. Historical,
estimated, projected and current evidence classifications remain distinct in every language.

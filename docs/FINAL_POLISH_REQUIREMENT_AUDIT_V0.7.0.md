# GramArtha v0.7.0 final-polish requirement audit

Audit date: 2026-08-29. Scope: additive presentation, multilingual output, PDF delivery,
visual verification and public release readiness. The decision engine, evidence gates, finance
rules, OSM logic, MVV oracle and 36-month digital twin remain unchanged.

## Requirement-by-requirement status

| Requirement | Status | Verification evidence |
|---|---|---|
| One deterministic `PlainLanguageSummary` derived from `VentureDecision` | IMPLEMENTED + VERIFIED | `backend/models/presentation.py`; `backend/presentation/plain_language.py`; numerical-contract tests |
| Website and PDF consume the same summary | IMPLEMENTED + VERIFIED | API serializes the summary; PDF builder uses the stored summary or the same deterministic builder |
| Simple conclusion before technical detail | IMPLEMENTED + VERIFIED | Website summary is first; PDF page 1 is the summary; prior technical pages follow unchanged |
| Required conclusion statuses | IMPLEMENTED + VERIFIED | Five explicit enum values and deterministic decision policy |
| Required venture, money, market, risk and action fields | IMPLEMENTED + VERIFIED | All prompt-listed fields are typed and serialized |
| Ranges rather than false precision | IMPLEMENTED + VERIFIED | Project cost, month-12 revenue and operating cash are deterministic planning ranges; evidence intervals retain their canonical bounds |
| English, Bengali and Hindi website summaries | IMPLEMENTED + VERIFIED | Browser switched one analysis ID across all three languages without a second analysis |
| English input/search workflow | PRESERVED + VERIFIED | Form and locality search remain English; output selector is explicitly labelled |
| Numerical invariance across languages | IMPLEMENTED + VERIFIED | Same analysis ID and canonical numeric object; tests assert one contract with three text views |
| Bengali and Hindi PDF font shaping | IMPLEMENTED + VERIFIED | OFL Noto fonts, FPDF2 and HarfBuzz; rendered PNG inspection found no broken glyphs |
| Three language-specific PDF download controls | IMPLEMENTED + VERIFIED | `/analysis/{id}/pdf?language=en|bn|hi`; invalid language returns HTTP 422 |
| Existing technical PDF content preserved | IMPLEMENTED + VERIFIED | New page 1 is prepended; the complete former seven-page technical report remains pages 2-8 |
| Entrepreneur-first visual hierarchy | IMPLEMENTED + VERIFIED | Decision badge, why/who cards, money grid, market grid, risks/actions and collapsed technical layer |
| Responsive mobile layout | IMPLEMENTED + VERIFIED | 390 x 844 Bengali browser pass; no horizontal overflow or clipped cards observed |
| Reduced-motion support | IMPLEMENTED | CSS honours `prefers-reduced-motion`; language-only scroll becomes non-animated |
| Keyboard/focus accessibility | PRESERVED + VERIFIED IN DOM | Semantic headings, form labels, buttons, links, details/summary and visible focus rules remain |
| Representative dairy, poultry, retail and processing cases | VERIFIED | Puapur browser cases: dairy, poultry, kirana and food processing; transport added for named OSM stress testing |
| OSM names/categories/distances visible | VERIFIED | Transport: six direct candidates; nearest Neamatpur Vegetable Market, 9.1 km; full named list visible |
| Seven technical result tabs | VERIFIED | All seven panels produced non-empty visible content in the browser |
| Automated regression suite | VERIFIED | Ruff passed; JavaScript syntax passed; 57 pytest tests passed |
| Public-safe release boundary | VERIFIED | Restricted HCES/ASUSE respondent files, private model artifacts, local databases and credentials are excluded from Git/public packaging |
| Fully localized deep technical appendix | PARTIAL | The entrepreneur-first summary and PDF first page are localized. Stable mathematical identifiers, source names and the preserved deep technical appendix remain English to avoid unreviewed machine translation of scientific claims. |
| Human linguistic review | NOT PERFORMED | Bengali and Hindi were rendered and visually inspected, but no independent professional translator signed off the copy. |

## Browser matrix

| Case | Analysis outcome | Evidence checked |
|---|---|---|
| Puapur, Purulia - dairy | Conditional / promising-small-start | Bengali switch, mobile layout, one indirect OSM candidate, finance and market ranges |
| Puapur, Purulia - poultry | Conditional / promising-small-start | Full summary generated |
| Puapur, Purulia - kirana | Conditional / promising-small-start | Full retail summary generated |
| Puapur, Purulia - food processing | Conditional / promising-small-start | Full processing summary generated |
| Puapur, Purulia - transport | Conditional / promising-small-start | Six direct OSM candidates, names, categories, distances, market and institution |

## Claim boundary

GramArtha provides conditional planning estimates, not observed complete locality demand, audited
shop sales, calibrated business-success probabilities, lender approval or guaranteed income. OSM
features are competitor proxies and do not reveal capacity, sales or market share. Historical,
estimated, projected and current evidence classifications remain visible in the technical layer.

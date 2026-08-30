# GramArtha design QA

## Comparison target

- Source visual truth: `/Users/mohitdutta/.codex/generated_images/01a04160-b707-78f2-85b9-277b39e603ec/exec-a88ab876-f4ca-43d4-b7e8-0f467933579a.png`
- Final desktop implementation: `docs/design-qa/implementation-desktop.png`
- Final mobile implementation: `docs/design-qa/implementation-mobile.png`
- Result-state evidence: `docs/design-qa/workflow-result.png`
- Final side-by-side evidence: `docs/design-qa/source-vs-implementation-final.png`
- Complete mobile market evidence: `docs/design-qa/mobile-complete-market.png`
- Desktop viewport override: 1440 x 1024 CSS px; IAB content capture: 1425 x 1013 px at density 1.
- Mobile viewport override: 390 x 844 CSS px; IAB content capture: 375 x 812 px at density 1.
- Source pixels: 1487 x 1058. For the side-by-side comparison, both source and implementation were normalized to 1440 x 1024 without browser chrome.
- Desktop state: Kolkata / Kolkata Ward No.1 selected; Kirana / grocery; 10 km; Quick analysis; English.

## Full-view comparison evidence

The final implementation preserves the selected 70/30 composition: editorial left narrative, broad right planning surface, fixed seven-stage ribbon, warm ivory/forest/orange palette, generated topographic river background, lightweight matched icons and a single dominant analysis action. Major-region proportions, headline wrapping, form density and selected-locality treatment are aligned with the source. The final implementation intentionally uses slightly more explicit journey and field icons because the user requested signs that match the text.

## Focused-region evidence

- Setup form: district and locality controls remain labeled, keyboard-focusable and operational; the selected locality has the source-like orange edge and confirmation icon.
- Planning controls: all original fields remain present and the long default business option no longer clips at desktop width.
- Result state: the simple summary, complete OSM competitor section and seven detailed result tabs render after the same analysis request. No named-candidate slice remains in the website or PDFs.
- Mobile: no horizontal document overflow (`scrollWidth == clientWidth == 375`); brand, hero, planning controls and primary action remain readable.
- Loading/motion: connected analysis icons, locality confirmation pulse, reveal transitions and background parallax are implemented, with a complete `prefers-reduced-motion` fallback.

## Comparison history

### Pass 1 — blocked

- [P1] Generated background was hidden by the opaque body surface.
  - Fix: made the body transparent and raised the real generated background asset behind the content.
- [P2] Hero type was materially larger than the target and wrapped into five lines.
  - Fix: reduced the desktop display scale to reproduce the target's three-line hierarchy.
- [P2] The default business-interest option clipped in the four-column grid.
  - Fix: assigned content-aware minimum widths and a wider business-interest track.

### Pass 2 — blocked

- [P2] Selected-locality confirmation lacked the source check icon.
  - Fix: added the matching Phosphor confirmation icon and explicit grid placement.
- [P1] Existing mobile CSS hid the `Artha` portion of the brand.
  - Fix: limited mobile hiding to the navigation tagline and preserved the complete brand.
- [P2] The horizontally scrollable journey exposed a persistent scrollbar.
  - Fix: retained touch scrolling while visually suppressing the scrollbar.

### Final pass — passed

No actionable P0, P1 or P2 mismatch remains.

## Required fidelity surfaces

- Fonts and typography: existing system/Inter stack retained; final heading scale, weight, line height and wrapping align with the selected target. No clipping was found.
- Spacing and layout rhythm: desktop two-column composition, planner padding, control spacing, sticky journey and mobile single-column collapse are stable.
- Colors and visual tokens: forest, orange and ivory tokens consistently map to the source; focus, disabled, selected and evidence states retain semantic contrast.
- Image quality and asset fidelity: the background is a real generated raster asset, not CSS/div art. It crops cleanly at desktop and mobile widths.
- Icons: one consistent Phosphor family is used for navigation, journey stages, fields, confirmation and analysis progress.
- Copy/content: every original workflow label, evidence statement and scientific-honesty caveat remains intact.
- Accessibility: native labels and controls remain, focus rings remain visible, reduced-motion disables nonessential movement, and mobile has no horizontal document overflow.

## Interaction verification

- District list loaded 23 supported districts plus its placeholder and became enabled.
- Kolkata selection updated the status text.
- Ward No.1 search and canonical selection worked.
- Kirana / grocery Quick analysis completed.
- Returned venture remained Kirana and the OSM competitor section rendered.
- All seven technical tabs were clicked successfully at phone size after removing the mobile sticky-layer collision.
- The complete local audit retained 335 named OSM candidates for the selected winning sector in English, Bengali and Hindi; the same 335 rows appeared in both the visible nearby list and detailed market list.
- “Find the best opportunity” executed all 11 supported sectors. The UI displayed the other 10 results, including an explicit evidence-gated sector, and Deep mode reported 512 scenarios for the winner.
- English, Bengali and Hindi PDF downloads completed with attachment headers; the PDFs paginate complete OSM lists instead of truncating at twelve entries.
- Browser console warnings/errors: none.

## Follow-up polish

- [P3] The implementation's planner is slightly more opaque than the concept so dense financial text remains readable over the moving background.
- [P3] The real mobile browser's native scrollbar reduces the captured content width by roughly 15 px; the page itself has no horizontal overflow.

final result: passed

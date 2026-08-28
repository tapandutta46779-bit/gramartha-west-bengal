# SIH26091 Productization v0.4.0

## Outcome

v0.4.0 adds an ordinary-entrepreneur planning path without changing or overwriting the verified
v0.3.0 data/model release. A user can select a verified West Bengal locality, enter own capital,
choose a sector or ask the browser to compare supported opportunities, and receive a readable
minimum-viable-venture and 36-month planning result.

## Implemented sector adapters

The adapter registry now has separate configurations for:

- kirana / grocery (ASUSE NIC 47 benchmark);
- poultry input and egg aggregation (NIC 46 distribution benchmark);
- fish collection and distribution (NIC 46 distribution benchmark);
- small food processing (NIC 10 benchmark);
- rural distribution / aggregation (NIC 46 benchmark).

Dairy v1 remains the deeper commodity-specific adapter. It continues to require productive supply,
current price, incumbent capacity, route cost, and cost configuration evidence; it is not silently
converted into the generic enterprise benchmark path.

Each new adapter defines a commodity/service unit, ASUSE mapping, demand/incumbent scaling,
configuration capacity, CAPEX/working-capital allocation, fixed-overhead treatment, basic compliance
requirements and downside-variable taxonomy. The three generated sizes are exhaustively evaluated;
the selected result is therefore exact only over that finite enumerated candidate set.

## Evidence interpretation

The v0.4 sector outputs have status `MODELLED_BENCHMARK` and LOW interval confidence. They are
constructed from real weighted ASUSE 2023-24 district/sector enterprise priors already present in
the private evidence pipeline. They are **not** observed locality demand, a local business census,
current selling-price observations, or lender quotations.

The central enterprise-output/input/asset/worker priors are converted to a starter-scale planning
configuration. Demand and incumbent-service envelopes use ±30% intervals. Variable procurement is
represented through the output/input margin; candidate monthly OPEX contains only a fixed-overhead
component so that ASUSE inputs are not double counted in MVV feasibility and the digital twin.

## Customer experience

The browser UI now presents:

- area and capital wizard;
- sector selection or “Find the best opportunity for me” comparison;
- readable project cost, own capital, illustrative finance requirement, month-12 revenue and cash
  surplus;
- distinct operating break-even, cash break-even and investment payback;
- market envelope and service-gap visual;
- CAPEX, working capital, OPEX and staffing;
- the network-repair explanation;
- 36-month cash chart and calculated staged-expansion triggers;
- alternatives;
- evidence/methodology in a secondary technical disclosure.

Raw JSON, internal identifiers and evidence-gate codes are no longer the primary customer view.
When the commodity-specific dairy path remains blocked, the UI asks for additional information and
offers the supported opportunity comparison instead of showing a backend refusal page.

## Verified E2E cases

The machine-readable result is `outputs/e2e/product_e2e_v0.4.0.json`.

| Locality / district | Sector | Capital | Result | Payback |
|---|---|---:|---|---:|
| Kolkata, Kolkata | Kirana | ₹1,00,000 | Conditional planning case | 21 months |
| Barasat, North 24 Parganas | Poultry aggregation | ₹1,00,000 | Conditional | 21 months |
| Abad Bhagabanpur, South 24 Parganas | Fish distribution | ₹1,25,000 | Conditional | 32 months |
| Kharibari, Darjeeling | Food processing | ₹1,50,000 | Conditional | 24 months |
| Anandapur, Jalpaiguri | Rural distribution | ₹1,20,000 | Conditional | 15 months |
| Adina, Maldah | Kirana | ₹80,000 | Conditional | 32 months |
| Adra, Purulia | Poultry aggregation | ₹90,000 | Conditional | 26 months |

All seven returned HTTP 200, a selected finite-set MVV, no blocking gate, bounded planning evidence
and a 36-month digital twin. Browser validation also passed the Kolkata “best opportunity” flow with
no console warning/error.

## Validation

- Ruff: passed.
- Pytest: 41 passed.
- JavaScript syntax check: passed.
- Real HTTP browser flow: passed.
- Existing HCES/ASUSE fitted artifacts and v0.3.0 audit remain unchanged.

## Still required for a high-confidence financial recommendation

This release is a productized planning estimator, not completion of every aspirational item in the
1,395-line specification. The following remain explicit evidence limitations:

- current local selling/procurement prices and current locality demand transactions;
- verified locality enterprise capacity and competitor entity resolution;
- current rent, wage, electricity, fuel and supplier quotations by locality/sector;
- sector-specific physical supply models for poultry, fishery and crops;
- full loan quote, interest rate, sanction terms and underwriting;
- calculated multi-variable failure boundaries and minimax-regret across joint uncertainty;
- Bengali/Hindi translation of all customer copy (language selection preserves frozen numbers but
  the new UI copy is presently English);
- the requested new 15-25 page v0.4 professional PDF.

No v0.4 output should be described as observed current locality revenue, lender approval, guaranteed
income, exact village demand or a global mathematical optimum.

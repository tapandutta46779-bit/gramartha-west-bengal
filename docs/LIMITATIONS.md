# Remaining Evidence and Method Limitations

- Census 2011 population/households are structural historical observations. No defensible 2026
  locality population projection has been loaded.
- HCES estimates are sampled district/sector priors, not exact village demand. ASUSE estimates are
  sampled district/sector/NIC2 enterprise priors, not a census of competitors or capacity.
- The 2019 livestock census is stale for a 2026 supply decision. Current productive-animal share,
  yield, seasonality, collection loss and reachable supply remain absent.
- Current locality milk selling/procurement prices, fuel-linked transport cost, competitor
  capacity, venture CAPEX/OPEX, wages and commercial rent are not loaded. They are blocking gates.
- OSM roads/POIs are volunteered proxy evidence; statewide coverage does not imply statewide
  economic completeness.
- Random-forest models won geographic-holdout MAE, but ordinary locality requests do not contain
  their household/enterprise microfeatures. Production therefore uses direct weighted survey
  priors and does not pretend to run an inapplicable model.
- MVV is exact only over the supplied finite candidate list. The current automatic library contains
  one dairy transport configuration and is not a general configuration MILP.
- Uncertainty propagation uses source intervals and deterministic endpoint arithmetic. A full
  correlated probabilistic model and expanded multi-shock engine remain unimplemented.
- PMMY/AHIDF screens do not establish lender rate, tenure, security, margin, live portal acceptance,
  underwriting or sanction. AHIDF's temporary continuation ends 2026-09-30 unless superseded.
- Restricted unit microdata and fitted artifacts are retained privately and are excluded from the
  public-share package. Aggregate outputs, code, provenance, checksums and metrics are shareable.

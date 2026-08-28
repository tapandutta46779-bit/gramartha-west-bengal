# Bottleneck Model

Implemented bottlenecks are marginal `EDGE_CAPACITY` relaxations: each edge is increased by a
declared unit, the exact flow is rerun, and served-demand gain is ranked against repair cost where
available. Node capacity, storage, processing, concentration, route fragility and other requested
classes remain partial and are not claimed as implemented.


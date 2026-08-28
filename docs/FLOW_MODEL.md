# Flow Model

For each commodity graph, a super-source connects supply nodes and demand nodes connect to a
super-sink. Original edges carry non-negative capacity and economic unit cost. Successive
shortest-path augmentation continues until no source-sink path exists. This lexicographically:

1. maximizes total served demand;
2. among that maximum flow, minimizes total economic cost.

Unserved demand is nominal demand minus served flow. Results include edge flows and served demand
per customer node. Exactness applies to the supplied finite graph and numerical tolerance, not to
the completeness of real-world evidence.


# West Bengal Geographic Crosswalk

Internal `geo_id` is never represented as an official identifier. DS057 identities are stable,
dataset-scoped hashes over rural/urban type, district, parent and locality. Official Census 2011
codes are attached only after exact district/locality matching, with sub-district disambiguation
when needed. Fuzzy matching is an explicit, flagged resolver fallback and is disabled by default.

The Census directory yielded 41,154 WB locality rows and 41,134 unique location codes. Exact
reconciliation attached Census codes to 31,747 DS057 identities; 380 ambiguous DS057 matches were
not merged. OSM V4 hierarchical matching supplied proxy coordinates to 3,320 identities: 2,681
were exact-name points contained in the matching district boundary and 639 duplicated-name cases
were additionally contained in a unique matching block/subdistrict boundary. Another 6,952 OSM
name candidates were withheld as ambiguous, and 43,265 identities had no exact OSM place-name
candidate. Unique spelling alone is never accepted as coordinate proof. Current LGD/PIN alignment
and post-2011 district splits remain partial.

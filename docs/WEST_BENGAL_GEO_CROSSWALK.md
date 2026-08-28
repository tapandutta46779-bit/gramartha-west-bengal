# West Bengal Geographic Crosswalk

Internal `geo_id` is never represented as an official identifier. DS057 identities are stable,
dataset-scoped hashes over rural/urban type, district, parent and locality. Official Census 2011
codes are attached only after exact district/locality matching, with sub-district disambiguation
when needed. Fuzzy matching is an explicit, flagged resolver fallback and is disabled by default.

The Census directory yielded 41,154 WB locality rows and 41,134 unique location codes. Exact
reconciliation attached Census codes to 31,747 DS057 identities; 380 ambiguous DS057 matches were
not merged. OSM exact-name matching supplied proxy coordinates to 4,980 identities; 4,632
ambiguous OSM matches were withheld. Current LGD/PIN alignment and post-2011 district splits remain
partial.


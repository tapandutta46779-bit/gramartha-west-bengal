# GramArtha public OSM runtime regression fix — v0.7.1

## Confirmed root cause

The full local West Bengal OSM database contained 381 administrative-area geometries, but the public deployment asset builder deleted both `admin_area` and `admin_area_rtree`. Localities with an exact OSM place point continued to work; unresolved wards and villages that needed a district representative-point proxy returned empty `catchment` and `competition` objects. Kolkata Ward 1 reproduced this exact failure on the public service.

## Fix

- The deployment asset still removes the 633,601-row road network to remain hostable, but it now preserves administrative-area geometry and its spatial index.
- A regression test decompresses the actual committed public OSM asset and verifies that every one of the 23 supported West Bengal districts resolves an explicitly labelled administrative representative-point proxy.
- The ordinary visible summary now shows up to six nearest direct/indirect OSM candidates with name, category, straight-line distance, inside/outside-radius status, coordinate quality and OSM vintage.
- The business-type explanation now distinguishes transparent scenario ranking from ML sector classification and confirms that a user-selected sector was not silently replaced.

## Honesty boundary

An administrative representative point is district context, not a locality centroid. OSM features are volunteered map evidence and may be incomplete. Counts do not measure competitor capacity, sales or market share, and a zero result is not proof that no competitor exists.

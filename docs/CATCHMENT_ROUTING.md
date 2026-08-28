# Catchment and Routing

The OSM store has R-tree indexes for 17,212 entities and 633,601 road ways. Radial catchments support
custom radii (5 km, 10 km or request value). Routing loads only road ways intersecting a bounded
local corridor, snaps endpoints to the local graph and runs Dijkstra using distance and road-class
default speeds.

Network travel time is labelled estimated. If no connected local route exists, the service returns
straight-line distance and withholds travel time.

from __future__ import annotations

import heapq
import itertools
import json
import math
import sqlite3
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from shapely import wkt


@dataclass(frozen=True)
class OsmEntity:
    osm_type: str
    osm_id: int
    category: str
    name: str | None
    latitude: float
    longitude: float
    tags: dict[str, str]


@dataclass(frozen=True)
class CatchmentResult:
    center_latitude: float
    center_longitude: float
    radius_km: float
    entities: list[OsmEntity]
    category_counts: dict[str, int]
    methodology: str = "OSM_RADIAL_CATCHMENT_V1"
    caveat: str = "OSM POIs are volunteered proxy evidence and may be incomplete."


@dataclass(frozen=True)
class RouteResult:
    distance_km: float | None
    estimated_travel_time_minutes: float | None
    road_classes: list[str]
    method: str
    connected: bool
    caveat: str


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0088
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    value = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(value))


class OsmSpatialStore:
    def __init__(self, path: str | Path) -> None:
        self.connection = sqlite3.connect(str(path))
        self.connection.row_factory = sqlite3.Row

    def metadata(self) -> dict[str, str]:
        return {
            row["key"]: row["value"]
            for row in self.connection.execute("SELECT key, value FROM metadata")
        }

    def administrative_area_proxy(self, district: str) -> dict[str, object] | None:
        """Return a clearly labelled district point for unresolved localities."""
        aliases = {
            "malda": "Maldah",
            "coochbehar": "Cooch Behar",
            "darjiling": "Darjeeling",
            "hugli": "Hooghly",
            "haora": "Howrah",
            "puruliya": "Purulia",
            "24 paraganas north": "North 24 Parganas",
            "north twenty four parganas": "North 24 Parganas",
            "24 paraganas south": "South 24 Parganas",
            "south twenty four parganas": "South 24 Parganas",
            "paschim barddhaman": "Paschim Bardhaman",
        }
        target = aliases.get(district.casefold().strip(), district.strip())
        row = self.connection.execute(
            "SELECT osm_id, name, geometry_wkt FROM admin_area "
            "WHERE admin_level = 5 AND lower(name) = lower(?) LIMIT 1",
            (target,),
        ).fetchone()
        if row is None:
            return None
        point = wkt.loads(row["geometry_wkt"]).representative_point()
        return {
            "latitude": point.y,
            "longitude": point.x,
            "coordinate_quality": "OSM_DISTRICT_REPRESENTATIVE_POINT_PROXY",
            "coordinate_parent": row["name"],
            "coordinate_reference_count": 1,
            "source_url": "https://www.openstreetmap.org/copyright",
            "osm_admin_area_id": f"relation/{row['osm_id']}",
        }

    def radial_catchment(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
        categories: set[str] | None = None,
        limit: int = 10_000,
    ) -> CatchmentResult:
        min_lat, max_lat, min_lon, max_lon = _bounding_box(latitude, longitude, radius_km)
        parameters: list[object] = [max_lat, min_lat, max_lon, min_lon]
        category_clause = ""
        if categories:
            placeholders = ",".join("?" for _ in categories)
            category_clause = f" AND e.category IN ({placeholders})"
            parameters.extend(sorted(categories))
        parameters.append(limit)
        rows = self.connection.execute(
            f"""
            SELECT e.* FROM osm_entity e
            JOIN osm_entity_rtree r ON r.rowid = e.rowid
            WHERE r.min_lat <= ? AND r.max_lat >= ?
              AND r.min_lon <= ? AND r.max_lon >= ?
              {category_clause}
            ORDER BY e.category, e.osm_type, e.osm_id
            LIMIT ?
            """,
            parameters,
        ).fetchall()
        entities = []
        counts: dict[str, int] = defaultdict(int)
        for row in rows:
            if haversine_km(latitude, longitude, row["lat"], row["lon"]) > radius_km:
                continue
            entity = OsmEntity(
                osm_type=row["osm_type"],
                osm_id=row["osm_id"],
                category=row["category"],
                name=row["name"],
                latitude=row["lat"],
                longitude=row["lon"],
                tags=json.loads(row["tags_json"]),
            )
            entities.append(entity)
            counts[entity.category] += 1
        return CatchmentResult(
            center_latitude=latitude,
            center_longitude=longitude,
            radius_km=radius_km,
            entities=entities,
            category_counts=dict(sorted(counts.items())),
        )

    def route(
        self,
        start_latitude: float,
        start_longitude: float,
        end_latitude: float,
        end_longitude: float,
        corridor_km: float = 5,
    ) -> RouteResult:
        direct = haversine_km(start_latitude, start_longitude, end_latitude, end_longitude)
        search_radius = direct / 2 + corridor_km
        center_lat = (start_latitude + end_latitude) / 2
        center_lon = (start_longitude + end_longitude) / 2
        min_lat, max_lat, min_lon, max_lon = _bounding_box(center_lat, center_lon, search_radius)
        rows = self.connection.execute(
            """
            SELECT w.* FROM road_way w
            JOIN road_way_rtree r ON r.rowid = w.rowid
            WHERE r.min_lat <= ? AND r.max_lat >= ?
              AND r.min_lon <= ? AND r.max_lon >= ?
            """,
            (max_lat, min_lat, max_lon, min_lon),
        ).fetchall()
        adjacency: dict[int, list[tuple[int, float, float, str]]] = defaultdict(list)
        coordinates: dict[int, tuple[float, float]] = {}
        for row in rows:
            nodes = json.loads(row["nodes_json"])
            highway = row["highway"]
            speed = _road_speed_kph(highway, row["maxspeed"])
            for left, right in zip(nodes, nodes[1:], strict=False):
                left_id, left_lat, left_lon = left
                right_id, right_lat, right_lon = right
                distance = haversine_km(left_lat, left_lon, right_lat, right_lon)
                minutes = distance / speed * 60
                coordinates[left_id] = (left_lat, left_lon)
                coordinates[right_id] = (right_lat, right_lon)
                adjacency[left_id].append((right_id, distance, minutes, highway))
                if row["oneway"] not in {"yes", "1", "true"}:
                    adjacency[right_id].append((left_id, distance, minutes, highway))
        if not coordinates:
            return _unavailable_route(direct, "No indexed OSM roads intersect the local corridor.")
        start = min(
            coordinates,
            key=lambda key: haversine_km(start_latitude, start_longitude, *coordinates[key]),
        )
        end = min(
            coordinates,
            key=lambda key: haversine_km(end_latitude, end_longitude, *coordinates[key]),
        )
        result = _dijkstra(adjacency, start, end)
        if result is None:
            return _unavailable_route(direct, "No connected local OSM route was found.")
        distance, minutes, classes = result
        return RouteResult(
            distance_km=distance,
            estimated_travel_time_minutes=minutes,
            road_classes=sorted(classes),
            method="OSM_LOCAL_NETWORK_DIJKSTRA_V1",
            connected=True,
            caveat=(
                "Travel time is an estimate from OSM road class/default speeds; it is not "
                "observed traffic time."
            ),
        )


def _dijkstra(adjacency, start: int, end: int):
    sequence = itertools.count()
    queue = [(0.0, 0.0, next(sequence), start, frozenset())]
    best = {start: 0.0}
    while queue:
        minutes, distance, _, node, classes = heapq.heappop(queue)
        if minutes > best.get(node, math.inf):
            continue
        if node == end:
            return distance, minutes, set(classes)
        for target, edge_distance, edge_minutes, highway in adjacency.get(node, []):
            candidate = minutes + edge_minutes
            if candidate < best.get(target, math.inf):
                best[target] = candidate
                heapq.heappush(
                    queue,
                    (
                        candidate,
                        distance + edge_distance,
                        next(sequence),
                        target,
                        classes | {highway},
                    ),
                )
    return None


def _bounding_box(latitude: float, longitude: float, radius_km: float):
    lat_delta = radius_km / 110.574
    lon_scale = max(math.cos(math.radians(latitude)), 0.01)
    lon_delta = radius_km / (111.320 * lon_scale)
    return (
        latitude - lat_delta,
        latitude + lat_delta,
        longitude - lon_delta,
        longitude + lon_delta,
    )


def _road_speed_kph(highway: str, maxspeed: str | None) -> float:
    if maxspeed:
        digits = "".join(character for character in maxspeed if character.isdigit())
        if digits:
            return max(5.0, min(float(digits), 120.0))
    return {
        "motorway": 80,
        "trunk": 65,
        "primary": 50,
        "secondary": 40,
        "tertiary": 30,
        "residential": 20,
        "service": 15,
        "unclassified": 20,
    }.get(highway, 12)


def _unavailable_route(direct_distance: float, caveat: str) -> RouteResult:
    return RouteResult(
        distance_km=direct_distance,
        estimated_travel_time_minutes=None,
        road_classes=[],
        method="STRAIGHT_LINE_DISTANCE_ONLY",
        connected=False,
        caveat=caveat + " Straight-line distance is reported; travel time is withheld.",
    )

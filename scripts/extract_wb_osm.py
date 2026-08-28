from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import osmium
from shapely import wkt

CATEGORIES = {
    ("amenity", "atm"): "ATM",
    ("amenity", "bank"): "BANK",
    ("amenity", "bus_station"): "TRANSPORT_HUB",
    ("amenity", "clinic"): "CLINIC",
    ("amenity", "college"): "COLLEGE",
    ("amenity", "fuel"): "FUEL_STATION",
    ("amenity", "hospital"): "HOSPITAL",
    ("amenity", "marketplace"): "MARKET",
    ("amenity", "pharmacy"): "PHARMACY",
    ("amenity", "restaurant"): "RESTAURANT",
    ("amenity", "school"): "SCHOOL",
    ("amenity", "university"): "COLLEGE",
    ("industrial", "dairy"): "DAIRY",
    ("public_transport", "platform"): "TRANSPORT_HUB",
    ("public_transport", "station"): "TRANSPORT_HUB",
    ("railway", "halt"): "TRANSPORT_HUB",
    ("railway", "station"): "TRANSPORT_HUB",
    ("shop", "bakery"): "FOOD_SHOP",
    ("shop", "beverages"): "FOOD_SHOP",
    ("shop", "convenience"): "FOOD_SHOP",
    ("shop", "dairy"): "DAIRY",
    ("shop", "department_store"): "SUPERMARKET",
    ("shop", "general"): "GENERAL_SHOP",
    ("shop", "greengrocer"): "FOOD_SHOP",
    ("shop", "mall"): "MARKET",
    ("shop", "supermarket"): "SUPERMARKET",
}


def classify(tags: dict[str, str]) -> str | None:
    for key_value, category in CATEGORIES.items():
        if tags.get(key_value[0]) == key_value[1]:
            return category
    if tags.get("building") == "warehouse" or tags.get("warehouse"):
        return "WAREHOUSE"
    if tags.get("industrial") or tags.get("landuse") == "industrial":
        return "INDUSTRIAL"
    if tags.get("place") in {
        "city",
        "town",
        "village",
        "hamlet",
        "suburb",
        "neighbourhood",
        "quarter",
    }:
        return "PLACE"
    cuisine = tags.get("cuisine", "")
    name = tags.get("name", "").casefold()
    if "tea" in cuisine or "tea" in name or "sweet" in name or "mishti" in name:
        return "TEA_OR_SWEET_SHOP"
    return None


class Extractor(osmium.SimpleHandler):
    def __init__(self, connection: sqlite3.Connection) -> None:
        super().__init__()
        self.connection = connection
        self.entities: list[tuple] = []
        self.roads: list[tuple] = []
        self.admin_areas: list[tuple] = []
        self.wkt_factory = osmium.geom.WKTFactory()

    def node(self, node) -> None:
        tags = dict(node.tags)
        category = classify(tags)
        if category and node.location.valid():
            self.entities.append(
                (
                    "node",
                    node.id,
                    category,
                    tags.get("name"),
                    node.location.lat,
                    node.location.lon,
                    json.dumps(tags, sort_keys=True, ensure_ascii=False),
                )
            )
            self._flush_if_needed()

    def way(self, way) -> None:
        tags = dict(way.tags)
        points = [
            [node.ref, node.location.lat, node.location.lon]
            for node in way.nodes
            if node.location.valid()
        ]
        if not points:
            return
        category = classify(tags)
        if category:
            latitude = sum(point[1] for point in points) / len(points)
            longitude = sum(point[2] for point in points) / len(points)
            self.entities.append(
                (
                    "way",
                    way.id,
                    category,
                    tags.get("name"),
                    latitude,
                    longitude,
                    json.dumps(tags, sort_keys=True, ensure_ascii=False),
                )
            )
        highway = tags.get("highway")
        if highway and len(points) > 1:
            latitudes = [point[1] for point in points]
            longitudes = [point[2] for point in points]
            self.roads.append(
                (
                    way.id,
                    highway,
                    tags.get("name"),
                    tags.get("maxspeed"),
                    tags.get("oneway", "no").casefold(),
                    min(latitudes),
                    max(latitudes),
                    min(longitudes),
                    max(longitudes),
                    json.dumps(points, separators=(",", ":")),
                    json.dumps(tags, sort_keys=True, ensure_ascii=False),
                )
            )
        self._flush_if_needed()

    def area(self, area) -> None:
        tags = dict(area.tags)
        admin_level = tags.get("admin_level")
        if (
            tags.get("boundary") != "administrative"
            or admin_level not in {"4", "5", "6", "7"}
            or not tags.get("name")
        ):
            return
        try:
            geometry_wkt = self.wkt_factory.create_multipolygon(area)
            geometry = wkt.loads(geometry_wkt)
        except (RuntimeError, ValueError):
            return
        if geometry.is_empty:
            return
        min_lon, min_lat, max_lon, max_lat = geometry.bounds
        self.admin_areas.append(
            (
                area.orig_id(),
                int(admin_level),
                tags["name"],
                geometry_wkt,
                min_lat,
                max_lat,
                min_lon,
                max_lon,
                json.dumps(tags, sort_keys=True, ensure_ascii=False),
            )
        )
        self._flush_if_needed()

    def _flush_if_needed(self) -> None:
        if (
            len(self.entities) >= 5_000
            or len(self.roads) >= 5_000
            or len(self.admin_areas) >= 500
        ):
            self.flush()

    def flush(self) -> None:
        if self.entities:
            self.connection.executemany(
                """
                INSERT OR REPLACE INTO osm_entity
                (osm_type, osm_id, category, name, lat, lon, tags_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                self.entities,
            )
            self.entities.clear()
        if self.roads:
            self.connection.executemany(
                """
                INSERT OR REPLACE INTO road_way
                (osm_id, highway, name, maxspeed, oneway, min_lat, max_lat,
                 min_lon, max_lon, nodes_json, tags_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                self.roads,
            )
            self.roads.clear()
        if self.admin_areas:
            self.connection.executemany(
                """
                INSERT OR REPLACE INTO admin_area
                (osm_id, admin_level, name, geometry_wkt, min_lat, max_lat,
                 min_lon, max_lon, tags_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                self.admin_areas,
            )
            self.admin_areas.clear()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_database(
    source: Path, destination: Path, expected_sha256: str | None = None
) -> dict[str, object]:
    source_hash = sha256(source)
    if expected_sha256 and source_hash != expected_sha256:
        raise ValueError(f"OSM SHA-256 mismatch: expected {expected_sha256}, got {source_hash}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".building")
    if temporary.exists():
        temporary.unlink()
    connection = sqlite3.connect(temporary)
    connection.executescript(
        """
        PRAGMA journal_mode=WAL;
        PRAGMA synchronous=NORMAL;
        CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE osm_entity (
            osm_type TEXT NOT NULL,
            osm_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            name TEXT,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            tags_json TEXT NOT NULL,
            UNIQUE(osm_type, osm_id, category)
        );
        CREATE INDEX idx_osm_entity_category ON osm_entity(category);
        CREATE TABLE road_way (
            osm_id INTEGER PRIMARY KEY,
            highway TEXT NOT NULL,
            name TEXT,
            maxspeed TEXT,
            oneway TEXT NOT NULL,
            min_lat REAL NOT NULL,
            max_lat REAL NOT NULL,
            min_lon REAL NOT NULL,
            max_lon REAL NOT NULL,
            nodes_json TEXT NOT NULL,
            tags_json TEXT NOT NULL
        );
        CREATE TABLE admin_area (
            osm_id INTEGER NOT NULL,
            admin_level INTEGER NOT NULL,
            name TEXT NOT NULL,
            geometry_wkt TEXT NOT NULL,
            min_lat REAL NOT NULL,
            max_lat REAL NOT NULL,
            min_lon REAL NOT NULL,
            max_lon REAL NOT NULL,
            tags_json TEXT NOT NULL,
            UNIQUE(osm_id, admin_level)
        );
        CREATE INDEX idx_admin_area_name_level ON admin_area(name, admin_level);
        """
    )
    handler = Extractor(connection)
    handler.apply_file(str(source), locations=True)
    handler.flush()
    connection.executescript(
        """
        CREATE VIRTUAL TABLE osm_entity_rtree USING rtree(
            rowid, min_lat, max_lat, min_lon, max_lon
        );
        INSERT INTO osm_entity_rtree
        SELECT rowid, lat, lat, lon, lon FROM osm_entity;
        CREATE VIRTUAL TABLE road_way_rtree USING rtree(
            rowid, min_lat, max_lat, min_lon, max_lon
        );
        INSERT INTO road_way_rtree
        SELECT rowid, min_lat, max_lat, min_lon, max_lon FROM road_way;
        CREATE VIRTUAL TABLE admin_area_rtree USING rtree(
            rowid, min_lat, max_lat, min_lon, max_lon
        );
        INSERT INTO admin_area_rtree
        SELECT rowid, min_lat, max_lat, min_lon, max_lon FROM admin_area;
        """
    )
    counts = {
        "entities": connection.execute("SELECT count(*) FROM osm_entity").fetchone()[0],
        "roads": connection.execute("SELECT count(*) FROM road_way").fetchone()[0],
        "admin_areas": connection.execute("SELECT count(*) FROM admin_area").fetchone()[0],
    }
    category_counts = dict(
        connection.execute(
            "SELECT category, count(*) FROM osm_entity GROUP BY category ORDER BY category"
        ).fetchall()
    )
    metadata = {
        "source_path": str(source),
        "source_sha256": source_hash,
        "source_size_bytes": str(source.stat().st_size),
        "extracted_at": datetime.now(UTC).isoformat(),
        "extractor_version": "WB_OSM_SQLITE_V2_DISTRICT_BOUNDARIES",
        "entity_count": str(counts["entities"]),
        "road_way_count": str(counts["roads"]),
        "admin_area_count": str(counts["admin_areas"]),
        "category_counts": json.dumps(category_counts, sort_keys=True),
        "osm_completeness_caveat": (
            "OSM is volunteered proxy evidence and is not a complete business registry."
        ),
    }
    connection.executemany("INSERT INTO metadata VALUES (?, ?)", metadata.items())
    connection.commit()
    connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    connection.close()
    temporary.replace(destination)
    return {
        **counts,
        "categories": category_counts,
        "source_sha256": source_hash,
        "destination_sha256": sha256(destination),
        "destination_size_bytes": destination.stat().st_size,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract indexed West Bengal OSM evidence")
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    result = create_database(args.source, args.destination, args.expected_sha256)
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()

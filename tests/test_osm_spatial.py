from __future__ import annotations

from pathlib import Path

from backend.evidence.store import EvidenceStore
from backend.models.geography import GeographicIdentity
from backend.service import _spatial_context
from backend.spatial.osm_store import OsmSpatialStore
from scripts.enrich_geographies_osm import enrich
from scripts.extract_wb_osm import create_database

OSM_XML = """<?xml version="1.0" encoding="UTF-8"?>
<osm version="0.6" generator="test">
  <node id="1" lat="22.5700" lon="88.3600" />
  <node id="2" lat="22.5710" lon="88.3610">
    <tag k="amenity" v="marketplace"/><tag k="name" v="Test Market"/>
  </node>
  <node id="3" lat="22.5720" lon="88.3620" />
  <way id="10">
    <nd ref="1"/><nd ref="2"/><nd ref="3"/>
    <tag k="highway" v="primary"/><tag k="name" v="Test Road"/>
  </way>
</osm>
"""

PLACE_OSM_XML = """<?xml version="1.0" encoding="UTF-8"?>
<osm version="0.6" generator="test">
  <node id="20" lat="22.7000" lon="88.4000">
    <tag k="place" v="town"/><tag k="name" v="Barasat"/>
  </node>
</osm>
"""


def test_extract_catchment_and_network_route(tmp_path: Path) -> None:
    source = tmp_path / "tiny.osm"
    source.write_text(OSM_XML)
    database = tmp_path / "osm.sqlite"
    result = create_database(source, database)
    assert result["entities"] == 1
    assert result["roads"] == 1

    store = OsmSpatialStore(database)
    catchment = store.radial_catchment(22.57, 88.36, 1)
    assert catchment.category_counts == {"MARKET": 1}
    assert catchment.entities[0].name == "Test Market"

    route = store.route(22.57, 88.36, 22.572, 88.362, corridor_km=1)
    assert route.connected
    assert route.distance_km is not None
    assert route.distance_km > 0
    assert route.estimated_travel_time_minutes is not None
    assert route.method == "OSM_LOCAL_NETWORK_DIJKSTRA_V1"


def test_exact_osm_place_crosswalk_adds_proxy_coordinate(tmp_path: Path) -> None:
    source = tmp_path / "places.osm"
    source.write_text(PLACE_OSM_XML)
    osm_database = tmp_path / "osm.sqlite"
    create_database(source, osm_database)
    evidence_database = tmp_path / "evidence.sqlite"
    store = EvidenceStore(evidence_database)
    store.put_geography(
        GeographicIdentity(
            geo_id="test:barasat",
            district="North 24 Parganas",
            locality="Barasat",
            locality_type="TOWN",
        )
    )
    report = enrich(evidence_database, osm_database, tmp_path / "report.json")
    updated = store.get_geography("test:barasat")
    assert report["matched"] == 1
    assert updated is not None
    assert updated.latitude == 22.7
    assert updated.osm_ids == ["node/20"]
    assert "OSM_PLACE_COORDINATE_PROXY" in updated.quality_flags


def test_service_spatial_context_is_proxy_and_withholds_capacity(
    tmp_path: Path, monkeypatch
) -> None:
    source = tmp_path / "tiny.osm"
    source.write_text(OSM_XML)
    database = tmp_path / "osm.sqlite"
    create_database(source, database)
    monkeypatch.setenv("SIH26091_OSM_SQLITE_PATH", str(database))
    geography = GeographicIdentity(
        geo_id="test",
        district="Kolkata",
        locality="Test",
        locality_type="TEST",
        latitude=22.57,
        longitude=88.36,
    )
    context = _spatial_context(geography, 1, "dairy")
    assert context["catchment"]["category_counts"] == {"MARKET": 1}
    assert context["catchment"]["nearest_market_route"]["connected"]
    assert context["competition"]["capacity"] is None
    assert context["competition"]["capacity_confidence"] == "UNKNOWN"

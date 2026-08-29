from backend.evidence.current_geography import rebuild_current_geography
from backend.evidence.districts import CURRENT_WEST_BENGAL_DISTRICTS
from backend.evidence.store import EvidenceStore
from backend.models.geography import GeographicIdentity


def _identity(
    geo_id: str,
    district: str,
    locality: str,
    *,
    block: str | None = None,
) -> GeographicIdentity:
    return GeographicIdentity(
        geo_id=geo_id,
        district=district,
        locality=locality,
        locality_type="VILLAGE",
        block=block,
    )


def test_current_layer_separates_bardhaman_history_and_builds_parent_chain():
    store = EvidenceStore()
    store.put_geography(_identity("DS057:purba:memari", "Bardhaman", "Memari", block="Memari-I"))
    store.put_geography(
        _identity(
            "DS057:paschim:andalu",
            "PASCHIM BARDHAMAN",
            "Andal",
            block="Andal",
        )
    )
    store.put_geography(_identity("CENSUS2011:memari", "Barddhaman", "Memari", block="Memari-I"))
    store.put_geography(_identity("CENSUS2011:ambiguous", "Barddhaman", "Repeated Name"))

    report = rebuild_current_geography(store.connection)

    assert report["current_districts"] == 23
    assert store.list_districts() == list(CURRENT_WEST_BENGAL_DISTRICTS)
    assert "Barddhaman" not in store.list_districts()
    assert "Purba Bardhaman" in store.list_districts()
    purba = store.search_geographies("Memari", district="Purba Bardhaman")
    assert len(purba) == 1
    assert purba[0].district == "Purba Bardhaman"
    assert store.search_geographies("Memari", district="Paschim Bardhaman") == []
    crosswalk = store.get_crosswalks("CENSUS2011:memari")
    assert crosswalk[0].relation == "EXACT_NAME_AND_COMPATIBLE_CURRENT_HIERARCHY"
    assert store.get_crosswalks("CENSUS2011:ambiguous") == []

    current_row = store.connection.execute(
        "SELECT parent_current_id FROM current_geo_entity WHERE source_geo_id = ?",
        ("DS057:purba:memari",),
    ).fetchone()
    parent = store.get_current_entity(current_row["parent_current_id"])
    assert parent is not None
    assert parent.entity_type == "BLOCK"
    assert parent.parent_current_id == parent.district_current_id


def test_current_search_ranking_and_type_filter():
    store = EvidenceStore()
    store.put_geography(_identity("DS057:exact", "Kolkata", "New Town"))
    store.put_geography(_identity("DS057:prefix", "Kolkata", "New Town Action Area"))
    store.put_geography(_identity("DS057:substring", "Kolkata", "Greater New Town"))
    rebuild_current_geography(store.connection)

    rows = store.search_geographies("New Town", district="Kolkata", locality_type="VILLAGE")
    assert [row.geo_id for row in rows] == [
        "DS057:exact",
        "DS057:prefix",
        "DS057:substring",
    ]

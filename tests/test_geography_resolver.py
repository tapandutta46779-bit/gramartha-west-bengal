from backend.evidence.geography_resolver import resolve_locality
from backend.evidence.store import EvidenceStore
from backend.models.geography import GeographicIdentity, ResolutionMethod


def identity(geo_id: str, district: str, locality: str, block: str):
    return GeographicIdentity(
        geo_id=geo_id,
        district=district,
        locality=locality,
        block=block,
        locality_type="VILLAGE",
        source_ids=["controlled"],
    )


def test_duplicate_locality_is_never_silently_merged():
    store = EvidenceStore()
    store.put_geography(identity("one", "Bankura", "Rampur", "Block A"))
    store.put_geography(identity("two", "Bankura", "Rampur", "Block B"))
    resolution = resolve_locality(store, locality="Rampur", district="Bankura")
    assert resolution.resolution_method == ResolutionMethod.AMBIGUOUS
    assert resolution.resolved_geo_id is None
    assert len(resolution.candidates) == 2
    resolved = resolve_locality(store, locality="Rampur", district="Bankura", parent="Block B")
    assert resolved.resolved_geo_id == "two"


def test_district_alias_is_explicit_and_flagged_as_alias_resolution():
    store = EvidenceStore()
    store.put_geography(identity("barasat", "24 Paraganas North", "Barasat", "Barasat - I"))
    resolution = resolve_locality(
        store,
        locality="Barasat",
        district="North 24 Parganas",
        parent="Barasat - I",
    )
    assert resolution.resolved_geo_id == "barasat"
    assert resolution.resolution_method == ResolutionMethod.EXACT_ALIAS
    assert resolution.confidence < 1

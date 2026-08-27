from pathlib import Path

from openpyxl import Workbook

from backend.evidence.livestock_adapter import ingest_livestock_workbook
from backend.evidence.store import EvidenceStore


def test_adapter_preserves_source_labels_and_aggregates_sexes(tmp_path: Path):
    path = tmp_path / "fixture.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Rural Male Population"
    header = [
        "state_name",
        "district_name",
        "block_name",
        "village_name",
        "cattle",
        "buffalo",
        "sheep",
        "goat",
        "pig",
    ]
    sheet.append(header)
    sheet.append(["West Bengal", "District Source Spelling", "Block A", "Village A", 2, 0, 0, 1, 0])
    female = workbook.create_sheet("Rural Female Population")
    female.append(header)
    female.append(
        ["West Bengal", "District Source Spelling", "Block A", "Village A", 3, 0, 0, 4, 0]
    )
    workbook.save(path)

    store = EvidenceStore()
    result = ingest_livestock_workbook(path, store, verify_checksum=False)
    assert result == {"source_rows": 2, "geographies": 1, "evidence_records": 5}
    geo = store.search_geographies("Village A")[0]
    assert geo.district == "District Source Spelling"
    cattle = next(
        record for record in store.get_evidence(geo.geo_id) if record.variable.endswith("cattle")
    )
    assert cattle.value == 5
    assert cattle.attributes["sex_breakdown"] == {"male": 2, "female": 3}

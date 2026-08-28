from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from openpyxl import Workbook

from backend.evidence.store import EvidenceStore
from backend.models.geography import GeographicIdentity
from scripts.build_wb_census_crosswalk import sha256
from scripts.ingest_wb_census_pca import ingest


def test_pca_ingest_preserves_2011_observation_semantics(tmp_path: Path) -> None:
    input_dir = tmp_path / "pca"
    input_dir.mkdir()
    path = input_dir / "WB_2011_PCA_TV_1901.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(
        [
            "State",
            "District",
            "Subdistt",
            "Town/Village",
            "Ward",
            "EB",
            "Level",
            "Name",
            "TRU",
            "No_HH",
            "TOT_P",
            "TOT_M",
            "TOT_F",
        ]
    )
    sheet.append(
        [
            "19",
            "337",
            "02325",
            "322758",
            "0000",
            "000000",
            "VILLAGE",
            "Test",
            "Rural",
            10,
            40,
            21,
            19,
        ]
    )
    workbook.save(path)
    manifest = {
        "created_at": datetime.now(UTC).isoformat(),
        "files": [
            {
                "filename": path.name,
                "catalog_url": "https://censusindia.gov.in/nada/index.php/catalog/1",
                "sha256": sha256(path),
            }
        ],
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest))
    database = tmp_path / "evidence.sqlite"
    store = EvidenceStore(database)
    store.put_geography(
        GeographicIdentity(
            geo_id="census:test",
            district="North Twenty Four Parganas",
            locality="Test",
            locality_type="VILLAGE",
            census_code="322758",
        )
    )
    result = ingest(input_dir, manifest_path, database)
    evidence = store.get_evidence("census:test")
    assert result["source_rows"] == 1
    assert result["unique_evidence_records"] == 4
    assert {item.variable: item.value for item in evidence}["population_observed_2011"] == 40
    assert all(item.observation_date.year == 2011 for item in evidence)
    assert all("NOT_CURRENT_POPULATION" in item.quality_flags for item in evidence)

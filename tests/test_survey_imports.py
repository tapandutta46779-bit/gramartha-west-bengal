from __future__ import annotations

import json
from pathlib import Path

from scripts.import_asuse import build_asuse_priors
from scripts.import_hces import build_hces_priors


def test_hces_weighted_prior_is_per_capita_and_month_normalized(tmp_path: Path) -> None:
    (tmp_path / "households.csv").write_text(
        "id,state,district,region,sector,weight,size\n"
        "1,19,North 24 Parganas,R1,rural,2,4\n"
        "2,18,Other,R2,rural,100,5\n"
    )
    (tmp_path / "items.csv").write_text(
        "id,item,quantity,expenditure,days\n1,milk,28,1400,28\n2,milk,999,999,30\n"
    )
    mapping = {
        "dataset_id": "HCES-TEST",
        "dataset_version": "test",
        "official_source_url": "https://microdata.gov.in/",
        "west_bengal_values": ["19"],
        "households": {
            "file": "households.csv",
            "join_columns": ["id"],
            "state_column": "state",
            "district_column": "district",
            "nss_region_column": "region",
            "sector_column": "sector",
            "weight_column": "weight",
            "household_size_column": "size",
        },
        "items": {
            "file": "items.csv",
            "join_columns": ["id"],
            "item_code_column": "item",
            "quantity_column": "quantity",
            "expenditure_column": "expenditure",
            "recall_days_column": "days",
            "quantity_unit": "litres",
        },
        "item_categories": {"milk": ["milk"]},
    }
    mapping_path = tmp_path / "mapping.json"
    mapping_path.write_text(json.dumps(mapping))
    result = build_hces_priors(tmp_path, mapping_path, tmp_path / "result.json")
    prior = result["priors"][0]
    assert result["west_bengal_households"] == 1
    assert prior["monthly_quantity_per_capita"] == 7.5
    assert prior["monthly_expenditure_inr_per_capita"] == 375
    assert prior["evidence_type"] == "SAMPLED_PRIOR"


def test_asuse_weighted_sector_prior(tmp_path: Path) -> None:
    (tmp_path / "enterprise.csv").write_text(
        "state,district,sector,nic,weight,receipts,workers,assets\n"
        "19,Kolkata,urban,47211,2,100,2,50\n"
        "19,Kolkata,urban,47212,1,400,5,200\n"
        "18,Other,urban,47211,99,999,9,999\n"
    )
    mapping = {
        "dataset_id": "ASUSE-TEST",
        "dataset_version": "test",
        "official_source_url": "https://microdata.gov.in/",
        "west_bengal_values": ["19"],
        "enterprises": {
            "file": "enterprise.csv",
            "state_column": "state",
            "district_column": "district",
            "sector_column": "sector",
            "nic_column": "nic",
            "weight_column": "weight",
            "measure_columns": {
                "receipts_inr": "receipts",
                "workers": "workers",
                "assets_inr": "assets",
            },
        },
    }
    mapping_path = tmp_path / "mapping.json"
    mapping_path.write_text(json.dumps(mapping))
    result = build_asuse_priors(tmp_path, mapping_path, tmp_path / "result.json")
    prior = result["priors"][0]
    assert prior["nic_2_digit"] == "47"
    assert prior["weighted_means"]["receipts_inr"] == 200
    assert prior["weighted_means"]["workers"] == 3
    assert prior["evidence_type"] == "SAMPLED_PRIOR"

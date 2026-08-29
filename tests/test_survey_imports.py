from __future__ import annotations

import json
import zipfile
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


def test_hces_zero_consumption_household_remains_in_denominator(tmp_path: Path) -> None:
    (tmp_path / "households.csv").write_text(
        "id,state,district,region,sector,weight,size\n01,19,D,R,rural,1,2\n2,19,D,R,rural,1,2\n"
    )
    (tmp_path / "items.csv").write_text("id,item,quantity,expenditure,days\n1.0,milk,14,140,7\n")
    mapping = {
        "dataset_id": "HCES-ZERO-TEST",
        "dataset_version": "test",
        "official_source_url": "https://microdata.gov.in/",
        "west_bengal_values": ["19"],
        "normalize_join_codes": True,
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
    archive = tmp_path / "input.zip"
    with zipfile.ZipFile(archive, "w") as handle:
        handle.write(tmp_path / "households.csv", "households.csv")
        handle.write(tmp_path / "items.csv", "items.csv")
    result = build_hces_priors(archive, mapping_path, tmp_path / "result.json")
    prior = result["priors"][0]
    assert prior["monthly_quantity_per_capita"] == 15
    assert prior["monthly_expenditure_inr_per_capita"] == 150
    assert prior["sample_households"] == 2
    assert result["inputs"][0]["file"] == "input.zip"


def test_asuse_weighted_sector_prior(tmp_path: Path) -> None:
    key = "fsu_serial_no,segment_no,second_stage_stratum_no,sample_est_no"
    files = {
        "LEVEL - 02(Block 2).csv": (
            f"{key},nss_region,district,sector,major_nic_2dig,major_nic_5dig,"
            "nature_of_operation,months_operated,mlt\n"
            "1,1,01,01,191,16,2,47,47211,1,12,200\n"
            "2,1,01,01,191,16,2,47,47212,2,6,100\n"
            "3,1,01,01,181,01,2,47,47211,1,12,9900\n"
        ),
        "LEVEL - 03.csv": (f"{key},ref_period_type\n1,1,01,01,1\n2,1,01,01,1\n3,1,01,01,1\n"),
        "LEVEL - 08.csv": (
            f"{key},item_no,value_rs\n"
            "1,1,01,01,765,50\n1,1,01,01,766,150\n1,1,01,01,769,100\n"
            "2,1,01,01,765,100\n2,1,01,01,766,500\n2,1,01,01,769,400\n"
        ),
        "LEVEL - 09.csv": (f"{key},item_no,total_workers\n1,1,01,01,789,2\n2,1,01,01,789,5\n"),
        "LEVEL - 11.csv": (
            f"{key},item_no,mv_assets_owned\n"
            "1,1,01,01,1001,10\n1,1,01,01,1003,20\n1,1,01,01,1019,40\n"
            "2,1,01,01,1001,20\n2,1,01,01,1003,50\n2,1,01,01,1019,80\n"
        ),
    }
    archive = tmp_path / "asuse.zip"
    with zipfile.ZipFile(archive, "w") as handle:
        for name, content in files.items():
            handle.writestr(name, content)
    mapping = {
        "dataset_id": "ASUSE-TEST",
        "dataset_version": "test",
        "official_source_url": "https://microdata.gov.in/",
        "state_code": "19",
        "weight_divisor": 100,
        "members": {
            "profile": "LEVEL - 02",
            "reference_period": "LEVEL - 03",
            "financials": "LEVEL - 08",
            "workers": "LEVEL - 09",
            "assets": "LEVEL - 11",
        },
        "financial_item_codes": {"input": "765", "output": "766", "gva": "769"},
        "total_workers_item_code": "789",
        "land_asset_item_code": "1001",
        "total_fixed_assets_excluding_land_item_code": "1019",
        "equipment_asset_item_codes": ["1003", "1004", "1006", "1007", "1008"],
    }
    mapping_path = tmp_path / "mapping.json"
    mapping_path.write_text(json.dumps(mapping))
    result = build_asuse_priors(archive, mapping_path, tmp_path / "result.json")
    prior = result["priors"][0]
    assert prior["nic_2_digit"] == "47"
    assert prior["weighted_enterprises"] == 3
    assert prior["weighted_metric_summaries"]["annual_gva_inr"]["mean"] == 1600
    assert prior["weighted_metric_summaries"]["workers"]["mean"] == 3
    assert prior["weighted_metric_summaries"]["equipment_investment_owned"]["mean"] == 30
    assert prior["evidence_type"] == "SAMPLED_PRIOR"

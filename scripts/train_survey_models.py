from __future__ import annotations

import argparse
import csv
import io
import json
import math
import zipfile
from collections import defaultdict
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

import joblib
import numpy as np
from sklearn.base import clone
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline

from scripts.import_asuse import _enterprise_key, _member_name
from scripts.import_hces import _key, _number, file_sha256

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "work/raw_stage"
OUTPUT = ROOT / "outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS/models"


def weighted_metrics(actual: np.ndarray, predicted: np.ndarray, weight: np.ndarray) -> dict:
    error = predicted - actual
    actual_mean = float(np.average(actual, weights=weight))
    predicted_mean = float(np.average(predicted, weights=weight))
    order = np.argsort(predicted)
    calibration_gaps = []
    for indexes in np.array_split(order, min(10, len(order))):
        if len(indexes):
            calibration_gaps.append(
                abs(
                    float(np.average(predicted[indexes], weights=weight[indexes]))
                    - float(np.average(actual[indexes], weights=weight[indexes]))
                )
            )
    return {
        "mae": float(np.average(np.abs(error), weights=weight)),
        "rmse": math.sqrt(float(np.average(error**2, weights=weight))),
        "weighted_bias": float(np.average(error, weights=weight)),
        "actual_weighted_mean": actual_mean,
        "predicted_weighted_mean": predicted_mean,
        "mean_calibration_ratio": predicted_mean / actual_mean if actual_mean else None,
        "decile_calibration_mae": float(np.mean(calibration_gaps)),
    }


def _fit_model(model: Pipeline, features: list[dict], target, weight) -> Pipeline:
    model.fit(features, target, model__sample_weight=weight)
    return model


def _category_baseline(
    train_categories: list[str],
    train_target: np.ndarray,
    train_weight: np.ndarray,
    test_categories: list[str],
) -> np.ndarray:
    totals: dict[str, list[float]] = defaultdict(lambda: [0.0, 0.0])
    for category, value, weight in zip(train_categories, train_target, train_weight, strict=True):
        totals[category][0] += float(value * weight)
        totals[category][1] += float(weight)
    fallback = float(np.average(train_target, weights=train_weight))
    return np.array(
        [
            totals[value][0] / totals[value][1] if totals[value][1] else fallback
            for value in test_categories
        ]
    )


def geographic_holdout(
    *,
    features: list[dict],
    target: np.ndarray,
    weight: np.ndarray,
    districts: list[str],
    categories: list[str],
    models: dict[str, Pipeline],
) -> dict:
    unique_districts = sorted(set(districts))
    predictions = {
        "category_weighted_mean_baseline": np.zeros(len(target), dtype=float),
        **{name: np.zeros(len(target), dtype=float) for name in models},
    }
    fold_rows: dict[str, list[dict]] = defaultdict(list)
    district_array = np.asarray(districts)
    for district in unique_districts:
        test_index = np.flatnonzero(district_array == district)
        train_index = np.flatnonzero(district_array != district)
        train_features = [features[index] for index in train_index]
        test_features = [features[index] for index in test_index]
        predictions["category_weighted_mean_baseline"][test_index] = _category_baseline(
            [categories[index] for index in train_index],
            target[train_index],
            weight[train_index],
            [categories[index] for index in test_index],
        )
        for name, template in models.items():
            fitted = _fit_model(
                clone(template), train_features, target[train_index], weight[train_index]
            )
            predictions[name][test_index] = fitted.predict(test_features)
        for name, values in predictions.items():
            fold_rows[name].append(
                {
                    "held_out_district_code": district,
                    "test_rows": len(test_index),
                    **weighted_metrics(target[test_index], values[test_index], weight[test_index]),
                }
            )
    candidates = {}
    for name, values in predictions.items():
        candidates[name] = {
            "geographic_holdout_metrics": weighted_metrics(target, values, weight),
            "district_holdout_folds": fold_rows[name],
        }
    selected = min(
        candidates,
        key=lambda name: candidates[name]["geographic_holdout_metrics"]["mae"],
    )
    return {"selected_by_weighted_mae": selected, "candidates": candidates}


def _csv_reader(archive: zipfile.ZipFile, name: str):
    raw = archive.open(name)
    text = io.TextIOWrapper(raw, encoding="utf-8-sig", errors="strict", newline="")
    return raw, text, csv.DictReader(text)


def load_hces_2023_training_rows() -> tuple[
    list[dict], np.ndarray, np.ndarray, list[str], list[str]
]:
    archive_path = RAW / "HCES_2023_24_RESTRICTED_MICRODATA/HCES_Data_2023-24_Csv.zip"
    mapping = json.loads((ROOT / "config/hces_2023_24_mapping.json").read_text())
    household_spec = mapping["households"]
    item_spec = mapping["items"]
    join_columns = household_spec["join_columns"]
    households = {}
    features_by_key: dict[tuple[str, ...], dict] = {}
    with zipfile.ZipFile(archive_path) as archive:
        raw, text, rows = _csv_reader(archive, household_spec["file"])
        try:
            for row in rows:
                if row["State"] != "19":
                    continue
                household_key = _key(row, join_columns)
                size = _number(row, "HOUSEHOLD_SIZE")
                if size <= 0:
                    continue
                households[household_key] = {
                    "district": row["District"],
                    "sector": row["Sector"],
                    "size": size,
                    "weight": _number(row, "MULTIPLIER") * size,
                    "visit_month": row["VISIT_MONTH"],
                }
        finally:
            text.close()
            raw.close()
        feature_name = next(name for name in archive.namelist() if "LEVEL - 03.csv" in name)
        raw, text, rows = _csv_reader(archive, feature_name)
        categorical = [
            "Household_Type",
            "Religion_of_HH_Head",
            "Social_Group_of_HH_Head",
            "Land_Ownership",
            "Type_of_Dwelling_Unit",
            "Energy_Source_Cooking",
            "Energy_Source_Lighting",
            "Ration_Card_Type",
            "Benefitted_From_PMGKY",
        ]
        try:
            for row in rows:
                if row["State"] != "19":
                    continue
                household_key = _key(row, join_columns)
                if household_key not in households:
                    continue
                features_by_key[household_key] = {
                    **{name: row[name] or "MISSING" for name in categorical},
                    "household_size": households[household_key]["size"],
                    "land_area_acres": _number(row, "Total_Area_Land_Owned_Acres"),
                    "sector": households[household_key]["sector"],
                    "visit_month": households[household_key]["visit_month"][:2] or "MISSING",
                }
        finally:
            text.close()
            raw.close()
        quantities = defaultdict(float)
        raw, text, rows = _csv_reader(archive, item_spec["file"])
        try:
            for row in rows:
                if row["Item_Code"] != "160":
                    continue
                household_key = _key(row, item_spec["join_columns"])
                if household_key in households:
                    quantities[household_key] += _number(row, "Total_Consumption_Quantity") * 30 / 7
        finally:
            text.close()
            raw.close()
    features = []
    target = []
    weights = []
    districts = []
    categories = []
    for household_key, household in households.items():
        if household_key not in features_by_key:
            continue
        features.append(features_by_key[household_key])
        target.append(quantities[household_key] / household["size"])
        weights.append(household["weight"])
        districts.append(household["district"])
        categories.append(household["sector"])
    return features, np.asarray(target), np.asarray(weights), districts, categories


def load_asuse_2025_training_rows() -> tuple[
    list[dict], np.ndarray, np.ndarray, list[str], list[str]
]:
    archive_path = RAW / "ASUSE_2025_RESTRICTED_MICRODATA/CSV_ASUSE2025.zip"
    mapping = json.loads((ROOT / "config/asuse_2025_mapping.json").read_text())
    enterprises = {}
    with zipfile.ZipFile(archive_path) as archive:
        raw, text, rows = _csv_reader(archive, _member_name(archive, mapping["members"]["profile"]))
        categorical = [
            "b2i204",
            "b2i206",
            "b2i208",
            "b2i211",
            "b2i213",
            "b2i216",
            "b2i219",
            "b2i220",
            "b2i221",
            "b2i227",
        ]
        try:
            for row in rows:
                if row["nssreg"][:2] != "19":
                    continue
                enterprises[_enterprise_key(row)] = {
                    "district": row["dist"],
                    "sector": row["sec"],
                    "nic2": row["b2i202a"],
                    "nature": row["b2i216"],
                    "months": _number(row, "b2i217"),
                    "weight": _number(row, "mlt") / 100,
                    "features": {
                        **{name: row[name] or "MISSING" for name in categorical},
                        "sector": row["sec"],
                        "nic2": row["b2i202a"],
                        "years_operation": _number(row, "b2i214"),
                        "months_operated": _number(row, "b2i217"),
                        "daily_work_hours": _number(row, "b2i218"),
                    },
                }
        finally:
            text.close()
            raw.close()
        raw, text, rows = _csv_reader(
            archive, _member_name(archive, mapping["members"]["reference_period"])
        )
        try:
            for row in rows:
                enterprise = enterprises.get(_enterprise_key(row))
                if enterprise:
                    enterprise["reference_type"] = row["b2pt2i265"]
        finally:
            text.close()
            raw.close()
        raw, text, rows = _csv_reader(
            archive, _member_name(archive, mapping["members"]["financials"])
        )
        try:
            for row in rows:
                if row["b7pt1b7pt2c2"] != "769":
                    continue
                enterprise = enterprises.get(_enterprise_key(row))
                if enterprise:
                    enterprise["gva"] = _number(row, "b7pt1b7pt2c3")
        finally:
            text.close()
            raw.close()
    features = []
    target = []
    weights = []
    districts = []
    categories = []
    for enterprise in enterprises.values():
        if "gva" not in enterprise or enterprise["weight"] <= 0:
            continue
        if enterprise.get("reference_type") == "4":
            factor = 1
        elif enterprise["nature"] == "1":
            factor = 12
        elif enterprise["months"] > 0:
            factor = enterprise["months"]
        else:
            continue
        features.append(enterprise["features"])
        target.append(enterprise["gva"] * factor)
        weights.append(enterprise["weight"])
        districts.append(enterprise["district"])
        categories.append(f"{enterprise['sector']}|{enterprise['nic2']}")
    return features, np.asarray(target), np.asarray(weights), districts, categories


def model_templates(seed: int = 26091) -> dict[str, Pipeline]:
    return {
        "ridge_one_hot": Pipeline([("features", DictVectorizer()), ("model", Ridge(alpha=10.0))]),
        "random_forest": Pipeline(
            [
                ("features", DictVectorizer()),
                (
                    "model",
                    RandomForestRegressor(
                        n_estimators=32,
                        max_depth=12,
                        min_samples_leaf=20,
                        max_features=0.7,
                        random_state=seed,
                        n_jobs=-1,
                    ),
                ),
            ]
        ),
    }


def train_task(
    *,
    task_id: str,
    loader: Callable,
    source_path: Path,
    target_definition: str,
    production_estimator: str,
    production_reason: str,
) -> dict:
    features, target, weight, districts, categories = loader()
    validation = geographic_holdout(
        features=features,
        target=target,
        weight=weight,
        districts=districts,
        categories=categories,
        models=model_templates(),
    )
    OUTPUT.mkdir(parents=True, exist_ok=True)
    artifacts = {}
    for name, template in model_templates().items():
        fitted = _fit_model(clone(template), features, target, weight)
        artifact_path = OUTPUT / f"{task_id}_{name}.joblib"
        joblib.dump(fitted, artifact_path)
        artifacts[name] = {
            "path": str(artifact_path.relative_to(ROOT)),
            "size_bytes": artifact_path.stat().st_size,
            "sha256": file_sha256(artifact_path),
        }
    selected = validation["selected_by_weighted_mae"]
    return {
        "task_id": task_id,
        "trained_at": datetime.now(UTC).isoformat(),
        "source_file": str(source_path.relative_to(ROOT)),
        "source_sha256": file_sha256(source_path),
        "target_definition": target_definition,
        "training_rows": len(target),
        "district_groups": len(set(districts)),
        "zero_target_rows": int(np.sum(target == 0)),
        "validation_strategy": "leave-one-district-out geographic holdout",
        "algorithm_selected_by_holdout_mae": selected,
        "production_estimator": production_estimator,
        "production_selection_reason": production_reason,
        "validation": validation,
        "artifacts": artifacts,
    }


def train_all() -> dict:
    hces_path = RAW / "HCES_2023_24_RESTRICTED_MICRODATA/HCES_Data_2023-24_Csv.zip"
    asuse_path = RAW / "ASUSE_2025_RESTRICTED_MICRODATA/CSV_ASUSE2025.zip"
    registry = {
        "registry_version": "survey-model-registry-v1",
        "created_at": datetime.now(UTC).isoformat(),
        "tasks": [
            train_task(
                task_id="hces_2023_24_household_liquid_milk",
                loader=load_hces_2023_training_rows,
                source_path=hces_path,
                target_definition=(
                    "zero-inclusive monthly liquid-milk litres per household member; item 160, "
                    "30/7 recall conversion"
                ),
                production_estimator="DIRECT_WEIGHTED_DISTRICT_SECTOR_SURVEY_PRIOR",
                production_reason=(
                    "Ordinary locality requests do not supply household micro-features; the direct "
                    "person-weighted survey estimator is production-safe, while trained ML is "
                    "retained for validated comparison only."
                ),
            ),
            train_task(
                task_id="asuse_2025_enterprise_annual_gva",
                loader=load_asuse_2025_training_rows,
                source_path=asuse_path,
                target_definition=(
                    "annualized enterprise GVA in INR using official item 769 and m rule"
                ),
                production_estimator="DIRECT_WEIGHTED_DISTRICT_SECTOR_NIC2_SURVEY_PRIOR",
                production_reason=(
                    "The direct survey estimator preserves published geography/sector weights and "
                    "does not invent an individual incumbent's capacity or sales."
                ),
            ),
        ],
    }
    path = OUTPUT / "model_registry.json"
    path.write_text(json.dumps(registry, indent=2) + "\n")
    return registry


def main() -> None:
    parser = argparse.ArgumentParser(description="Train and geographically validate survey models")
    parser.parse_args()
    registry = train_all()
    print(
        json.dumps(
            {
                task["task_id"]: {
                    "rows": task["training_rows"],
                    "holdout_selected": task["algorithm_selected_by_holdout_mae"],
                    "metrics": task["validation"]["candidates"][
                        task["algorithm_selected_by_holdout_mae"]
                    ]["geographic_holdout_metrics"],
                }
                for task in registry["tasks"]
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

from __future__ import annotations

import csv
import json
from pathlib import Path

from scripts.build_wb_census_crosswalk import sha256

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS"


def row(
    dataset_id: str,
    path: str,
    source_url: str,
    coverage: str,
    role: str,
    status: str = "ACQUIRED",
    blocker: str = "",
) -> dict[str, object]:
    local = ROOT / path
    return {
        "dataset_id": dataset_id,
        "local_path": path,
        "size_bytes": local.stat().st_size,
        "sha256": sha256(local),
        "source_url": source_url,
        "coverage": coverage,
        "role": role,
        "status": status,
        "blocker": blocker,
    }


def build() -> list[dict[str, object]]:
    rows = [
        row(
            "DS057-RAW-NATIONAL",
            "work/raw_stage/DS057_ALL_WEST_BENGAL/VillageAndWardLevelDataMale-Female.xlsx",
            "https://www.dahd.gov.in/sites/default/files/2023-07/VillageAndWardLevelDataMale-Female.xlsx",
            "India; retained because no WB publisher subset",
            "raw source",
        ),
        row(
            "DS057-WB-ALL",
            "outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS/DS057_West_Bengal_All_Available_Livestock_Localities.xlsx",
            "derived from DS057-RAW-NATIONAL",
            "Every available West Bengal district/locality row",
            "derived lossless state extract",
        ),
        row(
            "DS071-WB-OSM-PBF",
            "work/raw_stage/DS071_WEST_BENGAL/west_bengal.pbf",
            "https://geo2day.com/asia/india/west_bengal.pbf",
            "West Bengal regional extract",
            "raw source",
        ),
        row(
            "DS071-WB-OSM-SQLITE",
            "data/west_bengal_osm.sqlite",
            "derived from DS071-WB-OSM-PBF",
            "West Bengal",
            "indexed operational derivative",
        ),
        row(
            "CENSUS2011-LCD-NATIONAL",
            "work/raw_stage/CENSUS_2011_LOCATION_DIRECTORY/PC11_TV_DIR.xlsx",
            "https://censusindia.gov.in/nada/index.php/catalog/42648",
            "India; retained because publisher provides one directory",
            "raw source",
        ),
        row(
            "CENSUS2011-LCD-WB",
            "outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS/CENSUS2011_West_Bengal_Location_Directory.csv",
            "derived from CENSUS2011-LCD-NATIONAL",
            "West Bengal state code 19",
            "derived state extract",
        ),
        row(
            "BAHS2025",
            "work/raw_stage/BAHS_2025/BasicAnimalHusbandryStatistics2025.pdf",
            "https://www.dahd.gov.in/sites/default/files/2025-12/BasicAnimalHusbandryStatistics2025.pdf",
            "India; WB state yield rows used",
            "raw source",
        ),
        row(
            "PHASE2-EVIDENCE-SQLITE",
            "data/sih26091_phase2.sqlite",
            "derived from registered sources",
            "West Bengal",
            "operational database",
        ),
    ]
    pca_manifest = json.loads((OUTPUT / "CENSUS2011_PCA_West_Bengal_manifest.json").read_text())
    for item in pca_manifest["files"]:
        rows.append(
            row(
                f"CENSUS2011-PCA-TV-19{item['district_sequence_2011']:02d}",
                f"work/raw_stage/CENSUS_2011_PCA_WEST_BENGAL/{item['filename']}",
                item["download_url"],
                f"West Bengal 2011 district sequence {item['district_sequence_2011']:02d}",
                "raw source",
            )
        )
    technical = [
        (
            "HCES2022-TECH",
            "work/raw_stage/HCES_2022_23_TECHNICAL",
            "https://microdata.gov.in/NADA/index.php/catalog/224",
        ),
        (
            "HCES2023-TECH",
            "work/raw_stage/HCES_2023_24_TECHNICAL",
            "https://microdata.gov.in/NADA/index.php/catalog/237",
        ),
        (
            "ASUSE2023-TECH",
            "work/raw_stage/ASUSE_2023_24_TECHNICAL",
            "https://microdata.gov.in/NADA/index.php/catalog/238",
        ),
    ]
    for prefix, directory, source_url in technical:
        for path in sorted((ROOT / directory).iterdir()):
            rows.append(
                row(
                    f"{prefix}-{path.stem}",
                    str(path.relative_to(ROOT)),
                    source_url,
                    "National survey technical material",
                    "raw technical documentation",
                )
            )
    rows.extend(
        [
            row(
                dataset_id="HCES2022-UNIT-DATA",
                path="work/raw_stage/HCES_2022_23_RESTRICTED_MICRODATA/CSV_data_HH_Cons_exp_22_23.zip",
                source_url="https://microdata.gov.in/NADA/index.php/catalog/224",
                coverage="India sample; retained because publisher offers no WB-only archive",
                role="restricted unit microdata; CSV ZIP",
                status="ACQUIRED_RESTRICTED",
                blocker=(
                    "Applicant-only access; raw unit records must not be publicly redistributed"
                ),
            ),
            row(
                "HCES2023-UNIT-DATA",
                "work/raw_stage/HCES_2023_24_RESTRICTED_MICRODATA/HCES_Data_2023-24_Csv.zip",
                "https://microdata.gov.in/NADA/index.php/catalog/237",
                "India sample; retained because publisher offers no WB-only archive",
                "restricted unit microdata; CSV ZIP",
                "ACQUIRED_RESTRICTED",
                "Applicant-only access; raw unit records must not be publicly redistributed",
            ),
            row(
                "ASUSE2023-UNIT-DATA",
                "work/raw_stage/ASUSE_2023_24_RESTRICTED_MICRODATA/ASUSE_DATA_2023_24_CSV.zip",
                "https://microdata.gov.in/NADA/index.php/catalog/238",
                "India sample; retained because publisher offers no WB-only archive",
                "restricted unit microdata; CSV ZIP",
                "ACQUIRED_RESTRICTED",
                "Applicant-only access; raw unit records must not be publicly redistributed",
            ),
            row(
                "HCES2022-WB-MILK-PRIOR",
                "outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS/HCES_2022_23_West_Bengal_liquid_milk_priors.json",
                "derived from HCES2022-UNIT-DATA",
                "West Bengal sampled district-code/sector priors",
                "aggregate model prior",
            ),
            row(
                "HCES2023-WB-MILK-PRIOR",
                "outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS/HCES_2023_24_West_Bengal_liquid_milk_priors.json",
                "derived from HCES2023-UNIT-DATA",
                "West Bengal sampled district-code/sector priors",
                "aggregate model prior",
            ),
            row(
                "ASUSE2023-WB-ENTERPRISE-PRIOR",
                "outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS/ASUSE_2023_24_West_Bengal_enterprise_priors.json",
                "derived from ASUSE2023-UNIT-DATA",
                "West Bengal sampled district-code/sector/NIC2 priors",
                "aggregate model prior",
            ),
        ]
    )
    OUTPUT.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0])
    with (OUTPUT / "PHASE2_DATASET_REGISTRY.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    (OUTPUT / "PHASE2_DATASET_REGISTRY.json").write_text(json.dumps(rows, indent=2) + "\n")
    return rows


if __name__ == "__main__":
    print(json.dumps({"records": len(build())}, indent=2))

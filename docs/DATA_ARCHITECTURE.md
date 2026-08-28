# Data Architecture

Raw publisher files are preserved under `work/raw_stage/`. Derived West Bengal extracts and
manifests are under `outputs/SIH26091_WEST_BENGAL_ALL_DISTRICTS/`. Portable operational stores
are `data/sih26091_phase2.sqlite` and `data/west_bengal_osm.sqlite`.

Core rebuild order:

```sh
.venv/bin/python scripts/extract_wb_livestock.py <national.xlsx> <wb.xlsx> --manifest <json>
.venv/bin/sih26091-ingest-livestock <wb.xlsx> --sqlite data/sih26091_phase2.sqlite --expected-sha256 <sha256>
.venv/bin/python scripts/build_wb_census_crosswalk.py <PC11_TV_DIR.xlsx> <wb.csv> --sqlite data/sih26091_phase2.sqlite --manifest <json>
.venv/bin/python scripts/download_wb_census_pca.py <directory> --manifest <json>
.venv/bin/python scripts/ingest_wb_census_pca.py <directory> <manifest> --sqlite data/sih26091_phase2.sqlite --report <json>
.venv/bin/python scripts/extract_wb_osm.py <west-bengal.pbf> data/west_bengal_osm.sqlite --expected-sha256 <sha256> --manifest <json>
.venv/bin/python scripts/enrich_geographies_osm.py data/sih26091_phase2.sqlite data/west_bengal_osm.sqlite --report <json>
```

Every analysis records evidence dataset versions, OSM source checksum/extractor version, model
versions, timestamp and software commit.


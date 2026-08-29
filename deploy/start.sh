#!/usr/bin/env bash
set -euo pipefail

python deploy/prepare_runtime.py >/dev/null
export SIH26091_SQLITE_PATH="${GRAMARTHA_RUNTIME_DIR:-/tmp/gramartha-runtime}/gramartha.sqlite"
export SIH26091_OSM_SQLITE_PATH="${GRAMARTHA_RUNTIME_DIR:-/tmp/gramartha-runtime}/west_bengal_osm_poi.sqlite"
exec uvicorn backend.api.main:app --host 0.0.0.0 --port "${PORT:-10000}"

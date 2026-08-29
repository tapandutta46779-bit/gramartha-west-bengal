#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="${0:A:h}"
cd "$SCRIPT_DIR"

APP_URL="http://127.0.0.1:8765/ui/"
LOG_FILE="$SCRIPT_DIR/tmp/gramartha-local.log"
mkdir -p "$SCRIPT_DIR/tmp"

if ! curl --silent --fail "http://127.0.0.1:8765/health" >/dev/null 2>&1; then
  if [[ ! -x "$SCRIPT_DIR/.venv/bin/uvicorn" ]]; then
    echo "GramArtha is not installed. Run: python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'"
    read "?Press Return to close."
    exit 1
  fi
  if [[ ! -f "$SCRIPT_DIR/data/sih26091_phase2.sqlite" || ! -f "$SCRIPT_DIR/data/west_bengal_osm.sqlite" ]]; then
    echo "GramArtha's local planning databases are missing from the data folder."
    read "?Press Return to close."
    exit 1
  fi
  SIH26091_SQLITE_PATH="$SCRIPT_DIR/data/sih26091_phase2.sqlite" \
  SIH26091_OSM_SQLITE_PATH="$SCRIPT_DIR/data/west_bengal_osm.sqlite" \
    nohup "$SCRIPT_DIR/.venv/bin/uvicorn" backend.api.main:app \
      --host 127.0.0.1 --port 8765 >"$LOG_FILE" 2>&1 &
  for _ in {1..60}; do
    curl --silent --fail "http://127.0.0.1:8765/health" >/dev/null 2>&1 && break
    sleep 0.25
  done
fi

if curl --silent --fail "http://127.0.0.1:8765/health" >/dev/null 2>&1; then
  if [[ "${GRAMARTHA_NO_OPEN:-0}" != "1" ]]; then
    open "$APP_URL"
  fi
  echo "GramArtha is open. You may close this window; the local service will keep running."
else
  echo "GramArtha did not start. See $LOG_FILE"
fi
read "?Press Return to close."

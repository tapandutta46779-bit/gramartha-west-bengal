#!/bin/zsh
set -euo pipefail

ROOT="${0:A:h}"
cd "$ROOT"

APP_URL="http://127.0.0.1:8765/ui/"
HEALTH_URL="http://127.0.0.1:8765/health"
VENV="$ROOT/.gramartha-venv"
LOG="$ROOT/gramartha-local.log"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3.12+ is required. Install Python, then run this file again."
  read "?Press Return to close."
  exit 1
fi

PY_VERSION="$(python3 - <<'PY'
import sys
print(f"{sys.version_info.major}.{sys.version_info.minor}")
PY
)"
if ! python3 - <<'PY'
import sys
raise SystemExit(0 if sys.version_info >= (3, 12) else 1)
PY
then
  echo "Python 3.12+ is required. Found Python $PY_VERSION."
  read "?Press Return to close."
  exit 1
fi

if [[ ! -x "$VENV/bin/python" ]]; then
  echo "Preparing GramArtha for first launch..."
  python3 -m venv "$VENV"
  "$VENV/bin/python" -m pip install --upgrade pip
  "$VENV/bin/python" -m pip install .
fi

if [[ ! -f "$ROOT/data/sih26091_phase2.sqlite" || ! -f "$ROOT/data/west_bengal_osm.sqlite" ]]; then
  echo "The Judge Package runtime databases are missing. Re-download the release ZIP."
  read "?Press Return to close."
  exit 1
fi

if ! curl --silent --fail "$HEALTH_URL" >/dev/null 2>&1; then
  echo "Starting GramArtha..."
  SIH26091_SQLITE_PATH="$ROOT/data/sih26091_phase2.sqlite" \
  SIH26091_OSM_SQLITE_PATH="$ROOT/data/west_bengal_osm.sqlite" \
    nohup "$VENV/bin/python" -m uvicorn backend.api.main:app \
      --host 127.0.0.1 --port 8765 >"$LOG" 2>&1 &

  for _ in {1..80}; do
    curl --silent --fail "$HEALTH_URL" >/dev/null 2>&1 && break
    sleep 0.25
  done
fi

if curl --silent --fail "$HEALTH_URL" >/dev/null 2>&1; then
  open "$APP_URL"
  echo "GramArtha is running at $APP_URL"
  echo "You can close this window. Log: $LOG"
else
  echo "GramArtha did not start. See: $LOG"
fi

read "?Press Return to close."

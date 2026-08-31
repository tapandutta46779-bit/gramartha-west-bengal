#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

APP_URL="http://127.0.0.1:8765/ui/"
HEALTH_URL="http://127.0.0.1:8765/health"
VENV="$ROOT/.gramartha-venv"
LOG="$ROOT/gramartha-local.log"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3.12+ is required."
  exit 1
fi

python3 - <<'PY'
import sys
if sys.version_info < (3, 12):
    raise SystemExit(f"Python 3.12+ is required; found {sys.version.split()[0]}")
PY

if [[ ! -x "$VENV/bin/python" ]]; then
  echo "Preparing GramArtha for first launch..."
  python3 -m venv "$VENV"
  "$VENV/bin/python" -m pip install --upgrade pip
  "$VENV/bin/python" -m pip install .
fi

if [[ ! -f "$ROOT/data/sih26091_phase2.sqlite" || ! -f "$ROOT/data/west_bengal_osm.sqlite" ]]; then
  echo "The Judge Package runtime databases are missing. Re-download the release ZIP."
  exit 1
fi

if ! curl --silent --fail "$HEALTH_URL" >/dev/null 2>&1; then
  echo "Starting GramArtha..."
  SIH26091_SQLITE_PATH="$ROOT/data/sih26091_phase2.sqlite" \
  SIH26091_OSM_SQLITE_PATH="$ROOT/data/west_bengal_osm.sqlite" \
    nohup "$VENV/bin/python" -m uvicorn backend.api.main:app \
      --host 127.0.0.1 --port 8765 >"$LOG" 2>&1 &

  for _ in $(seq 1 80); do
    curl --silent --fail "$HEALTH_URL" >/dev/null 2>&1 && break
    sleep 0.25
  done
fi

if ! curl --silent --fail "$HEALTH_URL" >/dev/null 2>&1; then
  echo "GramArtha did not start. See: $LOG"
  exit 1
fi

if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$APP_URL" >/dev/null 2>&1 || true
elif command -v gio >/dev/null 2>&1; then
  gio open "$APP_URL" >/dev/null 2>&1 || true
fi

echo "GramArtha is running at $APP_URL"
echo "Log: $LOG"

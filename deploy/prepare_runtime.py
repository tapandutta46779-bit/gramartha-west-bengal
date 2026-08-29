from __future__ import annotations

import gzip
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "deploy" / "assets"
RUNTIME_DIR = Path(os.environ.get("GRAMARTHA_RUNTIME_DIR", "/tmp/gramartha-runtime"))


def unpack(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size > 0:
        return
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    with gzip.open(source, "rb") as compressed, temporary.open("wb") as output:
        shutil.copyfileobj(compressed, output, length=1024 * 1024)
    temporary.replace(destination)


def main() -> None:
    database = RUNTIME_DIR / "gramartha.sqlite"
    osm_database = RUNTIME_DIR / "west_bengal_osm_poi.sqlite"
    unpack(ASSETS / "gramartha_runtime.sqlite.gz", database)
    unpack(ASSETS / "west_bengal_osm_poi.sqlite.gz", osm_database)
    print(f"SIH26091_SQLITE_PATH={database}")
    print(f"SIH26091_OSM_SQLITE_PATH={osm_database}")


if __name__ == "__main__":
    main()

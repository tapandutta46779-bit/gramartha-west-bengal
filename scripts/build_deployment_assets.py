from __future__ import annotations

import gzip
import hashlib
import shutil
import sqlite3
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "deploy" / "assets"


def compress(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as raw, gzip.open(destination, "wb", compresslevel=9) as output:
        shutil.copyfileobj(raw, output, length=1024 * 1024)


def digest(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            checksum.update(chunk)
    return checksum.hexdigest()


def build_application_database(temporary: Path) -> Path:
    source = ROOT / "data" / "sih26091_phase2.sqlite"
    working = temporary / "gramartha_runtime_working.sqlite"
    target = temporary / "gramartha_runtime.sqlite"
    source_connection = sqlite3.connect(source)
    connection = sqlite3.connect(working)
    source_connection.backup(connection)
    source_connection.close()
    connection.execute("DELETE FROM analysis")
    connection.execute("DELETE FROM geographic_identity")
    connection.commit()
    connection.execute(f"VACUUM INTO '{target}'")
    connection.close()
    return target


def build_osm_database(temporary: Path) -> Path:
    source = sqlite3.connect(ROOT / "data" / "west_bengal_osm.sqlite")
    target_path = temporary / "west_bengal_osm_poi.sqlite"
    target = sqlite3.connect(target_path)
    source.backup(target)
    source.close()
    target.executescript(
        """
        DELETE FROM road_way;
        DELETE FROM road_way_rtree;
        DELETE FROM admin_area;
        DELETE FROM admin_area_rtree;
        VACUUM;
        """
    )
    target.close()
    return target_path


def main() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="gramartha-deploy-") as directory:
        temporary = Path(directory)
        artifacts = [build_application_database(temporary), build_osm_database(temporary)]
        for artifact in artifacts:
            destination = ASSET_DIR / f"{artifact.name}.gz"
            compress(artifact, destination)
            print(
                f"{destination.relative_to(ROOT)}\t{destination.stat().st_size}\t"
                f"sha256:{digest(destination)}"
            )


if __name__ == "__main__":
    main()

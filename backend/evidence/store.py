from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from statistics import median

from backend.models.decision import VentureDecision
from backend.models.evidence import EvidenceRecord
from backend.models.geography import CurrentGeoEntity, GeoCrosswalk, GeographicIdentity

from .current_geography import normalize_name
from .districts import CURRENT_WEST_BENGAL_DISTRICTS, canonical_district, current_district


class EvidenceStore:
    def __init__(self, path: str | Path = ":memory:") -> None:
        self.connection = sqlite3.connect(str(path), check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self._defer_commits = False
        self._migrate()

    def _migrate(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS geographic_identity (
                geo_id TEXT PRIMARY KEY,
                state TEXT NOT NULL,
                district TEXT NOT NULL,
                locality TEXT NOT NULL,
                payload TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_geo_search
                ON geographic_identity(state, district, locality);
            CREATE TABLE IF NOT EXISTS evidence_record (
                id TEXT PRIMARY KEY,
                geo_id TEXT NOT NULL,
                variable TEXT NOT NULL,
                source_id TEXT NOT NULL,
                payload TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_evidence_geo ON evidence_record(geo_id);
            CREATE TABLE IF NOT EXISTS regional_prior (
                id TEXT PRIMARY KEY,
                district TEXT NOT NULL,
                sector TEXT NOT NULL,
                variable TEXT NOT NULL,
                payload TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_regional_prior_lookup
                ON regional_prior(district, sector, variable);
            CREATE TABLE IF NOT EXISTS analysis (
                analysis_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                payload TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS current_geo_entity (
                canonical_current_id TEXT PRIMARY KEY,
                canonical_name TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                parent_current_id TEXT,
                district_current_id TEXT NOT NULL,
                current_district TEXT NOT NULL,
                official_code TEXT,
                effective_from TEXT,
                effective_to TEXT,
                source_geo_id TEXT,
                source TEXT NOT NULL,
                payload TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_current_geo_search
                ON current_geo_entity(current_district, canonical_name, entity_type);
            CREATE INDEX IF NOT EXISTS idx_current_geo_source
                ON current_geo_entity(source_geo_id);
            CREATE TABLE IF NOT EXISTS historical_geo_entity (
                source TEXT NOT NULL,
                source_geo_id TEXT PRIMARY KEY,
                source_name TEXT NOT NULL,
                source_parent TEXT,
                source_district TEXT NOT NULL,
                observation_year INTEGER NOT NULL,
                payload TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS geo_crosswalk (
                source TEXT NOT NULL,
                source_geo_id TEXT NOT NULL,
                canonical_current_id TEXT NOT NULL,
                relation TEXT NOT NULL,
                confidence REAL NOT NULL,
                effective_from TEXT,
                effective_to TEXT,
                notes TEXT NOT NULL,
                PRIMARY KEY (source, source_geo_id, canonical_current_id)
            );
            CREATE INDEX IF NOT EXISTS idx_geo_crosswalk_current
                ON geo_crosswalk(canonical_current_id);
            """
        )

    def put_geography(self, item: GeographicIdentity) -> None:
        self.connection.execute(
            "INSERT OR REPLACE INTO geographic_identity VALUES (?, ?, ?, ?, ?)",
            (item.geo_id, item.state, item.district, item.locality, item.model_dump_json()),
        )
        self._commit_unless_deferred()

    def search_geographies(
        self,
        query: str,
        limit: int = 20,
        district: str | None = None,
        locality_type: str | None = None,
    ) -> list[GeographicIdentity]:
        if self._has_current_localities():
            return self._search_current_geographies(query, limit, district, locality_type)
        pattern = f"%{query.casefold()}%"
        if district:
            rows = self.connection.execute(
                """
                SELECT payload FROM geographic_identity
                WHERE lower(locality) LIKE ?
                ORDER BY locality, geo_id
                """,
                (pattern,),
            ).fetchall()
            requested = current_district(district) or district.strip()
            matches = [GeographicIdentity.model_validate_json(row["payload"]) for row in rows]
            return [
                item
                for item in matches
                if (current_district(item.district, source=_source(item.geo_id)) or item.district)
                == requested
                and (not locality_type or item.locality_type == locality_type)
            ][:limit]
        rows = self.connection.execute(
            """
            SELECT payload FROM geographic_identity
            WHERE lower(state) LIKE ? OR lower(district) LIKE ? OR lower(locality) LIKE ?
            ORDER BY district, locality LIMIT ?
            """,
            (pattern, pattern, pattern, limit),
        ).fetchall()
        return [GeographicIdentity.model_validate_json(row["payload"]) for row in rows]

    def list_districts(self) -> list[str]:
        if self._has_current_localities():
            rows = self.connection.execute(
                "SELECT canonical_name FROM current_geo_entity "
                "WHERE entity_type = 'DISTRICT' ORDER BY canonical_name"
            ).fetchall()
            return [row["canonical_name"] for row in rows]
        present = {
            current
            for row in self.connection.execute(
                "SELECT DISTINCT district FROM geographic_identity WHERE state = 'West Bengal'"
            ).fetchall()
            if (current := current_district(row["district"], source="DS057"))
        }
        return [name for name in CURRENT_WEST_BENGAL_DISTRICTS if name in present]

    def get_geography(self, geo_id: str) -> GeographicIdentity | None:
        current = self.connection.execute(
            "SELECT payload FROM current_geo_entity WHERE source_geo_id = ? "
            "AND payload IS NOT NULL LIMIT 1",
            (geo_id,),
        ).fetchone()
        if current:
            return GeographicIdentity.model_validate_json(current["payload"])
        row = self.connection.execute(
            "SELECT payload FROM geographic_identity WHERE geo_id = ?", (geo_id,)
        ).fetchone()
        return GeographicIdentity.model_validate_json(row["payload"]) if row else None

    def get_current_entity(self, canonical_current_id: str) -> CurrentGeoEntity | None:
        row = self.connection.execute(
            "SELECT * FROM current_geo_entity WHERE canonical_current_id = ?",
            (canonical_current_id,),
        ).fetchone()
        if row is None:
            return None
        payload = GeographicIdentity.model_validate_json(row["payload"]) if row["payload"] else None
        return CurrentGeoEntity(
            canonical_current_id=row["canonical_current_id"],
            canonical_name=row["canonical_name"],
            entity_type=row["entity_type"],
            parent_current_id=row["parent_current_id"],
            district_current_id=row["district_current_id"],
            current_district=row["current_district"],
            official_code=row["official_code"],
            effective_from=row["effective_from"],
            effective_to=row["effective_to"],
            source_geo_id=row["source_geo_id"],
            source=row["source"],
            payload=payload,
        )

    def get_crosswalks(self, source_geo_id: str) -> list[GeoCrosswalk]:
        rows = self.connection.execute(
            """
            SELECT DISTINCT x.* FROM geo_crosswalk x
            LEFT JOIN current_geo_entity c
              ON c.canonical_current_id = x.canonical_current_id
            WHERE x.source_geo_id = ?
               OR x.canonical_current_id = ?
               OR c.source_geo_id = ?
            ORDER BY x.confidence DESC
            """,
            (source_geo_id, source_geo_id, source_geo_id),
        ).fetchall()
        return [
            GeoCrosswalk(
                source=row["source"],
                source_geo_id=row["source_geo_id"],
                canonical_current_id=row["canonical_current_id"],
                relation=row["relation"],
                confidence=row["confidence"],
                effective_from=row["effective_from"],
                effective_to=row["effective_to"],
                notes=row["notes"],
            )
            for row in rows
        ]

    def all_geographies(self) -> list[GeographicIdentity]:
        if self._has_current_localities():
            rows = self.connection.execute(
                "SELECT payload FROM current_geo_entity WHERE payload IS NOT NULL "
                "ORDER BY current_district, canonical_name, canonical_current_id"
            ).fetchall()
            return [GeographicIdentity.model_validate_json(row["payload"]) for row in rows]
        rows = self.connection.execute(
            "SELECT payload FROM geographic_identity ORDER BY district, locality, geo_id"
        ).fetchall()
        return [GeographicIdentity.model_validate_json(row["payload"]) for row in rows]

    def put_evidence(self, record: EvidenceRecord) -> None:
        self.connection.execute(
            "INSERT OR REPLACE INTO evidence_record VALUES (?, ?, ?, ?, ?)",
            (record.id, record.geo_id, record.variable, record.source_id, record.model_dump_json()),
        )
        self._commit_unless_deferred()

    def get_evidence(self, geo_id: str) -> list[EvidenceRecord]:
        # Current product localities frequently carry a DS057 identity while the
        # structural observation remains keyed to its Census-2011 identity.  An
        # explicit high-confidence crosswalk may link those records; retrieving
        # them here preserves their 2011 observation date instead of pretending
        # that the historical measurement is current.
        rows = self.connection.execute(
            """
            WITH current_ids AS (
                SELECT canonical_current_id FROM current_geo_entity
                WHERE source_geo_id = ? OR canonical_current_id = ?
            ), linked_geo_ids AS (
                SELECT ? AS geo_id
                UNION
                SELECT source_geo_id FROM geo_crosswalk
                WHERE canonical_current_id IN current_ids
                  AND confidence >= 0.90
                  AND relation = 'EXACT_NAME_AND_COMPATIBLE_CURRENT_HIERARCHY'
            )
            SELECT payload FROM evidence_record
            WHERE geo_id IN linked_geo_ids
            ORDER BY variable, id
            """,
            (geo_id, geo_id, geo_id),
        ).fetchall()
        return [EvidenceRecord.model_validate_json(row["payload"]) for row in rows]

    def get_locality_spatial_proxy(self, item: GeographicIdentity) -> dict | None:
        """Return a bounded parent-area proxy without altering canonical geography.

        Exact coordinates always belong on the identity itself.  For an unresolved
        ward/village, two or more coordinate-linked siblings in the same block or
        municipality can provide a planning proxy.  A wide sibling cloud is rejected
        because it is not precise enough for local competitor discovery.
        """
        parent_field = "municipality" if item.municipality else "block"
        parent_value = item.municipality or item.block
        if not parent_value:
            return None
        rows = self.connection.execute(
            "SELECT payload FROM current_geo_entity "
            "WHERE current_district = ? AND payload IS NOT NULL",
            (item.district,),
        ).fetchall()
        coordinates: list[tuple[float, float]] = []
        for row in rows:
            sibling = GeographicIdentity.model_validate_json(row["payload"])
            if getattr(sibling, parent_field) != parent_value:
                continue
            if sibling.latitude is None or sibling.longitude is None:
                continue
            coordinates.append((float(sibling.latitude), float(sibling.longitude)))
        if len(coordinates) < 2:
            return None
        latitude = median(value[0] for value in coordinates)
        longitude = median(value[1] for value in coordinates)
        # About 22 km latitude/longitude at West Bengal latitudes.  Wider parent
        # clouds are unsuitable for a hyper-local competitor scan.
        if any(
            abs(lat - latitude) > 0.20 or abs(lon - longitude) > 0.22 for lat, lon in coordinates
        ):
            return None
        return {
            "latitude": latitude,
            "longitude": longitude,
            "coordinate_quality": f"{parent_field.upper()}_SIBLING_MEDIAN_PROXY",
            "coordinate_reference_count": len(coordinates),
            "coordinate_parent": parent_value,
            "source_url": "https://www.openstreetmap.org/copyright",
        }

    def put_regional_prior(self, record: EvidenceRecord, *, district: str, sector: str) -> None:
        self.connection.execute(
            "INSERT OR REPLACE INTO regional_prior VALUES (?, ?, ?, ?, ?)",
            (record.id, district, sector, record.variable, record.model_dump_json()),
        )
        self._commit_unless_deferred()

    def get_regional_priors(self, district: str, sector: str) -> list[EvidenceRecord]:
        canonical = canonical_district(district)
        if canonical is None:
            return []
        rows = self.connection.execute(
            "SELECT payload FROM regional_prior WHERE district = ? AND sector = ? "
            "ORDER BY variable, id",
            (canonical, sector),
        ).fetchall()
        return [EvidenceRecord.model_validate_json(row["payload"]) for row in rows]

    def put_analysis(self, decision: VentureDecision) -> None:
        self.connection.execute(
            "INSERT OR REPLACE INTO analysis VALUES (?, ?, ?)",
            (decision.analysis_id, decision.created_at.isoformat(), decision.model_dump_json()),
        )
        self._commit_unless_deferred()

    def get_analysis(self, analysis_id: str) -> VentureDecision | None:
        row = self.connection.execute(
            "SELECT payload FROM analysis WHERE analysis_id = ?", (analysis_id,)
        ).fetchone()
        return VentureDecision.model_validate_json(row["payload"]) if row else None

    def export_json(self) -> str:
        counts = {}
        for table in ("geographic_identity", "evidence_record", "regional_prior", "analysis"):
            counts[table] = self.connection.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        return json.dumps(counts, sort_keys=True)

    def _commit_unless_deferred(self) -> None:
        if not self._defer_commits:
            self.connection.commit()

    @contextmanager
    def transaction(self) -> Iterator[None]:
        previous = self._defer_commits
        self._defer_commits = True
        try:
            yield
            if not previous:
                self.connection.commit()
        except Exception:
            if not previous:
                self.connection.rollback()
            raise
        finally:
            self._defer_commits = previous

    def _has_current_localities(self) -> bool:
        return bool(
            self.connection.execute(
                "SELECT 1 FROM current_geo_entity WHERE payload IS NOT NULL LIMIT 1"
            ).fetchone()
        )

    def _search_current_geographies(
        self,
        query: str,
        limit: int,
        district: str | None,
        locality_type: str | None,
    ) -> list[GeographicIdentity]:
        requested = current_district(district) if district else None
        if district and requested is None:
            return []
        clauses = ["payload IS NOT NULL"]
        values: list[str] = []
        if requested:
            clauses.append("current_district = ?")
            values.append(requested)
        if locality_type:
            clauses.append("entity_type = ?")
            values.append(locality_type)
        rows = self.connection.execute(
            f"SELECT canonical_name, entity_type, payload FROM current_geo_entity "
            f"WHERE {' AND '.join(clauses)}",
            values,
        ).fetchall()
        target = normalize_name(query)
        ranked = []
        for row in rows:
            item = GeographicIdentity.model_validate_json(row["payload"])
            names = [item.locality, *item.aliases]
            scores = [
                _search_score(target, normalize_name(name), index > 0)
                for index, name in enumerate(names)
            ]
            score = min(scores, default=99)
            if score[0] >= 9:
                continue
            ranked.append((score, normalize_name(item.locality), item.geo_id, item))
        ranked.sort(key=lambda value: value[:3])
        return [value[3] for value in ranked[:limit]]


def _source(geo_id: str) -> str:
    return geo_id.split(":", 1)[0]


def _search_score(target: str, candidate: str, alias: bool) -> tuple[int, int]:
    if not target:
        return (9, len(candidate))
    if candidate == target:
        return (1 if alias else 0, 0)
    if candidate.startswith(target):
        return (2, len(candidate) - len(target))
    tokens = candidate.split()
    if target in tokens or all(part in tokens for part in target.split()):
        return (3, len(candidate))
    if target in candidate:
        return (4, candidate.index(target))
    return (9, len(candidate))

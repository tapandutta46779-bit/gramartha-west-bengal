from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from backend.models.decision import VentureDecision
from backend.models.evidence import EvidenceRecord
from backend.models.geography import GeographicIdentity

from .districts import canonical_district


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
            """
        )

    def put_geography(self, item: GeographicIdentity) -> None:
        self.connection.execute(
            "INSERT OR REPLACE INTO geographic_identity VALUES (?, ?, ?, ?, ?)",
            (item.geo_id, item.state, item.district, item.locality, item.model_dump_json()),
        )
        self._commit_unless_deferred()

    def search_geographies(
        self, query: str, limit: int = 20, district: str | None = None
    ) -> list[GeographicIdentity]:
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
            requested = _district_search_key(district)
            matches = [GeographicIdentity.model_validate_json(row["payload"]) for row in rows]
            return [
                item
                for item in matches
                if _district_search_key(item.district).casefold() == requested.casefold()
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
        rows = self.connection.execute(
            "SELECT DISTINCT district FROM geographic_identity WHERE state = 'West Bengal'"
        ).fetchall()
        return sorted(
            {_district_search_key(row["district"]) for row in rows},
            key=str.casefold,
        )

    def get_geography(self, geo_id: str) -> GeographicIdentity | None:
        row = self.connection.execute(
            "SELECT payload FROM geographic_identity WHERE geo_id = ?", (geo_id,)
        ).fetchone()
        return GeographicIdentity.model_validate_json(row["payload"]) if row else None

    def all_geographies(self) -> list[GeographicIdentity]:
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
        rows = self.connection.execute(
            "SELECT payload FROM evidence_record WHERE geo_id = ? ORDER BY variable, id", (geo_id,)
        ).fetchall()
        return [EvidenceRecord.model_validate_json(row["payload"]) for row in rows]

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


def _district_search_key(value: str) -> str:
    if value.casefold().strip() in {"barddhaman", "bardhaman"}:
        return "Barddhaman"
    return canonical_district(value) or value.strip()

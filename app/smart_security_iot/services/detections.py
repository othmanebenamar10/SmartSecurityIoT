from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from smart_security_iot.database.db import Database


@dataclass(frozen=True)
class DetectionEvent:
    type: str  # authorized | unknown
    user_id: int | None
    confidence: float
    capture_path: str | None
    risk_level: str
    details: dict


class DetectionStore:
    def __init__(self, db: Database) -> None:
        self._db = db

    def add(self, e: DetectionEvent) -> None:
        self._db.execute(
            """
            INSERT INTO detections (type, user_id, confidence, capture_path, risk_level, details)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                e.type,
                e.user_id,
                float(e.confidence),
                e.capture_path,
                e.risk_level,
                json.dumps(e.details, ensure_ascii=True),
            ),
        )

    def list_all(self, limit: int = 100) -> list[dict]:
        rows = self._db.query_all(
            """
            SELECT d.*, u.first_name || ' ' || u.last_name AS user
            FROM detections d
            LEFT JOIN users u ON u.id = d.user_id
            ORDER BY d.created_at DESC
            LIMIT ?
            """,
            (limit,),
        )
        return [dict(r) for r in rows]

    def count_by_type(self, dtype: str) -> int:
        row = self._db.query_one("SELECT COUNT(*) AS cnt FROM detections WHERE type = ?", (dtype,))
        return int(row["cnt"]) if row else 0

    def count_since(self, minutes: int = 60) -> int:
        row = self._db.query_one(
            "SELECT COUNT(*) AS cnt FROM detections WHERE created_at >= datetime('now', ?)",
            (f"-{minutes} minutes",),
        )
        return int(row["cnt"]) if row else 0

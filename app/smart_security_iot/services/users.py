from __future__ import annotations

import pickle
from dataclasses import dataclass
from typing import Optional

import numpy as np

from smart_security_iot.database.db import Database


@dataclass(frozen=True)
class UserRow:
    id: int
    first_name: str
    last_name: str
    role: str
    face_encoding: Optional[np.ndarray]
    face_image_path: str | None

    @property
    def label(self) -> str:
        return f"{self.last_name} {self.first_name}".strip()


class UserStore:
    def __init__(self, db: Database) -> None:
        self._db = db

    def list_users(self) -> list[UserRow]:
        rows = self._db.query_all(
            "SELECT id, first_name, last_name, role, face_encoding, face_image_path FROM users ORDER BY last_name, first_name"
        )
        out: list[UserRow] = []
        for r in rows:
            enc = None
            blob = r["face_encoding"]
            if blob is not None:
                try:
                    enc = pickle.loads(blob)
                except Exception:
                    enc = None
            out.append(
                UserRow(
                    id=int(r["id"]),
                    first_name=str(r["first_name"]),
                    last_name=str(r["last_name"]),
                    role=str(r["role"]),
                    face_encoding=enc,
                    face_image_path=str(r["face_image_path"]) if r["face_image_path"] is not None else None,
                )
            )
        return out

    def upsert_face(self, user_id: int, encoding: Optional[np.ndarray], image_path: str | None) -> None:
        blob = None
        if encoding is not None:
            blob = pickle.dumps(encoding.astype(np.float32), protocol=pickle.HIGHEST_PROTOCOL)
        with self._db.connect() as conn:
            cur = conn.execute(
                "UPDATE users SET face_encoding = ?, face_image_path = ? WHERE id = ?",
                (blob, image_path, user_id),
            )
            if cur.rowcount == 0:
                raise RuntimeError(f"User id not found: {user_id}")

    def create_user(self, first_name: str, last_name: str, role: str = "user") -> int:
        with self._db.connect() as conn:
            cur = conn.execute(
                "INSERT INTO users (first_name, last_name, role) VALUES (?, ?, ?)",
                (first_name.strip(), last_name.strip(), role),
            )
            return int(cur.lastrowid or 0)

    def delete_user(self, user_id: int) -> bool:
        with self._db.connect() as conn:
            cur = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            return cur.rowcount > 0

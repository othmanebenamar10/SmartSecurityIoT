from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class DbPaths:
    path: Path


class Database:
    def __init__(self, path: Path) -> None:
        self._paths = DbPaths(path=path)

    @property
    def path(self) -> Path:
        return self._paths.path

    def connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.path), isolation_level=None)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn

    def migrate(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user',
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    face_encoding BLOB NULL,
                    face_image_path TEXT NULL
                );

                CREATE TABLE IF NOT EXISTS detections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    type TEXT NOT NULL, -- authorized | unknown
                    user_id INTEGER NULL,
                    confidence REAL NOT NULL,
                    capture_path TEXT NULL,
                    risk_level TEXT NOT NULL,
                    details TEXT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS security_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    level TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    meta_json TEXT NULL
                );

                CREATE TABLE IF NOT EXISTS auth_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash BLOB NOT NULL,
                    role TEXT NOT NULL DEFAULT 'admin',
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS auth_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    username TEXT NOT NULL,
                    success INTEGER NOT NULL,
                    ip TEXT NULL
                );
                """
            )

    def execute(self, sql: str, params: Iterable[Any] = ()) -> None:
        with self.connect() as conn:
            conn.execute(sql, tuple(params))

    def query_one(self, sql: str, params: Iterable[Any] = ()) -> sqlite3.Row | None:
        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(sql, tuple(params))
            return cur.fetchone()

    def query_all(self, sql: str, params: Iterable[Any] = ()) -> list[sqlite3.Row]:
        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(sql, tuple(params))
            return cur.fetchall()

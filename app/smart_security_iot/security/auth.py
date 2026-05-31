from __future__ import annotations

import logging
import time

import bcrypt

from smart_security_iot.core.config import AppConfig
from smart_security_iot.database.db import Database


class AuthError(Exception):
    pass


class Session:
    def __init__(self, user_id: int, role: str, timeout_min: int = 20) -> None:
        self.user_id = user_id
        self.role = role
        self._start = time.time()
        self._timeout = timeout_min * 60

    @property
    def expired(self) -> bool:
        return time.time() - self._start > self._timeout

    @property
    def elapsed(self) -> float:
        return time.time() - self._start

    @property
    def remaining(self) -> float:
        return max(0.0, self._timeout - self.elapsed)

    def refresh(self) -> None:
        self._start = time.time()


class AuthService:
    def __init__(self, db: Database, config: AppConfig, logger: logging.Logger) -> None:
        self._db = db
        self._config = config
        self._logger = logger
        self._lockouts: dict[str, float] = {}
        self._session: Session | None = None

    def bootstrap_admin(self) -> None:
        row = self._db.query_one("SELECT id FROM auth_users WHERE username = ?", (self._config.admin_username,))
        if row is not None:
            return
        pw_hash = bcrypt.hashpw(self._config.admin_password.encode("utf-8"), bcrypt.gensalt(rounds=12))
        self._db.execute(
            "INSERT INTO auth_users (username, password_hash, role) VALUES (?, ?, ?)",
            (self._config.admin_username, pw_hash, "admin"),
        )
        self._logger.info("Bootstrapped admin user '%s'", self._config.admin_username)

    def _is_locked(self, username: str) -> bool:
        until = self._lockouts.get(username)
        if until is None:
            return False
        if time.time() >= until:
            self._lockouts.pop(username, None)
            return False
        return True

    def _register_attempt(self, username: str, success: bool) -> None:
        self._db.execute(
            "INSERT INTO auth_attempts (username, success) VALUES (?, ?)",
            (username, 1 if success else 0),
        )

    def _recent_failures(self, username: str) -> int:
        rows = self._db.query_all(
            """
            SELECT success FROM auth_attempts
            WHERE username = ?
              AND created_at >= datetime('now', ?)
            ORDER BY id DESC
            """,
            (username, f"-{self._config.lockout_min} minutes"),
        )
        return sum(1 for r in rows if int(r["success"]) == 0)

    def login(self, username: str, password: str) -> tuple[int, str]:
        username = (username or "").strip()
        if not username:
            raise AuthError("Identifiant vide")
        if self._is_locked(username):
            raise AuthError("Compte verrouille temporairement")

        row = self._db.query_one("SELECT id, password_hash, role FROM auth_users WHERE username = ?", (username,))
        if row is None:
            self._register_attempt(username, False)
            raise AuthError("Identifiants invalides")

        ok = bcrypt.checkpw(password.encode("utf-8"), row["password_hash"])
        self._register_attempt(username, ok)
        if not ok:
            failures = self._recent_failures(username)
            if failures >= self._config.max_login_attempts:
                self._lockouts[username] = time.time() + (self._config.lockout_min * 60)
                self._logger.warning("Lockout triggered for '%s'", username)
            raise AuthError("Identifiants invalides")

        self._session = Session(user_id=int(row["id"]), role=str(row["role"]), timeout_min=self._config.session_timeout_min)
        return int(row["id"]), str(row["role"])

    @property
    def session(self) -> Session | None:
        if self._session is not None and self._session.expired:
            self._session = None
        return self._session

    def clear_session(self) -> None:
        self._session = None

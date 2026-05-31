from __future__ import annotations

import logging
import threading
import time
from collections import deque
from typing import Callable


class Watchdog:
    def __init__(self, logger: logging.Logger, interval_s: float = 5.0) -> None:
        self._logger = logger
        self._interval = interval_s
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._checks: list[tuple[str, Callable[[], bool], Callable[[], object] | None]] = []

    def register(self, name: str, check_fn: Callable[[], bool], recover_fn: Callable[[], object] | None = None) -> None:
        self._checks.append((name, check_fn, recover_fn))

    @property
    def has_checks(self) -> bool:
        return bool(self._checks)

    def start(self) -> None:
        if self._thread is not None or not self._checks:
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name="watchdog")
        self._thread.start()
        self._logger.info("Watchdog started (interval=%ss)", self._interval)

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=3)
            self._thread = None

    def _run(self) -> None:
        while not self._stop.is_set():
            for name, check_fn, recover_fn in self._checks:
                if self._stop.is_set():
                    break
                try:
                    ok = check_fn()
                    if not ok:
                        self._logger.warning("Watchdog: %s unhealthy", name)
                        if recover_fn:
                            self._logger.info("Watchdog: recovering %s", name)
                            recover_fn()
                except Exception as ex:
                    self._logger.error("Watchdog check %s failed: %s", name, ex)
            self._stop.wait(self._interval)


class HealthMonitor:
    def __init__(self, logger: logging.Logger, max_samples: int = 60) -> None:
        self._logger = logger
        self._samples: deque[dict] = deque(maxlen=max_samples)

    def record(self, data: dict) -> None:
        data["_ts"] = time.time()
        self._samples.append(data)

    def health_status(self) -> dict:
        if not self._samples:
            return {"status": "unknown", "uptime": 0, "fps": 0}
        recent = [s for s in self._samples if time.time() - s.get("_ts", 0) < 10]
        return {
            "status": "healthy" if len(recent) > 0 else "stalled",
            "uptime": time.time() - self._samples[0].get("_ts", time.time()),
            "fps": len(recent),
        }

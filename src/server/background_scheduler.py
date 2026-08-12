"""Background scheduler service for agent-server housekeeping.

``_AgentSession`` owns user/model turns, but session housekeeping has its own
clock: finished background-task notifications and scheduled prompts must be
checked even while the foreground worker is parked waiting for user input.
This module keeps that clock small, deterministic, and independently
unit-testable.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field
from typing import Callable

logger = logging.getLogger(__name__)


@dataclass
class SessionBackgroundScheduler:
    """Run session housekeeping ticks on an independent daemon thread.

    The service intentionally knows nothing about cron internals or task
    notification queues. The owning session supplies a single ``tick_fn`` that
    performs one best-effort housekeeping pass. ``tick`` is also public so tests
    can cover behavior without waiting for wall-clock time.
    """

    tick_fn: Callable[[], None]
    interval_s: float = 0.5
    name: str = "agent-server-background-scheduler"
    _stop: threading.Event = field(default_factory=threading.Event, init=False)
    _tick_lock: threading.Lock = field(default_factory=threading.Lock, init=False)
    _thread: threading.Thread | None = field(default=None, init=False)

    def start(self) -> None:
        """Start the daemon loop once; repeated calls are harmless."""
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._run,
            name=self.name,
            daemon=True,
        )
        self._thread.start()

    def stop(self, timeout: float = 2.0) -> None:
        """Request shutdown and join briefly."""
        self._stop.set()
        thread = self._thread
        if thread is not None and thread.is_alive():
            thread.join(timeout=timeout)

    def tick(self) -> bool:
        """Run one housekeeping pass if no previous tick is still running.

        Returns ``True`` when the supplied tick function ran. A slow tick is
        skipped rather than overlapped, which keeps scheduled turns and
        notification delivery single-threaded at the service boundary.
        """
        if not self._tick_lock.acquire(blocking=False):
            return False
        try:
            self.tick_fn()
            return True
        except Exception:  # noqa: BLE001 — background housekeeping is best-effort
            logger.debug("[agent-server] background scheduler tick failed", exc_info=True)
            return False
        finally:
            self._tick_lock.release()

    def _run(self) -> None:
        while not self._stop.wait(self.interval_s):
            self.tick()

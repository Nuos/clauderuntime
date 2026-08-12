"""Phase B — Loop Governance: ``B2. Scheduler decouple`` coverage."""

from __future__ import annotations

import threading
import unittest
from unittest.mock import MagicMock

from src.server.agent_server import AgentServerConfig, _AgentSession
from src.server.background_scheduler import SessionBackgroundScheduler


class TestSessionBackgroundScheduler(unittest.TestCase):
    def test_tick_runs_once_and_skips_overlap(self) -> None:
        started = threading.Event()
        release = threading.Event()
        calls: list[str] = []

        def slow_tick() -> None:
            calls.append("tick")
            started.set()
            self.assertTrue(release.wait(timeout=1.0))

        service = SessionBackgroundScheduler(slow_tick, interval_s=60.0)
        worker = threading.Thread(target=service.tick)
        worker.start()
        self.assertTrue(started.wait(timeout=1.0))

        self.assertFalse(service.tick())

        release.set()
        worker.join(timeout=1.0)
        self.assertFalse(worker.is_alive())
        self.assertEqual(calls, ["tick"])

    def test_background_thread_ticks_while_foreground_is_waiting(self) -> None:
        ticked = threading.Event()
        foreground_release = threading.Event()

        def tick() -> None:
            ticked.set()

        service = SessionBackgroundScheduler(tick, interval_s=0.001)
        foreground = threading.Thread(
            target=lambda: foreground_release.wait(timeout=1.0)
        )
        foreground.start()
        service.start()
        try:
            self.assertTrue(ticked.wait(timeout=1.0))
            self.assertTrue(foreground.is_alive())
        finally:
            foreground_release.set()
            foreground.join(timeout=1.0)
            service.stop(timeout=1.0)


class TestAgentSessionBackgroundTick(unittest.TestCase):
    def _session(self) -> _AgentSession:
        return _AgentSession(
            session_id="scheduler-sess",
            cwd="/tmp",
            config=AgentServerConfig(single_session=False),
            loop=MagicMock(),
            out_queue=MagicMock(),
        )

    def test_tick_runs_housekeeping_when_turn_gate_is_free(self) -> None:
        sess = self._session()
        calls: list[str] = []
        sess._deliver_task_notifications = (  # type: ignore[method-assign]
            lambda: calls.append("deliver") or False
        )
        sess._fire_due_scheduled = lambda: calls.append("fire") or False  # type: ignore[method-assign]
        sess._push_cron_state = lambda message="": calls.append("push")  # type: ignore[method-assign]

        sess._background_scheduler_tick()

        self.assertEqual(calls, ["deliver", "fire"])

    def test_tick_does_not_interleave_with_active_turn(self) -> None:
        sess = self._session()
        calls: list[str] = []
        sess._deliver_task_notifications = (  # type: ignore[method-assign]
            lambda: calls.append("deliver") or False
        )
        sess._fire_due_scheduled = lambda: calls.append("fire") or False  # type: ignore[method-assign]
        sess._push_cron_state = lambda message="": calls.append("push")  # type: ignore[method-assign]

        gate_acquired = threading.Event()
        release_gate = threading.Event()
        holder = threading.Thread(
            target=self._hold_turn_gate,
            args=(sess, gate_acquired, release_gate),
        )
        holder.start()
        self.assertTrue(gate_acquired.wait(timeout=1.0))
        try:
            sess._background_scheduler_tick()
        finally:
            release_gate.set()
            holder.join(timeout=1.0)

        self.assertEqual(calls, ["push"])
        self.assertFalse(holder.is_alive())

    @staticmethod
    def _hold_turn_gate(
        sess: _AgentSession,
        gate_acquired: threading.Event,
        release_gate: threading.Event,
    ) -> None:
        sess._turn_gate.acquire()
        try:
            gate_acquired.set()
            release_gate.wait(timeout=1.0)
        finally:
            sess._turn_gate.release()


if __name__ == "__main__":
    unittest.main()

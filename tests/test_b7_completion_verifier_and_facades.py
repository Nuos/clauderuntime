"""B7 W6 — completion verifier + server session facades tests."""

from __future__ import annotations

import asyncio
import unittest
from types import SimpleNamespace

from src.runtime.completion_verifier import (
    CompletionStatus,
    StructuralCompletionVerifier,
)
from src.runtime.server_session_facades import (
    PermissionBridge,
    SchedulerBridge,
    ServerSessionFacades,
    SessionState,
    SurfaceEmitter,
)


class TestCompletionVerifier(unittest.TestCase):
    def setUp(self) -> None:
        self.verifier = StructuralCompletionVerifier()

    def test_terminal_completed_with_evidence_passes(self) -> None:
        trace = SimpleNamespace(terminal_status="completed")
        decision = self.verifier.verify("contract", trace, ["/tmp/evidence.json"])
        self.assertEqual(decision.status, CompletionStatus.PASS)
        self.assertIn("/tmp/evidence.json", decision.evidence_refs)

    def test_no_terminal_status_indeterminate(self) -> None:
        decision = self.verifier.verify("contract", SimpleNamespace(status="running"), [])
        self.assertEqual(decision.status, CompletionStatus.INDETERMINATE)

    def test_failed_terminal_fails(self) -> None:
        trace = SimpleNamespace(terminal_status="failed")
        decision = self.verifier.verify("contract", trace, ["/tmp/e.json"])
        self.assertEqual(decision.status, CompletionStatus.FAIL)

    def test_missing_evidence_indeterminate_even_if_terminal(self) -> None:
        trace = SimpleNamespace(terminal_status="completed")
        decision = self.verifier.verify("contract", trace, [])
        self.assertEqual(decision.status, CompletionStatus.INDETERMINATE)
        self.assertTrue(any("no evidence" in r for r in decision.reasons))


class TestServerFacades(unittest.TestCase):
    def test_facade_dataclasses_hold_references(self) -> None:
        emitted: list[dict] = []
        scheduler = object()
        facades = ServerSessionFacades(
            permission_bridge=PermissionBridge(ask_handler=lambda r: None, pending_requests={"p1": 1}),
            surface_emitter=SurfaceEmitter(emit=emitted.append),
            scheduler_bridge=SchedulerBridge(scheduler=scheduler),
            session_state=SessionState(
                app_state=object(),
                messages=lambda: ["m1"],
                stats={"turns": 3},
            ),
        )
        facades.surface_emitter.push({"type": "x"})
        self.assertEqual(emitted, [{"type": "x"}])
        self.assertIs(facades.scheduler_bridge.scheduler, scheduler)
        self.assertEqual(facades.session_state.message_list(), ["m1"])
        self.assertEqual(facades.permission_bridge.pending_requests["p1"], 1)

    def test_agent_session_exposes_facades(self) -> None:
        from src.server.agent_server import AgentServerConfig, _AgentSession

        loop = asyncio.new_event_loop()
        try:
            session = _AgentSession(
                session_id="s1",
                cwd="/tmp",
                config=AgentServerConfig(),
                loop=loop,
                out_queue=asyncio.Queue(),
            )
            facades = session.facades()
            self.assertIsInstance(facades, ServerSessionFacades)
            # facades reference the LIVE session objects (no copied state)
            self.assertIs(facades.surface_emitter.emit.__func__, session._emit.__func__)
            self.assertIs(facades.surface_emitter.emit.__self__, session)
            self.assertIs(facades.scheduler_bridge.scheduler, session.cron_scheduler)
            self.assertEqual(facades.session_state.stats["turns"], session._stats_turns)
            # lazy: same instance on second access
            self.assertIs(facades, session.facades())
        finally:
            loop.close()


if __name__ == "__main__":
    unittest.main()

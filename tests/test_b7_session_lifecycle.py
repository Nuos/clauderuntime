"""B7 W4 — session lifecycle (durable-only resume contract) tests.

State / Resume Law (Behavior Bible §I): resume restores durable semantics
only — never temporary permission, trust verdicts, API keys, live MCP
sessions, threads/handles or abort controllers. These tests pin the
SessionLifecycle owner's boundary enforcement.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from src.runtime.session_lifecycle import SessionLifecycle, SessionPhase
from src.task_registry import RuntimeTaskRegistry


class TestLifecyclePhases(unittest.TestCase):
    def test_start_then_end(self) -> None:
        lc = SessionLifecycle()
        record = lc.start("s1", durable_refs=("transcript.json",))
        self.assertEqual(record.phase, SessionPhase.STARTED)
        ended = lc.end("s1")
        self.assertEqual(ended.phase, SessionPhase.ENDED)

    def test_end_unknown_returns_none(self) -> None:
        lc = SessionLifecycle()
        self.assertIsNone(lc.end("nope"))

    def test_fork_and_rewind_record_phases(self) -> None:
        lc = SessionLifecycle()
        self.assertEqual(lc.fork("s2").phase, SessionPhase.FORKED)
        self.assertEqual(lc.rewind("s2").phase, SessionPhase.REWOUND)


class TestDurableMetadataGate(unittest.TestCase):
    def test_ephemeral_keys_rejected(self) -> None:
        lc = SessionLifecycle()
        metadata = SimpleNamespace(
            agent_id="a1",
            api_key="sk-secret",
            permission_mode="bypassPermissions",
            mcp_clients={"srv": object()},
            thread_id="t1",
        )
        violations = lc.validate_durable_metadata(metadata)
        self.assertTrue(any("api_key" in v for v in violations))
        self.assertTrue(any("permission_mode" in v for v in violations))
        self.assertTrue(any("mcp_clients" in v for v in violations))
        self.assertTrue(any("thread_id" in v for v in violations))

    def test_durable_only_metadata_accepted(self) -> None:
        lc = SessionLifecycle()
        metadata = SimpleNamespace(
            agent_id="a1",
            agent_type="local_agent",
            description="probe",
            initial_prompt="hi",
            model="test-model",
            output_file="/tmp/x.jsonl",
            status="failed",
        )
        self.assertEqual(lc.validate_durable_metadata(metadata), [])

    def test_null_metadata_accepted(self) -> None:
        self.assertEqual(SessionLifecycle().validate_durable_metadata(None), [])


class TestResumeBoundary(unittest.TestCase):
    def test_resume_with_live_handle_raises(self) -> None:
        lc = SessionLifecycle()
        fake_state = SimpleNamespace(id="a1", proc=object(), handle=None)
        with self.assertRaises(RuntimeError):
            lc._assert_no_ephemeral_state(fake_state)

    def test_resume_without_durable_returns_none(self) -> None:
        # No resume metadata on disk → nothing durable to restore.
        lc = SessionLifecycle()
        with tempfile.TemporaryDirectory() as tmp:
            registry = RuntimeTaskRegistry()
            # agent_id points at a transcript that does not exist
            state = lc.resume("no-such-agent", registry)
            self.assertIsNone(state)

    def test_resume_records_phase(self) -> None:
        lc = SessionLifecycle()
        with tempfile.TemporaryDirectory() as tmp:
            registry = RuntimeTaskRegistry()
            lc.resume("no-such-agent", registry)
            self.assertNotIn("no-such-agent", lc.records)


if __name__ == "__main__":
    unittest.main()

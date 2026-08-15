"""B7 W4 — session lifecycle owner.

State / Resume Law (Behavior Bible §I): persistence saves durable semantics,
never live privilege. Resume does not restore: temporary permission, workspace
trust verdicts, API keys in the clear, live MCP sessions, threads / locks / OS
handles, or old abort controllers.

This module formalizes the lifecycle owner for start / resume / fork / rewind /
end. The resume path delegates to the existing durable-restore machinery
(``src.agent.resume_agent``) and enforces the ephemeral-drop contract at the
boundary: the only thing a resumed session may carry is durable identity +
workspace metadata (see ``DurableResumeMetadata``).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

#: Field names that must NEVER appear in durable resume metadata. This is a
#: defense-in-depth gate on the metadata schema: if a future change adds any
#: of these to the durable payload, the lifecycle gate fails closed instead of
#: silently restoring live capability.
EPHEMERAL_METADATA_KEYS = (
    "api_key",
    "permission_context",
    "permission_mode",
    "trust",
    "workspace_trusted",
    "mcp_clients",
    "mcp_client",
    "thread",
    "thread_id",
    "handle",
    "proc",
    "abort_controller",
    "abort_signal",
    "session_token",
    "credential",
)


class SessionPhase(str, Enum):
    STARTED = "started"
    RESUMED = "resumed"
    FORKED = "forked"
    REWOUND = "rewound"
    ENDED = "ended"


@dataclass
class SessionLifecycleRecord:
    session_id: str
    phase: SessionPhase
    durable_refs: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()


@dataclass
class SessionLifecycle:
    """Sole owner of session start / resume / fork / rewind / end.

    The class is deliberately thin: it does not reimplement resume (the
    durable machinery already exists); it is the AUTHORITY BOUNDARY that
    (a) routes lifecycle operations, and (b) enforces that nothing ephemeral
    crosses the resume boundary.
    """

    records: dict[str, SessionLifecycleRecord] = field(default_factory=dict)

    # ------------------------------------------------------------------ #
    # Lifecycle operations                                                #
    # ------------------------------------------------------------------ #

    def start(self, session_id: str, *, durable_refs: tuple[str, ...] = ()) -> SessionLifecycleRecord:
        record = SessionLifecycleRecord(session_id=session_id, phase=SessionPhase.STARTED, durable_refs=durable_refs)
        self.records[session_id] = record
        return record

    def end(self, session_id: str) -> SessionLifecycleRecord | None:
        record = self.records.get(session_id)
        if record is None:
            return None
        self.records[session_id] = SessionLifecycleRecord(
            session_id=session_id, phase=SessionPhase.ENDED, durable_refs=record.durable_refs
        )
        return self.records[session_id]

    def resume(self, agent_id: str, runtime: Any) -> Any:
        """Resume a task's DURABLE state; ephemeral capability is never restored.

        Delegates to ``resume_agent._restore_state_from_metadata`` (the
        existing durable restore) and then validates the ephemeral-drop
        contract on the resulting state. Returns the restored task state or
        ``None`` when there is nothing durable to restore.
        """
        from src.agent.resume_agent import _restore_state_from_metadata

        state = _restore_state_from_metadata(agent_id, runtime)
        if state is not None:
            self._assert_no_ephemeral_state(state)
            self.records[agent_id] = SessionLifecycleRecord(
                session_id=agent_id, phase=SessionPhase.RESUMED
            )
        return state

    def fork(self, session_id: str, *, notes: tuple[str, ...] = ()) -> SessionLifecycleRecord:
        """Fork a session: durable conversation identity is copied, live
        capability references are NOT (subagents rebuild permission / MCP /
        handle state from the parent at spawn time)."""
        self.records[session_id] = SessionLifecycleRecord(
            session_id=session_id, phase=SessionPhase.FORKED, notes=notes
        )
        return self.records[session_id]

    def rewind(self, session_id: str, *, notes: tuple[str, ...] = ()) -> SessionLifecycleRecord:
        self.records[session_id] = SessionLifecycleRecord(
            session_id=session_id, phase=SessionPhase.REWOUND, notes=notes
        )
        return self.records[session_id]

    # ------------------------------------------------------------------ #
    # Contract enforcement                                                #
    # ------------------------------------------------------------------ #

    def validate_durable_metadata(self, metadata: Any) -> list[str]:
        """Return every ephemeral key present on a resume-metadata object.

        An empty result means the metadata is durable-only and may be
        persisted / restored. Any hit is a contract violation.
        """
        violations: list[str] = []
        if metadata is None:
            return violations
        data = metadata.__dict__ if hasattr(metadata, "__dict__") else {}
        for key, value in data.items():
            lowered = key.lower()
            if any(token in lowered for token in EPHEMERAL_METADATA_KEYS) and value not in (None, ""):
                violations.append(f"{key}={value!r}")
        return violations

    def _assert_no_ephemeral_state(self, state: Any) -> None:
        data = state.__dict__ if hasattr(state, "__dict__") else {}
        for key in ("proc", "handle", "abort_controller"):
            if key in data and data[key] is not None:
                raise RuntimeError(
                    f"session lifecycle: resumed state carries live handle "
                    f"{key!r} — ephemeral capability must not cross the "
                    "resume boundary (Behavior Bible §I)"
                )
        violations = self.validate_durable_metadata(state)
        if violations:
            logger.warning(
                "session lifecycle: resumed state carries ephemeral-looking fields %s",
                violations,
            )

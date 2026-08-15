"""B7 W6 — AgentServer ownership facades.

The server's ``_AgentSession`` accumulated many lifecycle objects in one
class ("God Session"). Without changing the WebSocket / worker-thread /
permission Event roundtrip, this module splits the session's DIFFERENT
lifecycle concerns into typed sub-objects (per P1 spec §1 and
``blueprints/server_session_facades.py``) so tests can target one facade
instead of "one change affecting the whole session".

These are decomposition boundaries, not new logic: each facade holds
references to the LIVE session objects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class PermissionBridge:
    """Permission ask roundtrip between the worker and the surface."""

    ask_handler: Any = None
    pending_requests: dict[str, Any] = field(default_factory=dict)


@dataclass
class SurfaceEmitter:
    """Outbound event emission (thread-safe enqueue)."""

    emit: Callable[[dict], None] | None = None

    def push(self, msg: dict) -> None:
        if self.emit is not None:
            self.emit(msg)


@dataclass
class SchedulerBridge:
    """Bridge to the session's scheduled-task engine."""

    scheduler: Any = None


@dataclass
class SessionState:
    """Read-side session state view (app state / messages / stats)."""

    app_state: Any = None
    messages: Any = None  # callable -> list, or list
    stats: dict[str, Any] = field(default_factory=dict)

    def message_list(self) -> list:
        if callable(self.messages):
            return self.messages()
        return self.messages or []


@dataclass
class ServerSessionFacades:
    """Aggregate of the session's typed facades (B7 W6 decomposition)."""

    permission_bridge: PermissionBridge = field(default_factory=PermissionBridge)
    surface_emitter: SurfaceEmitter = field(default_factory=SurfaceEmitter)
    scheduler_bridge: SchedulerBridge = field(default_factory=SchedulerBridge)
    session_state: SessionState = field(default_factory=SessionState)

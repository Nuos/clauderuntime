from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass
class RuntimeSession:
    session_id: str
    permission_context: Any
    tool_context: Any
    task_registry: Any
    lifecycle: Any
    model_capability_resolver: Any
    extension_gate: Any
    surface_emitter: Any | None = None

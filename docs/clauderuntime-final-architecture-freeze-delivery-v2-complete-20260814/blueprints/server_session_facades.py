from dataclasses import dataclass
from typing import Any

@dataclass
class PermissionBridge:
    ask_handler: Any
    pending_requests: Any

@dataclass
class SurfaceEmitter:
    emit: Any

@dataclass
class SchedulerBridge:
    scheduler: Any

@dataclass
class SessionState:
    app_state: Any
    messages: Any
    stats: Any

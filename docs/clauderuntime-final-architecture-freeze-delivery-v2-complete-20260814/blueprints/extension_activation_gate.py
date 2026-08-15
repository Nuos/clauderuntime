from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any

class ActivationBehavior(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_TRUST = "require_trust"
    INVALID = "invalid"
    COLLISION = "collision"

@dataclass(frozen=True)
class ExtensionDescriptor:
    kind: str
    name: str
    source: str
    scope: str
    trust_level: str
    provenance_hash: str
    requested_capabilities: tuple[str, ...] = ()

@dataclass(frozen=True)
class ActivationDecision:
    behavior: ActivationBehavior
    reason: str

class ExtensionActivationGate:
    def decide(self, descriptor: ExtensionDescriptor, *, workspace_trusted: bool, policy: Any) -> ActivationDecision:
        raise NotImplementedError

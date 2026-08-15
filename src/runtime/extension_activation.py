"""B7 W3 — extension activation gate (trust-before-activation).

Lifecycle law (Behavior Bible §G): Discovery is separate from Activation.
Project Plugin / Skill / Hook / MCP must not execute merely because they were
discovered. Activation requires provenance, trust resolution, validation and a
deterministic collision policy.

This module provides the unified activation boundary:

    Discovery → ExtensionDescriptor → provenance → trust resolution
      → validation → ActivationDecision → capability registration

It deliberately does NOT change the internal mechanisms of Plugin / MCP /
Skill / Hook loaders (migration contract: unify the activation lifecycle, not
the mechanisms). Policy comes from ``machine/extension-trust-policy.yaml``.

Outcomes are auditable: every decision carries a reason, and the gate keeps a
provenance ledger (name → hash + precedence) so collisions are deterministic.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

logger = logging.getLogger(__name__)

TRUST_LEVELS = ("bundled", "managed", "user", "project", "mcp")

#: Default policy mirrors ``machine/extension-trust-policy.yaml``.
DEFAULT_POLICY: dict[str, Any] = {
    "activation": {
        "project_requires_workspace_trust": True,
        "discovery_may_execute_code": False,
        "partial_activation_rollback_required": True,
    },
    "collision": {
        "exact_same_hash": "dedupe",
        "same_precedence_different_content": "reject",
        "project_over_managed": "deny_by_default",
        "silent_overwrite": "forbidden",
    },
}

_POLICY_PATH = Path(__file__).resolve().parents[2] / "machine" / "extension-trust-policy.yaml"


def _load_policy() -> dict[str, Any]:
    try:
        import yaml  # type: ignore[import-not-found]

        raw = yaml.safe_load(_POLICY_PATH.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            return raw
    except Exception:  # noqa: BLE001 — policy is advisory; fall back to defaults
        logger.debug("extension-trust-policy.yaml unavailable; using defaults", exc_info=True)
    return DEFAULT_POLICY


class ActivationBehavior(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_TRUST = "require_trust"
    INVALID = "invalid"
    COLLISION = "collision"


@dataclass(frozen=True)
class ExtensionDescriptor:
    """Everything the gate needs to make an activation decision.

    ``scope`` ∈ {bundled, managed, user, project, mcp}; ``trust_level`` is the
    resolved trust classification; ``provenance_hash`` fingerprints the
    extension content (manifest + payload) for deterministic collision
    detection.
    """

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


@dataclass
class _LedgerEntry:
    name: str
    scope: str
    provenance_hash: str


class ExtensionActivationGate:
    """Deterministic trust-before-activation boundary for extensions.

    Instances keep an in-process activation ledger for collision detection and
    provenance audit. ``decide`` is pure with respect to the ledger: pass
    ``ledger`` explicitly or rely on the instance ledger.
    """

    def __init__(self, policy: Mapping[str, Any] | None = None) -> None:
        loaded = dict(policy) if policy is not None else _load_policy()
        self.policy: dict[str, Any] = {
            "activation": {
                **DEFAULT_POLICY["activation"],
                **(loaded.get("activation") or {}),
            },
            "collision": {
                **DEFAULT_POLICY["collision"],
                **(loaded.get("collision") or {}),
            },
        }
        self._ledger: dict[str, _LedgerEntry] = {}

    # ------------------------------------------------------------------ #
    # Decision                                                            #
    # ------------------------------------------------------------------ #

    def decide(
        self,
        descriptor: ExtensionDescriptor,
        *,
        workspace_trusted: bool,
        ledger: Mapping[str, _LedgerEntry] | None = None,
    ) -> ActivationDecision:
        """Resolve the activation decision for ``descriptor``.

        Order of checks (deterministic):

        1. INVALID — malformed descriptor (missing name/hash/scope, unknown
           kind or trust level).
        2. COLLISION — name already active with different content at the same
           precedence (silent overwrite forbidden); exact-same-hash dedupes.
        3. TRUST — project/user/mcp scope executable activation requires the
           workspace to be trusted (``project_requires_workspace_trust``).
        4. DENY — policy-level denials (``project_over_managed`` etc.).
        5. ALLOW — activation may proceed.
        """
        # 1) structural validity
        invalid = self._invalid_reason(descriptor)
        if invalid:
            return ActivationDecision(ActivationBehavior.INVALID, invalid)

        active = (ledger if ledger is not None else self._ledger).get(descriptor.name)

        # 4) policy-level denials (before dedupe: a project shadow of a
        #    managed extension is denied even for identical content)
        denial = self._policy_denial(descriptor, active)
        if denial:
            return ActivationDecision(ActivationBehavior.DENY, denial)

        # 2) deterministic collision policy
        if active is not None:
            if active.provenance_hash == descriptor.provenance_hash:
                # exact_same_hash → dedupe (idempotent re-activation)
                return ActivationDecision(
                    ActivationBehavior.ALLOW,
                    f"dedupe: identical content for {descriptor.name!r} already active",
                )
            collision_policy = self.policy["collision"]
            if collision_policy.get("silent_overwrite") == "forbidden":
                return ActivationDecision(
                    ActivationBehavior.COLLISION,
                    f"name collision: {descriptor.name!r} active with different "
                    f"content (hash {active.provenance_hash[:12]}); silent "
                    "overwrite is forbidden — reject or explicitly replace",
                )
            if collision_policy.get("same_precedence_different_content") == "reject":
                return ActivationDecision(
                    ActivationBehavior.COLLISION,
                    f"same-precedence collision for {descriptor.name!r} with "
                    "different content is rejected by policy",
                )
            return ActivationDecision(
                ActivationBehavior.COLLISION,
                f"collision policy does not allow overwriting {descriptor.name!r}",
            )

        # 3) trust-before-activation for executable extension scopes
        activation = self.policy["activation"]
        if descriptor.scope in ("project", "user", "mcp") and activation.get(
            "project_requires_workspace_trust"
        ):
            if not workspace_trusted:
                return ActivationDecision(
                    ActivationBehavior.REQUIRE_TRUST,
                    f"extension {descriptor.name!r} (scope={descriptor.scope}) "
                    "requires workspace trust before activation; workspace is "
                    "not trusted",
                )

        return ActivationDecision(
            ActivationBehavior.ALLOW, f"extension {descriptor.name!r} may activate"
        )

    def activate(
        self,
        descriptor: ExtensionDescriptor,
        *,
        workspace_trusted: bool,
    ) -> ActivationDecision:
        """Decide AND record the outcome in the instance ledger (auditable)."""
        decision = self.decide(descriptor, workspace_trusted=workspace_trusted)
        if decision.behavior in (ActivationBehavior.ALLOW,):
            self._ledger[descriptor.name] = _LedgerEntry(
                name=descriptor.name,
                scope=descriptor.scope,
                provenance_hash=descriptor.provenance_hash,
            )
        return decision

    # ------------------------------------------------------------------ #
    # Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _invalid_reason(self, descriptor: ExtensionDescriptor) -> str | None:
        if not descriptor.name or not descriptor.name.strip():
            return "extension name is required"
        if not descriptor.provenance_hash or len(descriptor.provenance_hash) < 8:
            return "extension provenance_hash is required (>=8 hex chars)"
        if descriptor.scope not in TRUST_LEVELS:
            return f"unknown extension scope {descriptor.scope!r} (expected one of {TRUST_LEVELS})"
        if descriptor.trust_level not in TRUST_LEVELS:
            return f"unknown trust_level {descriptor.trust_level!r} (expected one of {TRUST_LEVELS})"
        if not descriptor.kind or not descriptor.source:
            return "extension kind and source are required"
        return None

    def _policy_denial(
        self, descriptor: ExtensionDescriptor, active: _LedgerEntry | None
    ) -> str | None:
        if (
            descriptor.scope == "project"
            and active is not None
            and active.scope == "managed"
            and self.policy["collision"].get("project_over_managed") == "deny_by_default"
        ):
            # A project-scope extension shadowing a managed one is denied by
            # default; explicit replacement must go through the caller.
            return (
                f"project-scope extension {descriptor.name!r} shadowing managed "
                "extension is denied by default (project_over_managed policy)"
            )
        return None

    # ------------------------------------------------------------------ #
    # Audit                                                               #
    # ------------------------------------------------------------------ #

    def ledger(self) -> list[dict[str, str]]:
        return [
            {"name": e.name, "scope": e.scope, "provenance_hash": e.provenance_hash}
            for e in self._ledger.values()
        ]

    def is_active(self, name: str) -> bool:
        return name in self._ledger


def content_hash(*parts: str | bytes) -> str:
    """Fingerprint extension content for provenance (deterministic)."""
    digest = hashlib.sha256()
    for part in parts:
        data = part.encode("utf-8") if isinstance(part, str) else part
        digest.update(data)
        digest.update(b"\x00")
    return digest.hexdigest()


def descriptor_from_loaded_plugin(plugin: Any) -> ExtensionDescriptor:
    """Adapt a ``LoadedPlugin`` into an :class:`ExtensionDescriptor`.

    Scope derives from the plugin's ``source`` (bundled/managed/user/project/
    mcp); provenance hashes the manifest name + path so two different plugins
    with the same name collide deterministically.
    """
    source = getattr(plugin, "source", "user") or "user"
    scope = source if source in TRUST_LEVELS else "user"
    path = str(getattr(plugin, "path", "") or "")
    manifest = getattr(plugin, "manifest", None)
    manifest_name = getattr(manifest, "name", "") or getattr(plugin, "name", "")
    provenance = content_hash(manifest_name, path)
    return ExtensionDescriptor(
        kind="plugin",
        name=getattr(plugin, "name", ""),
        source=source,
        scope=scope,
        trust_level=scope,
        provenance_hash=provenance,
    )

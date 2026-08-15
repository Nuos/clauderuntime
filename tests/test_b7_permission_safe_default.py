"""B7 W1 — Permission Safe-by-Default contract tests.

Covers the W1 exit conditions:
- ``ToolContext`` no longer defaults to an implicit ``bypassPermissions``;
- a bare ``bypassPermissions`` mode is NOT honored (fails closed) unless it
  carries explicit ``bypass_origin`` / ``bypass_reason``;
- headless (no interaction channel) ask → deny;
- production setup / subagent / rule-loader paths preserve or attach bypass
  provenance instead of silently dropping it.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from typing import Any

from src.agent.run_agent import _build_permission_context
from src.permissions.check import has_permissions_to_use_tool
from src.permissions.loader import apply_rules_to_context
from src.permissions.setup import setup_permissions
from src.permissions.types import (
    PermissionAllowDecision,
    PermissionPassthroughResult,
    PermissionResult,
    ToolPermissionContext,
)
from src.tool_system.context import ToolContext


class _MockTool:
    def __init__(self, name: str = "TestTool") -> None:
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_mcp(self) -> bool:
        return False

    def check_permissions(self, tool_input: dict[str, Any], context: Any) -> PermissionResult:
        return PermissionPassthroughResult()


class TestToolContextSafeDefault(unittest.TestCase):
    def test_default_mode_is_safe_default_not_bypass(self) -> None:
        ctx = ToolContext(workspace_root=Path("."))
        self.assertEqual(ctx.permission_context.mode, "default")
        self.assertFalse(ctx.permission_context.is_bypass_justified())

    def test_explicit_justified_bypass_still_supported(self) -> None:
        ctx = ToolContext(
            workspace_root=Path("."),
            permission_context=ToolPermissionContext(
                mode="bypassPermissions",
                bypass_origin="test:explicit",
                bypass_reason="explicit test context",
            ),
        )
        self.assertTrue(ctx.permission_context.is_bypass_justified())


class TestBypassJustification(unittest.TestCase):
    def test_bare_bypass_not_justified(self) -> None:
        self.assertFalse(ToolPermissionContext(mode="bypassPermissions").is_bypass_justified())

    def test_bypass_with_provenance_justified(self) -> None:
        ctx = ToolPermissionContext(
            mode="bypassPermissions",
            bypass_origin="cli:--dangerously-skip-permissions",
            bypass_reason="explicit user request",
        )
        self.assertTrue(ctx.is_bypass_justified())

    def test_bypass_origin_without_reason_not_justified(self) -> None:
        ctx = ToolPermissionContext(mode="bypassPermissions", bypass_origin="cli:x")
        self.assertFalse(ctx.is_bypass_justified())

    def test_bypass_reason_without_origin_not_justified(self) -> None:
        ctx = ToolPermissionContext(mode="bypassPermissions", bypass_reason="r")
        self.assertFalse(ctx.is_bypass_justified())

    def test_default_mode_not_bypass_justified(self) -> None:
        self.assertFalse(ToolPermissionContext().is_bypass_justified())


class TestDecisionLayerFailsClosed(unittest.TestCase):
    def test_unjustified_bypass_not_honored(self) -> None:
        # A bare bypassPermissions context must NOT short-circuit to allow.
        ctx = ToolPermissionContext(mode="bypassPermissions")
        result = has_permissions_to_use_tool(_MockTool(), {}, ctx)
        self.assertNotIsInstance(result, PermissionAllowDecision)
        self.assertEqual(result.behavior, "ask")

    def test_justified_bypass_honored(self) -> None:
        ctx = ToolPermissionContext(
            mode="bypassPermissions",
            bypass_origin="cli:--dangerously-skip-permissions",
            bypass_reason="explicit user request",
        )
        result = has_permissions_to_use_tool(_MockTool(), {}, ctx)
        self.assertIsInstance(result, PermissionAllowDecision)
        self.assertEqual(result.behavior, "allow")

    def test_headless_ask_without_channel_denies(self) -> None:
        # Headless (no interaction channel → should_avoid_permission_prompts)
        # must convert any ask into a deny (fail closed).
        ctx = ToolPermissionContext(mode="default", should_avoid_permission_prompts=True)
        result = has_permissions_to_use_tool(_MockTool(), {}, ctx)
        self.assertEqual(result.behavior, "deny")

    def test_headless_unjustified_bypass_denies(self) -> None:
        # Unjustified bypass + headless → bypass not honored AND no channel → deny.
        ctx = ToolPermissionContext(
            mode="bypassPermissions", should_avoid_permission_prompts=True
        )
        result = has_permissions_to_use_tool(_MockTool(), {}, ctx)
        self.assertEqual(result.behavior, "deny")


class TestSetupCarriesProvenance(unittest.TestCase):
    def test_setup_bypass_mode_gets_justification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = setup_permissions(cwd=tmp, mode="bypassPermissions")
            self.assertTrue(result.context.is_bypass_justified())
            self.assertIsNotNone(result.context.bypass_origin)

    def test_setup_explicit_provenance_kept(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = setup_permissions(
                cwd=tmp,
                mode="bypassPermissions",
                bypass_origin="test:explicit-origin",
                bypass_reason="test explicit reason",
            )
            self.assertEqual(result.context.bypass_origin, "test:explicit-origin")
            self.assertTrue(result.context.is_bypass_justified())

    def test_setup_default_mode_is_safe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = setup_permissions(cwd=tmp)
            self.assertEqual(result.context.mode, "default")
            self.assertFalse(result.context.is_bypass_justified())

    def test_setup_additional_dirs_preserves_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = setup_permissions(
                cwd=tmp,
                mode="bypassPermissions",
                bypass_origin="test:origin",
                bypass_reason="test reason",
            )
            # Force the additional-dirs reconstruction path via rules round-trip.
            rebuilt = apply_rules_to_context(result.context, [])
            self.assertEqual(rebuilt.bypass_origin, "test:origin")
            self.assertTrue(rebuilt.is_bypass_justified())


class TestSubagentInheritance(unittest.TestCase):
    def test_subagent_propagates_parent_bypass_provenance(self) -> None:
        parent = ToolContext(
            workspace_root=Path("."),
            permission_context=ToolPermissionContext(
                mode="bypassPermissions",
                bypass_origin="cli:--dangerously-skip-permissions",
                bypass_reason="explicit user request",
            ),
        )
        child_ctx = _build_permission_context(parent, "bypassPermissions", is_async=False)
        self.assertTrue(child_ctx.is_bypass_justified())

    def test_subagent_default_mode_gets_explicit_origin_but_stays_safe(self) -> None:
        parent = ToolContext(workspace_root=Path("."))
        child_ctx = _build_permission_context(parent, "default", is_async=False)
        self.assertEqual(child_ctx.mode, "default")
        self.assertFalse(child_ctx.is_bypass_justified())


if __name__ == "__main__":
    unittest.main()

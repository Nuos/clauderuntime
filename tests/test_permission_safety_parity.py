"""Wave 2 F6 — 权限安全链差分测试（deny-first / fail-closed / hook 不变式）。

对照 B3 强制安全规则：
- deny > ask > allow（settings 规则层，已有 parity 测试，此处补边界）
- classifier 不可用不得 silent allow（auto mode + unavailable → 交互保持 ask /
  headless 转为 deny）
- headless cannot-prompt → fail closed（ask + should_avoid → deny + 可解释 reason）
- hook allow 不能越过 deny/safety（hook 层只产出 hookPermissionResult marker，
  最终决策由权限层做出）
"""

import asyncio
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from src.permissions.check import has_permissions_to_use_tool
from src.permissions.types import (
    PermissionPassthroughResult,
    ToolPermissionContext,
)
from src.services.tool_execution.tool_hooks import run_pre_tool_use_hooks
from src.tool_system.context import ToolContext
from src.types.messages import UserMessage


def _make_mock_tool(name: str):
    tool = MagicMock()
    tool.name = name
    tool.check_permissions = MagicMock(
        return_value=PermissionPassthroughResult(
            behavior="passthrough", message="Allow?",
        )
    )
    return tool


class TestClassifierFailClosed(unittest.TestCase):
    """auto mode + classifier 不可用：不得 silent allow。"""

    def setUp(self):
        self.tool = _make_mock_tool("Bash")

    def _ctx(self, avoid_prompts: bool) -> ToolPermissionContext:
        return ToolPermissionContext(
            mode="auto",
            should_avoid_permission_prompts=avoid_prompts,
        )

    def test_classifier_unavailable_headless_fails_closed(self):
        """classifier 不可用 + headless → deny（不 silent allow）。"""
        with patch("src.permissions.check.auto_mode_classify") as mock_cls:
            mock_cls.return_value = MagicMock(
                unavailable=True, allow=False, reason="classifier_down",
            )
            decision = has_permissions_to_use_tool(
                self.tool, {"command": "ls"}, self._ctx(avoid_prompts=True),
            )
        self.assertEqual(decision.behavior, "deny")
        # 决策必须有可解释 reason（F10）
        self.assertIsNotNone(decision.decision_reason)
        self.assertIn("unavailable", str(getattr(decision, "message", "")).lower())

    def test_classifier_unavailable_interactive_keeps_ask(self):
        """classifier 不可用 + 交互 → 保持 ask（交由用户）。"""
        with patch("src.permissions.check.auto_mode_classify") as mock_cls:
            mock_cls.return_value = MagicMock(
                unavailable=True, allow=False, reason="classifier_down",
            )
            decision = has_permissions_to_use_tool(
                self.tool, {"command": "ls"}, self._ctx(avoid_prompts=False),
            )
        self.assertEqual(decision.behavior, "ask")


class TestHeadlessFailClosed(unittest.TestCase):
    """headless cannot-prompt → fail closed。"""

    def test_headless_deny_has_decision_reason(self):
        tool = _make_mock_tool("Write")
        ctx = ToolPermissionContext(
            mode="default",
            always_ask_rules={"session": ["Write"]},
            should_avoid_permission_prompts=True,
        )
        decision = has_permissions_to_use_tool(
            tool, {"file_path": "/tmp/x", "content": "y"}, ctx,
        )
        self.assertEqual(decision.behavior, "deny")
        self.assertIsNotNone(decision.decision_reason)
        self.assertIn("prompts", str(getattr(decision, "message", "")).lower())


class TestHookMarkerInvariant(unittest.TestCase):
    """hook allow 只产出 marker，不直接决定权限（deny/safety 不可被 hook 越过）。"""

    async def _run_hook(self, permission_behavior: str):
        context = ToolContext(workspace_root=Path("/tmp"))
        tool = _make_mock_tool("Bash")
        results = []
        with patch(
            "src.hooks.hook_executor.has_hook_for_event",
            return_value=True,
        ), patch(
            "src.hooks.hook_executor.execute_pre_tool_hooks",
        ) as mock_exec:
            async def _fake_gen():
                yield {"permission_behavior": permission_behavior}

            mock_exec.side_effect = lambda *a, **k: _fake_gen()
            async for r in run_pre_tool_use_hooks(
                context, tool, {"command": "ls"}, "toolu_hook",
            ):
                results.append(r)
        return results

    def test_hook_allow_yields_marker_not_decision(self):
        """hook 返回 allow 时：产出 hookPermissionResult 标记而非最终 allow。"""
        results = asyncio.run(self._run_hook("allow"))
        self.assertTrue(results, "hook 应有结果")
        for r in results:
            rtype = r.get("type") if isinstance(r, dict) else getattr(r, "type", None)
            # marker 类型：hookPermissionResult / message / additionalContext，
            # 绝不包含独立生效的最终权限决策
            self.assertIn(
                rtype,
                {"hookPermissionResult", "message", "additionalContext",
                 "hookUpdatedInput", "preventContinuation", "stopReason", "stop"},
                f"hook 产出了非法结果类型: {rtype}",
            )


if __name__ == "__main__":
    unittest.main()

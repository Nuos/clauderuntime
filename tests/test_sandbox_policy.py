"""Wave 4 F15 — sandbox fail-closed 测试（CCR-12 Isolation Runtime）。

对照规则圣经 CCR-12：
- NoSandboxBackend 只能作显式 unsandboxed backend
- 不得伪装成 isolation complete（provides_isolation=False）
- require_isolation / 禁 unsandboxed 时 fail-closed
"""

import unittest
from pathlib import Path
from unittest.mock import MagicMock

from src.execution.sandbox import (
    NoSandboxBackend,
    SandboxPolicy,
    SandboxRequest,
    default_sandbox_backend,
    sandbox_policy_from_settings,
)


def _request() -> SandboxRequest:
    return SandboxRequest(argv=("echo", "hi"), cwd=Path("/tmp"))


class TestNoSandboxFailClosed(unittest.TestCase):
    """NoSandboxBackend fail-closed 语义。"""

    def setUp(self):
        self.backend = NoSandboxBackend()

    def test_capability_reports_no_isolation(self):
        """provides_isolation 必须为 False（不伪装 complete）。"""
        cap = self.backend.capability()
        self.assertFalse(cap.provides_isolation)
        self.assertTrue(cap.available)

    def test_require_isolation_denied(self):
        """require_isolation=True 且 backend 无隔离 → deny。"""
        policy = SandboxPolicy(require_isolation=True, allow_unsandboxed=False)
        invocation = self.backend.prepare(_request(), policy)
        self.assertFalse(invocation.allowed)
        self.assertFalse(invocation.isolated)
        self.assertIn("isolation required", invocation.reason)

    def test_disallow_unsandboxed_denied(self):
        """allow_unsandboxed=False 且 backend 无隔离 → deny。"""
        policy = SandboxPolicy(require_isolation=False, allow_unsandboxed=False)
        invocation = self.backend.prepare(_request(), policy)
        self.assertFalse(invocation.allowed)
        self.assertIn("unsandboxed", invocation.reason.lower())

    def test_default_unsandboxed_allowed_not_isolated(self):
        """默认 policy → allowed 但 isolated=False（显式 unsandboxed）。"""
        invocation = self.backend.prepare(_request(), SandboxPolicy())
        self.assertTrue(invocation.allowed)
        self.assertFalse(invocation.isolated)

    def test_run_denied_invocation_returns_126(self):
        """denied invocation run → exit 126（不执行命令）。"""
        policy = SandboxPolicy(require_isolation=True, allow_unsandboxed=False)
        invocation = self.backend.prepare(_request(), policy)
        result = self.backend.run(invocation)
        self.assertEqual(result.exit_code, 126)
        self.assertIn("isolation", result.stderr)


class TestSandboxPolicyFromSettings(unittest.TestCase):
    """settings → SandboxPolicy 解析。"""

    def test_no_sandbox_setting_defaults(self):
        """无 sandbox 设置 → 默认（允许 unsandboxed）。"""
        policy = sandbox_policy_from_settings(MagicMock(sandbox=None))
        self.assertFalse(policy.require_isolation)
        self.assertTrue(policy.allow_unsandboxed)

    def test_sandbox_disabled_defaults(self):
        """sandbox.enabled=False → 默认 policy。"""
        policy = sandbox_policy_from_settings(
            MagicMock(sandbox=MagicMock(enabled=False)),
        )
        self.assertFalse(policy.require_isolation)

    def test_sandbox_fail_if_unavailable_requires_isolation(self):
        """sandbox.enabled=True + fail_if_unavailable=True → require_isolation。"""
        settings = MagicMock(
            sandbox=MagicMock(
                enabled=True,
                fail_if_unavailable=True,
                enabled_platforms=(),
                allow_unsandboxed_commands=True,
            )
        )
        policy = sandbox_policy_from_settings(settings)
        self.assertTrue(policy.require_isolation)
        self.assertFalse(policy.allow_unsandboxed)

    def test_platform_gate_disables_sandbox(self):
        """平台不在 enabled_platforms → 默认 policy（不要求隔离）。"""
        settings = MagicMock(
            sandbox=MagicMock(
                enabled=True,
                enabled_platforms=("linux",),  # 非 macos
                fail_if_unavailable=True,
                allow_unsandboxed_commands=True,
            )
        )
        policy = sandbox_policy_from_settings(settings, platform="macos")
        self.assertFalse(policy.require_isolation)

    def test_default_backend_is_no_sandbox(self):
        """default_sandbox_backend 返回 NoSandboxBackend。"""
        self.assertIsInstance(default_sandbox_backend(), NoSandboxBackend)


if __name__ == "__main__":
    unittest.main()

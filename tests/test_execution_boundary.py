"""Wave 4 F14/F18 — isolation 边界差分测试（CCR-12 Isolation Runtime）。

对照规则圣经 CCR-12 强制不变量：
- Permission ≠ Isolation；Execution Environment ≠ Isolation
- filesystem/network/env/secrets/subprocess 五边界独立约束、可独立失败
- workspace canonicalization + roots 校验 + symlink 解析（R7-07 real-target/symlink second check）
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from src.execution.boundary import (
    DefaultProcessPolicy,
    DefaultWorkspaceGuard,
    ExecutionBoundary,
    minimal_execution_boundary,
)
from src.execution.policy import (
    ConfigurableNetworkPolicy,
    MinimalEnvPolicy,
)
from src.execution.sandbox import MacOSSandboxBackend, NoSandboxBackend, default_sandbox_backend


class TestIsolationBoundaryIndependence(unittest.TestCase):
    """Permission ≠ Isolation、五边界独立。"""

    def test_permission_is_not_isolation(self):
        """sandbox backend 与 permission 层分离，能力必须显式报告。"""
        backend = default_sandbox_backend()
        self.assertIsInstance(backend, (NoSandboxBackend, MacOSSandboxBackend))
        cap = backend.capability()
        self.assertIsInstance(cap.provides_isolation, bool)
        self.assertTrue(cap.reason)

    def test_five_boundaries_independent(self):
        """ExecutionBoundary 组合五个独立可替换组件。"""
        boundary = ExecutionBoundary()
        self.assertIsInstance(boundary.workspace_guard, DefaultWorkspaceGuard)
        self.assertIsInstance(boundary.process_policy, DefaultProcessPolicy)
        # sandbox / network / env 各自独立（不是同一对象）
        self.assertIsNot(
            boundary.sandbox_backend, boundary.network_policy,
        )
        # 每个边界可独立替换（injection）
        custom = ExecutionBoundary(
            workspace_guard=MagicMock(),
            sandbox_backend=NoSandboxBackend(name="custom"),  # type: ignore[arg-type]
        )
        self.assertIsNotNone(custom.workspace_guard)
        self.assertEqual(custom.sandbox_backend.name, "custom")

    def test_minimal_boundary_uses_minimal_policies(self):
        """minimal_execution_boundary 使用 MinimalEnvPolicy + ConfigurableNetworkPolicy。"""
        boundary = minimal_execution_boundary(network_mode="none")
        self.assertIsInstance(boundary.env_policy, MinimalEnvPolicy)
        self.assertIsInstance(boundary.network_policy, ConfigurableNetworkPolicy)
        self.assertEqual(
            getattr(boundary.network_policy, "mode"), "none",
        )


class TestWorkspaceGuard(unittest.TestCase):
    """workspace canonicalization + roots 校验（F18）。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.guard = DefaultWorkspaceGuard()
        (self.root / "sub").mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def test_inside_roots_allowed(self):
        """workspace 内路径 → allow。"""
        decision = self.guard.check_path(
            self.root / "sub" / "file.txt",
            roots=[self.root], access="read",
        )
        self.assertTrue(decision.allow)

    def test_outside_roots_denied(self):
        """workspace 外路径 → deny。"""
        outside = Path(tempfile.gettempdir()) / "outside.txt"
        decision = self.guard.check_path(
            outside, roots=[self.root], access="write",
        )
        self.assertFalse(decision.allow)
        self.assertIn("outside", decision.reason.lower())

    def test_workspace_escape_explicit(self):
        """allow_workspace_escape=True → 显式放行（保留 Full Access 语义）。"""
        outside = Path(tempfile.gettempdir()) / "esc.txt"
        decision = self.guard.check_path(
            outside, roots=[self.root], access="read",
            allow_workspace_escape=True,
        )
        self.assertTrue(decision.allow)
        self.assertIn("escape", decision.reason.lower())

    def test_symlink_resolved_to_real_target(self):
        """symlink 路径解析到真实目标后判定（real-target second check）。"""
        # 创建 symlink 指向 workspace 外 → resolve 后应 deny
        outside = Path(tempfile.gettempdir()) / "clauderuntime_real_target.txt"
        outside.write_text("secret")
        symlink = self.root / "sub" / "link.txt"
        symlink.symlink_to(outside)
        decision = self.guard.check_path(
            symlink, roots=[self.root], access="read",
        )
        # resolve() 解 symlink → 指向 workspace 外 → deny
        self.assertFalse(decision.allow)
        self.assertEqual(decision.path, outside.resolve())

    def test_relative_path_resolved(self):
        """相对路径 resolve 为绝对路径后判定。"""
        decision = self.guard.check_path(
            Path("."), roots=[self.root], access="read",
            allow_workspace_escape=True,
        )
        self.assertTrue(decision.path.is_absolute())


class TestProcessPolicy(unittest.TestCase):
    """process policy（F14 边界之一）。"""

    def test_empty_command_denied(self):
        """空命令 → deny。"""
        decision = DefaultProcessPolicy().check_process(
            "   ", cwd=Path("/tmp"),
        )
        self.assertFalse(decision.allow)

    def test_nonempty_command_allowed(self):
        """非空命令 → allow（默认 policy）。"""
        decision = DefaultProcessPolicy().check_process(
            "echo hi", cwd=Path("/tmp"),
        )
        self.assertTrue(decision.allow)


if __name__ == "__main__":
    unittest.main()

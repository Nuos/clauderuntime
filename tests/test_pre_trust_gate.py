"""Wave 3 F13 — trust lifecycle 测试（CCR-13 Trust）。

对照 reference pre-trust / trust lifecycle 语义：
- trusted 来源（enterprise/managed/policy/user/dynamic）→ allow
- project/local/unknown 来源 → 需要 workspace trust（project-scoped）
- unknown 来源 fail-closed（无 workspace trust 时 deny）
- session trust 不恢复：resume 场景 workspace_trusted=False 时
  project 来源不得因会话恢复而自动放行
"""

import tempfile
import unittest
from pathlib import Path

from src.permissions.pre_trust import check_pre_trust_gate


class TestPreTrustGate(unittest.TestCase):
    """check_pre_trust_gate 判定。"""

    def test_trusted_sources_allowed(self):
        """operator/enterprise 来源直接允许。"""
        for source in ("enterprise", "managed", "policy", "user", "dynamic"):
            with self.subTest(source=source):
                decision = check_pre_trust_gate("hook", source=source)
                self.assertTrue(decision.allow, f"{source} 应 allow: {decision.reason}")

    def test_project_source_requires_workspace_trust(self):
        """project 来源：workspace_trusted=True → allow；False → deny。"""
        ok = check_pre_trust_gate(
            "mcp", source="project", workspace_trusted=True,
        )
        self.assertTrue(ok.allow)
        denied = check_pre_trust_gate(
            "mcp", source="project", workspace_trusted=False,
        )
        self.assertFalse(denied.allow)

    def test_local_source_requires_workspace_trust(self):
        """local 来源同样需要 workspace trust。"""
        denied = check_pre_trust_gate(
            "project-config", source="local", workspace_trusted=False,
        )
        self.assertFalse(denied.allow)

    def test_unknown_fails_closed(self):
        """unknown 来源无 workspace trust → deny（fail-closed）。
        显式传 workspace_trusted=False（不依赖全局会话信任状态，
        避免全量顺序下的全局状态 flaky）。"""
        decision = check_pre_trust_gate(
            "hook", source=None, workspace_trusted=False,
        )
        self.assertFalse(decision.allow)
        self.assertIn("unknown", decision.reason.lower())

    def test_session_trust_not_restored_on_resume(self):
        """resume 场景：workspace_trusted=False 时 project 来源仍被拒
        （session-scoped trust 不因会话恢复而重建）。"""
        decision = check_pre_trust_gate(
            "mcp",
            source="project",
            workspace_trusted=False,
            cwd="/tmp/workspace",
        )
        self.assertFalse(decision.allow)
        self.assertIn("trust", decision.reason.lower())

    def test_action_label_in_reason(self):
        """reason 携带 action 标签（hook/mcp/project-config 可区分）。"""
        decision = check_pre_trust_gate(
            "hook", source="user",
        )
        self.assertIn("hook", decision.reason.lower())


if __name__ == "__main__":
    unittest.main()

"""Wave 4 F16/F17 — env/secret policy + network policy 测试（CCR-12）。

对照规则圣经 CCR-12 的 env/secrets 与 network 独立约束：
- MinimalEnvPolicy：allowlist 保留 + secret scrub + GitHub Action INPUT twins 移除
- ConfigurableNetworkPolicy：none/loopback/allowlist/full 四模式 + 无 host fail-closed
"""

import unittest

from src.execution.policy import (
    ConfigurableNetworkPolicy,
    MinimalEnvPolicy,
    _is_loopback_host,
    default_network_policy,
)
from src.execution.boundary import DefaultEnvPolicy as BoundaryDefaultEnvPolicy
from src.utils.subprocess_env import SUBPROCESS_SECRET_ENV_KEYS


class TestMinimalEnvPolicy(unittest.TestCase):
    """F16 — env/secret policy。"""

    def test_keeps_allowlist(self):
        """allowlist 内的 key 保留。"""
        env = {"PATH": "/usr/bin", "HOME": "/root", "RANDOM_VAR": "x"}
        result = MinimalEnvPolicy().prepare_env(env)
        self.assertIn("PATH", result)
        self.assertIn("HOME", result)
        self.assertNotIn("RANDOM_VAR", result)

    def test_scrubs_secret_keys(self):
        """secret key 被移除（provider/tool secrets）。"""
        secret = next(iter(SUBPROCESS_SECRET_ENV_KEYS))
        env = {"PATH": "/usr/bin", secret: "should-not-leak"}
        result = MinimalEnvPolicy().prepare_env(env)
        self.assertNotIn(secret, result)

    def test_scrubs_input_twins(self):
        """GitHub Action INPUT_ 前缀 twin 被移除。"""
        secret = next(iter(SUBPROCESS_SECRET_ENV_KEYS))
        twin = f"INPUT_{secret}"
        env = {"PATH": "/usr/bin", twin: "leak", secret: "leak2"}
        result = MinimalEnvPolicy().prepare_env(env)
        self.assertNotIn(twin, result)
        self.assertNotIn(secret, result)

    def test_extra_allowed_keys(self):
        """extra_allowed_keys 生效（但仍受 secret scrub 约束）。"""
        policy = MinimalEnvPolicy(extra_allowed_keys=("MY_TOOL_VAR",))
        env = {"MY_TOOL_VAR": "keep", "OTHER": "drop"}
        result = policy.prepare_env(env)
        self.assertIn("MY_TOOL_VAR", result)
        self.assertNotIn("OTHER", result)

    def test_default_env_passthrough(self):
        """DefaultEnvPolicy 全量透传（兼容默认）。"""
        env = {"PATH": "/usr/bin", "SECRET": "x"}
        result = BoundaryDefaultEnvPolicy().prepare_env(env)
        self.assertEqual(result, env)


class TestNetworkPolicy(unittest.TestCase):
    """F17 — network policy 四模式。"""

    def test_none_denies_all(self):
        """mode=none → 全部 deny。"""
        policy = ConfigurableNetworkPolicy(mode="none")
        self.assertFalse(policy.check_url("https://example.com").allow)

    def test_full_allows_all(self):
        """mode=full → 全部 allow。"""
        policy = ConfigurableNetworkPolicy(mode="full")
        self.assertTrue(policy.check_url("https://example.com").allow)

    def test_loopback_allows_localhost(self):
        """mode=loopback → localhost allow，外部 deny。"""
        policy = ConfigurableNetworkPolicy(mode="loopback")
        self.assertTrue(policy.check_url("http://localhost:8080/x").allow)
        self.assertTrue(policy.check_url("http://127.0.0.1:8080/x").allow)
        self.assertFalse(policy.check_url("https://example.com").allow)

    def test_allowlist_matches_host(self):
        """mode=allowlist → 命中 allow，未命中 deny。"""
        policy = ConfigurableNetworkPolicy(
            mode="allowlist", allowed_hosts=frozenset({"api.example.com"}),
        )
        self.assertTrue(policy.check_url("https://api.example.com/v1").allow)
        self.assertFalse(policy.check_url("https://other.com").allow)

    def test_no_host_fails_closed(self):
        """无 host 的 URL → deny（fail-closed）。"""
        policy = ConfigurableNetworkPolicy(mode="full")
        self.assertFalse(policy.check_url("not-a-url").allow)

    def test_loopback_host_detection(self):
        """_is_loopback_host：localhost / 127.x / 非 loopback。"""
        self.assertTrue(_is_loopback_host("localhost"))
        self.assertTrue(_is_loopback_host("127.0.0.1"))
        self.assertTrue(_is_loopback_host("::1"))
        self.assertFalse(_is_loopback_host("example.com"))

    def test_default_network_full(self):
        """default_network_policy → mode=full。"""
        self.assertEqual(getattr(default_network_policy(), "mode"), "full")


if __name__ == "__main__":
    unittest.main()

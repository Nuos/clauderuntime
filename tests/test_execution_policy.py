from __future__ import annotations

from src.execution import (
    ConfigurableNetworkPolicy,
    MinimalEnvPolicy,
    minimal_execution_boundary,
)
from src.utils.subprocess_env import SUBPROCESS_SECRET_ENV_KEYS


def test_minimal_env_policy_keeps_allowlist_and_strips_secrets():
    env = {
        "PATH": "/bin",
        "HOME": "/tmp/home",
        "ANTHROPIC_API_KEY": "secret",
        "INPUT_ANTHROPIC_API_KEY": "input-secret",
        "AWS_SECRET_ACCESS_KEY": "aws-secret",
        "CUSTOM_TOOL_TOKEN": "custom",
        "EXTRA_ALLOWED": "ok",
        "UNLISTED": "drop",
    }
    policy = MinimalEnvPolicy(
        extra_allowed_keys=("EXTRA_ALLOWED", "CUSTOM_TOOL_TOKEN"),
        secret_keys=SUBPROCESS_SECRET_ENV_KEYS + ("CUSTOM_TOOL_TOKEN",),
    )

    prepared = policy.prepare_env(env)

    assert prepared == {
        "PATH": "/bin",
        "HOME": "/tmp/home",
        "EXTRA_ALLOWED": "ok",
    }


def test_minimal_env_policy_returns_fresh_dict():
    env = {"PATH": "/bin"}

    prepared = MinimalEnvPolicy().prepare_env(env)
    prepared["PATH"] = "/usr/bin"

    assert env["PATH"] == "/bin"


def test_network_policy_none_denies_outbound_url():
    decision = ConfigurableNetworkPolicy(mode="none").check_url(
        "https://example.com/data",
        purpose="web-fetch",
    )

    assert decision.allow is False
    assert decision.mode == "none"
    assert decision.host == "example.com"
    assert "disabled" in decision.reason


def test_network_policy_loopback_allows_only_loopback_hosts():
    policy = ConfigurableNetworkPolicy(mode="loopback")

    assert policy.check_url("http://localhost:8000").allow is True
    assert policy.check_url("http://127.0.0.1:8000").allow is True
    assert policy.check_url("http://[::1]:8000").allow is True
    denied = policy.check_url("http://example.com")

    assert denied.allow is False
    assert "outside loopback" in denied.reason


def test_network_policy_allowlist_checks_host_exactly():
    policy = ConfigurableNetworkPolicy(
        mode="allowlist",
        allowed_hosts=frozenset({"api.example.com"}),
    )

    assert policy.check_url("https://api.example.com/v1").allow is True
    denied = policy.check_url("https://evil.example.com/v1")

    assert denied.allow is False
    assert denied.host == "evil.example.com"
    assert "not allowlisted" in denied.reason


def test_network_policy_full_allows_external_hosts():
    decision = ConfigurableNetworkPolicy(mode="full").check_url(
        "https://example.com",
    )

    assert decision.allow is True
    assert decision.reason == "network: full network access allowed"


def test_execution_boundary_exposes_minimal_profile():
    boundary = minimal_execution_boundary(
        network_mode="allowlist",
        allowed_hosts=("api.example.com",),
        extra_env_keys=("EXTRA_ALLOWED",),
    )

    assert boundary.prepare_env(
        {
            "PATH": "/bin",
            "EXTRA_ALLOWED": "ok",
            "ANTHROPIC_API_KEY": "secret",
            "UNLISTED": "drop",
        }
    ) == {"PATH": "/bin", "EXTRA_ALLOWED": "ok"}
    assert boundary.check_network("https://api.example.com").allow is True
    assert boundary.check_network("https://example.com").allow is False

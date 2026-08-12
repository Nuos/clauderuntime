from __future__ import annotations

import sys

from src.execution import (
    ExecutionBoundary,
    NoSandboxBackend,
    SandboxPolicy,
    SandboxRequest,
    current_sandbox_platform,
    sandbox_policy_from_settings,
)
from src.settings.types import SettingsSchema


def test_current_sandbox_platform_uses_documented_tokens(monkeypatch):
    monkeypatch.setattr(sys, "platform", "darwin")
    assert current_sandbox_platform() == "macos"

    monkeypatch.setattr(sys, "platform", "win32")
    assert current_sandbox_platform() == "windows"

    monkeypatch.setattr(sys, "platform", "linux")
    assert current_sandbox_platform() == "linux"


def test_no_sandbox_backend_reports_available_without_isolation():
    capability = NoSandboxBackend().capability(platform="macos")

    assert capability.backend_name == "no-sandbox"
    assert capability.platform == "macos"
    assert capability.available is True
    assert capability.provides_isolation is False
    assert "does not provide isolation" in capability.reason


def test_no_sandbox_backend_prepares_unsandboxed_invocation(tmp_path):
    request = SandboxRequest(argv=("echo", "ok"), cwd=tmp_path)

    invocation = NoSandboxBackend().prepare(request)

    assert invocation.allowed is True
    assert invocation.isolated is False
    assert invocation.request is request
    assert invocation.backend_name == "no-sandbox"


def test_no_sandbox_backend_refuses_when_isolation_is_required(tmp_path):
    request = SandboxRequest(argv=("echo", "ok"), cwd=tmp_path)
    policy = SandboxPolicy(require_isolation=True, allow_unsandboxed=False)

    invocation = NoSandboxBackend().prepare(request, policy)
    result = NoSandboxBackend().run(invocation)

    assert invocation.allowed is False
    assert "isolation required" in invocation.reason
    assert result.exit_code == 126
    assert "isolation required" in result.stderr


def test_no_sandbox_backend_can_run_local_process_when_allowed(tmp_path):
    request = SandboxRequest(
        argv=(sys.executable, "-c", "print('sandbox-backend-ok')"),
        cwd=tmp_path,
        timeout_s=5,
    )
    invocation = NoSandboxBackend().prepare(request)

    result = NoSandboxBackend().run(invocation)

    assert result.exit_code == 0
    assert result.stdout.strip() == "sandbox-backend-ok"
    assert result.stderr == ""
    assert result.timed_out is False


def test_sandbox_policy_from_settings_respects_enabled_platforms():
    settings = SettingsSchema.from_dict(
        {
            "sandbox": {
                "enabled": True,
                "failIfUnavailable": True,
                "enabledPlatforms": ["macos"],
            }
        }
    )

    linux_policy = sandbox_policy_from_settings(settings, platform="linux")
    macos_policy = sandbox_policy_from_settings(settings, platform="macos")

    assert linux_policy.require_isolation is False
    assert linux_policy.allow_unsandboxed is True
    assert "disabled on platform linux" in linux_policy.reason
    assert macos_policy.require_isolation is True
    assert macos_policy.allow_unsandboxed is False


def test_sandbox_policy_from_settings_honors_allow_unsandboxed_commands():
    settings = SettingsSchema.from_dict(
        {
            "sandbox": {
                "enabled": True,
                "allowUnsandboxedCommands": False,
            }
        }
    )

    policy = sandbox_policy_from_settings(settings, platform="macos")

    assert policy.require_isolation is False
    assert policy.allow_unsandboxed is False


def test_execution_boundary_exposes_sandbox_backend(tmp_path):
    boundary = ExecutionBoundary()
    request = SandboxRequest(
        argv=(sys.executable, "-c", "print('boundary')"),
        cwd=tmp_path,
    )

    invocation = boundary.prepare_sandbox(request)
    result = boundary.run_sandbox(invocation)

    assert invocation.backend_name == "no-sandbox"
    assert invocation.isolated is False
    assert result.exit_code == 0
    assert result.stdout.strip() == "boundary"

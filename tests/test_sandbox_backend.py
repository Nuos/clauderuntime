from __future__ import annotations

import sys
import socket
from unittest.mock import patch

from src.execution import (
    ExecutionBoundary,
    MacOSSandboxBackend,
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


def test_no_sandbox_backend_timeout_terminates_process_tree(tmp_path):
    request = SandboxRequest(
        argv=(sys.executable, "-c", "import time; time.sleep(30)"),
        cwd=tmp_path,
        timeout_s=0.05,
    )

    result = NoSandboxBackend().run(NoSandboxBackend().prepare(request))

    assert result.exit_code == 124
    assert result.timed_out is True
    assert "process tree" in result.termination_reason


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


def test_sandbox_policy_from_settings_parses_filesystem_rules(tmp_path):
    settings = SettingsSchema.from_dict(
        {
            "sandbox": {
                "enabled": True,
                "allowReadPaths": [str(tmp_path / "read")],
                "denyReadPaths": [str(tmp_path / "secret")],
                "allowWritePaths": [str(tmp_path / "out")],
                "denyWritePaths": [str(tmp_path / "blocked")],
            }
        }
    )

    policy = sandbox_policy_from_settings(settings, platform="macos")

    assert policy.allow_read_paths == (tmp_path / "read",)
    assert policy.deny_read_paths == (tmp_path / "secret",)
    assert policy.allow_write_paths == (tmp_path / "out",)
    assert policy.deny_write_paths == (tmp_path / "blocked",)


def test_sandbox_policy_from_settings_parses_network_allow_all():
    settings = SettingsSchema.from_dict(
        {"sandbox": {"enabled": True, "network": {"allowAll": True, "allowedDomains": ["example.com"]}}}
    )

    policy = sandbox_policy_from_settings(settings, platform="macos")

    assert policy.allow_all_network is True
    assert policy.allowed_network_hosts == ("example.com",)


def test_execution_boundary_exposes_sandbox_backend(tmp_path):
    boundary = ExecutionBoundary()
    request = SandboxRequest(
        argv=(sys.executable, "-c", "print('boundary')"),
        cwd=tmp_path,
    )

    invocation = boundary.prepare_sandbox(request)
    result = boundary.run_sandbox(invocation)

    assert invocation.backend_name in {"no-sandbox", "macos-seatbelt"}
    if invocation.isolated:
        assert result.exit_code == 0
        assert result.stdout.strip() == "boundary"
    else:
        assert result.exit_code == 126


def test_macos_backend_marks_probe_failure_unavailable(tmp_path):
    backend = MacOSSandboxBackend(executable="/does/not/exist")
    with patch("src.execution.sandbox.current_sandbox_platform", return_value="macos"):
        capability = backend.capability()
        invocation = backend.prepare(SandboxRequest(argv=("echo", "no"), cwd=tmp_path))

    assert capability.available is False
    assert capability.provides_isolation is False
    assert invocation.allowed is True
    assert invocation.isolated is False


def test_macos_profile_denies_network_and_external_writes(tmp_path):
    profile = MacOSSandboxBackend._profile(SandboxRequest(argv=("echo", "ok"), cwd=tmp_path))

    assert "(deny default)" in profile
    assert "network" not in profile
    assert str(tmp_path.resolve()) in profile


def test_macos_profile_translates_filesystem_rules(tmp_path):
    policy = SandboxPolicy(
        allow_read_paths=(tmp_path / "read",),
        deny_read_paths=(tmp_path / "secret",),
        allow_write_paths=(tmp_path / "out",),
        deny_write_paths=(tmp_path / "blocked",),
    )

    profile = MacOSSandboxBackend._profile(
        SandboxRequest(argv=("echo", "ok"), cwd=tmp_path), policy,
    )

    assert f'(allow file-read* (subpath "{tmp_path / "read"}"))' in profile
    assert f'(deny file-read* (subpath "{tmp_path / "secret"}"))' in profile
    assert f'(allow file-write* (subpath "{tmp_path / "out"}"))' in profile
    assert f'(deny file-write* (subpath "{tmp_path / "blocked"}"))' in profile


def test_macos_profile_allows_network_only_when_explicitly_enabled(tmp_path):
    request = SandboxRequest(argv=("echo", "ok"), cwd=tmp_path)

    denied_profile = MacOSSandboxBackend._profile(request, SandboxPolicy())
    allowed_profile = MacOSSandboxBackend._profile(
        request, SandboxPolicy(allow_all_network=True),
    )

    assert "(allow network*)" not in denied_profile
    assert "(allow network*)" in allowed_profile


def test_macos_backend_denies_then_allows_network_by_policy(tmp_path):
    backend = MacOSSandboxBackend()
    if not backend.capability().provides_isolation:
        return
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen(2)
    host, port = listener.getsockname()
    command = (
        "import socket; "
        f"socket.create_connection(({host!r}, {port}), timeout=2).close()"
    )
    request = SandboxRequest(
        argv=(sys.executable, "-c", command), cwd=tmp_path, timeout_s=5,
    )
    try:
        denied = backend.run(backend.prepare(request, SandboxPolicy()))
        allowed = backend.run(
            backend.prepare(request, SandboxPolicy(allow_all_network=True)),
        )
        assert denied.exit_code != 0
        assert allowed.exit_code == 0
    finally:
        listener.close()


def test_macos_backend_blocks_write_outside_request_cwd(tmp_path):
    backend = MacOSSandboxBackend()
    capability = backend.capability()
    if not capability.provides_isolation:
        return

    outside = tmp_path.parent / "outside-sandbox-write.txt"
    request = SandboxRequest(
        argv=(sys.executable, "-c", f"open({str(outside)!r}, 'w').write('blocked')"),
        cwd=tmp_path,
        timeout_s=5,
    )
    result = backend.run(backend.prepare(request))

    assert result.exit_code != 0
    assert not outside.exists()


def test_macos_backend_honors_deny_write_path_inside_request_cwd(tmp_path):
    backend = MacOSSandboxBackend()
    if not backend.capability().provides_isolation:
        return

    blocked = tmp_path / "blocked.txt"
    policy = SandboxPolicy(deny_write_paths=(blocked,))
    request = SandboxRequest(
        argv=(sys.executable, "-c", f"open({str(blocked)!r}, 'w').write('blocked')"),
        cwd=tmp_path,
        timeout_s=5,
    )

    result = backend.run(backend.prepare(request, policy))

    assert result.exit_code != 0
    assert not blocked.exists()


def test_macos_backend_honors_deny_read_path_inside_request_cwd(tmp_path):
    backend = MacOSSandboxBackend()
    if not backend.capability().provides_isolation:
        return

    secret = tmp_path / "secret.txt"
    secret.write_text("not-visible")
    policy = SandboxPolicy(deny_read_paths=(secret,))
    request = SandboxRequest(
        argv=(sys.executable, "-c", f"print(open({str(secret)!r}).read())"),
        cwd=tmp_path,
        timeout_s=5,
    )

    result = backend.run(backend.prepare(request, policy))

    assert result.exit_code != 0
    assert "not-visible" not in result.stdout

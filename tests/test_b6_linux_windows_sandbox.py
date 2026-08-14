"""B6 P1 — Linux (bubblewrap) / Windows (Job Object) minimum isolation.

Tests the decision layer on this (macOS) host: honest capability reporting per
platform, fail-closed behavior under ``require_isolation``, and the argv-wrap
shape the Bash path consumes. The OS-specific spawn paths (bwrap on Linux,
Job Object on Windows) cannot execute here; their structure is pinned and the
registry discloses the platform status truthfully.
"""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import src.execution.sandbox as sandbox_mod
from src.execution.sandbox import (
    LinuxSandboxBackend,
    NoSandboxBackend,
    SandboxPolicy,
    SandboxRequest,
    WindowsSandboxBackend,
    default_sandbox_backend,
    sandbox_command_argv,
)


def _invocation(backend, *, require_isolation: bool, allow_unsandboxed: bool = True):
    policy = SandboxPolicy(
        require_isolation=require_isolation,
        allow_unsandboxed=allow_unsandboxed,
    )
    request = SandboxRequest(argv=("echo", "hi"), cwd=Path("/work"))
    return backend.prepare(request, policy)


# ---------------------------------------------------------------------------
# default backend selection
# ---------------------------------------------------------------------------


def test_default_backend_matches_platform(monkeypatch) -> None:
    monkeypatch.setattr(sandbox_mod, "current_sandbox_platform", lambda: "macos")
    assert isinstance(default_sandbox_backend(), sandbox_mod.MacOSSandboxBackend)
    monkeypatch.setattr(sandbox_mod, "current_sandbox_platform", lambda: "linux")
    assert isinstance(default_sandbox_backend(), LinuxSandboxBackend)
    monkeypatch.setattr(sandbox_mod, "current_sandbox_platform", lambda: "windows")
    assert isinstance(default_sandbox_backend(), WindowsSandboxBackend)
    monkeypatch.setattr(sandbox_mod, "current_sandbox_platform", lambda: "other")
    assert isinstance(default_sandbox_backend(), NoSandboxBackend)


# ---------------------------------------------------------------------------
# Linux bubblewrap backend
# ---------------------------------------------------------------------------


def test_linux_capability_unavailable_on_macos() -> None:
    cap = LinuxSandboxBackend().capability()
    assert cap.available is False
    assert cap.provides_isolation is False
    assert "linux" in cap.reason.lower()


def test_linux_prepare_fails_closed_under_require_isolation(monkeypatch) -> None:
    backend = LinuxSandboxBackend()
    monkeypatch.setattr(backend, "_probe", lambda: (False, "no bwrap on this host"))
    inv = _invocation(backend, require_isolation=True)
    assert inv.allowed is False
    assert inv.isolated is False


def test_linux_prepare_allows_unsandboxed_when_not_required(monkeypatch) -> None:
    backend = LinuxSandboxBackend()
    monkeypatch.setattr(backend, "_probe", lambda: (False, "no bwrap on this host"))
    inv = _invocation(backend, require_isolation=False)
    assert inv.allowed is True
    assert inv.isolated is False


def test_linux_prepare_isolates_when_backend_available(monkeypatch) -> None:
    backend = LinuxSandboxBackend()
    monkeypatch.setattr(backend, "_probe", lambda: (True, "bwrap available"))
    inv = _invocation(backend, require_isolation=True)
    assert inv.allowed is True
    assert inv.isolated is True


def test_linux_wrap_argv_shape() -> None:
    request = SandboxRequest(argv=("sh", "-c", "true"), cwd=Path("/work"))
    argv = LinuxSandboxBackend._wrap_argv(request)
    assert argv[0] == "bwrap"
    assert "--die-with-parent" in argv
    assert "--ro-bind" in argv and "/" in argv
    assert "--bind" in argv and "/work" in argv
    assert "--unshare-net" in argv  # network denied by default
    assert argv[-3:] == ("sh", "-c", "true")


def test_linux_wrap_argv_allows_network_when_requested() -> None:
    request = SandboxRequest(argv=("curl", "x"), cwd=Path("/work"))
    policy = SandboxPolicy(allow_all_network=True)
    argv = LinuxSandboxBackend._wrap_argv(request, policy)
    assert "--unshare-net" not in argv


def test_linux_sandbox_command_argv_wraps_when_isolated(monkeypatch) -> None:
    backend = LinuxSandboxBackend()
    monkeypatch.setattr(backend, "_probe", lambda: (True, "bwrap available"))
    request = SandboxRequest(argv=("echo", "hi"), cwd=Path("/work"))
    inv = backend.prepare(request, SandboxPolicy(require_isolation=True))
    argv = sandbox_command_argv(inv)
    assert argv[0] == "bwrap"


def test_linux_run_refuses_when_not_isolated(monkeypatch) -> None:
    backend = LinuxSandboxBackend()
    monkeypatch.setattr(backend, "_probe", lambda: (False, "no bwrap"))
    request = SandboxRequest(argv=("echo", "hi"), cwd=Path("/work"))
    inv = backend.prepare(request, SandboxPolicy(require_isolation=True))
    result = backend.run(inv)
    assert result.exit_code == 126


# ---------------------------------------------------------------------------
# Windows Job Object backend
# ---------------------------------------------------------------------------


def test_windows_capability_unavailable_on_macos() -> None:
    cap = WindowsSandboxBackend().capability()
    assert cap.available is False
    assert cap.provides_isolation is False
    assert "windows" in cap.reason.lower()


def test_windows_prepare_fails_closed_under_require_isolation() -> None:
    backend = WindowsSandboxBackend()
    inv = _invocation(backend, require_isolation=True)
    assert inv.allowed is False
    assert inv.isolated is False


def test_windows_prepare_allows_unsandboxed_when_not_required() -> None:
    backend = WindowsSandboxBackend()
    inv = _invocation(backend, require_isolation=False)
    assert inv.allowed is True
    assert inv.isolated is False


def test_windows_sandbox_command_argv_uses_job_launcher(monkeypatch) -> None:
    backend = WindowsSandboxBackend()
    # Force the isolated branch so we pin the argv-wrap shape (the launcher is
    # what attaches the Job Object at spawn time on win32).
    monkeypatch.setattr(backend, "_probe", lambda: (True, "job api available"))
    request = SandboxRequest(argv=("powershell", "-c", "true"), cwd=Path("C:\\work"))
    inv = backend.prepare(request, SandboxPolicy(require_isolation=True))
    assert inv.isolated is True
    argv = sandbox_command_argv(inv)
    assert argv[0] == sys.executable
    assert "-m" in argv
    assert "src.execution.win_job_launcher" in argv
    assert argv[-4:] == ("--", "powershell", "-c", "true")


def test_windows_launcher_refuses_on_non_windows() -> None:
    from src.execution.win_job_launcher import run_argv_in_job

    result = run_argv_in_job(("echo", "hi"), cwd="/work")
    assert result.exit_code == 126
    assert "win32" in result.stderr


def test_windows_job_argv_shape() -> None:
    from src.execution.win_job_launcher import _job_object_argv

    argv = _job_object_argv(("cmd", "/c", "dir"))
    assert argv[0] == sys.executable
    assert "src.execution.win_job_launcher" in argv
    assert argv[-4:] == ("--", "cmd", "/c", "dir")

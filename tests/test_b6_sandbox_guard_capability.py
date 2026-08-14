"""B6 P0 — sandbox guard must be capability-aware.

The macOS Seatbelt backend provides real isolation and is wired into the Bash
path. The guard must therefore NOT hard-gate or claim "unsandboxed" when the
platform backend actually provides isolation — otherwise ``failIfUnavailable``
makes the working sandbox unreachable, and ``enabled`` alone tells the user
commands run unsandboxed while they are wrapped by ``sandbox-exec`` (a stale
"no enforcement" claim, B6: truthful provides_isolation).

Only when the platform backend cannot provide isolation may the guard warn
(``enabled``, not required) or refuse (``enabled`` + ``failIfUnavailable``).
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.permissions import sandbox_guard
from src.permissions.sandbox_guard import (
    _warned_once,
    sandbox_hard_gate_error,
    sandbox_unsandboxed_warning,
)
from src.tool_system.tools.bash.bash_tool import bash_command_safety_guard


@pytest.fixture(autouse=True)
def _reset_warned_once() -> None:
    """The warn-once module global must not leak across tests."""
    sandbox_guard._warned_once = False
    yield
    sandbox_guard._warned_once = False


def _settings(enabled: bool = True, fail_if_unavailable: bool = False) -> SimpleNamespace:
    return SimpleNamespace(
        sandbox=SimpleNamespace(
            enabled=enabled,
            fail_if_unavailable=fail_if_unavailable,
            enabled_platforms=[],
        )
    )


def _fake_backend(provides_isolation: bool) -> object:
    capability = SimpleNamespace(provides_isolation=provides_isolation)
    return SimpleNamespace(capability=lambda: capability)


def test_no_gate_nor_warning_when_backend_provides_isolation(monkeypatch) -> None:
    """macOS with a working Seatbelt probe: requirement is satisfiable."""
    monkeypatch.setattr(
        sandbox_guard, "_enforcement_available", lambda: True,
    )
    assert sandbox_hard_gate_error(_settings(enabled=True, fail_if_unavailable=True)) is None
    assert sandbox_unsandboxed_warning(_settings(enabled=True)) is None


def test_hard_gate_when_enforcement_unavailable_and_required(monkeypatch) -> None:
    """Linux/Windows no-isolation backend + failIfUnavailable → refuse."""
    monkeypatch.setattr(
        sandbox_guard, "_enforcement_available", lambda: False,
    )
    gate = sandbox_hard_gate_error(_settings(enabled=True, fail_if_unavailable=True))
    assert gate is not None
    assert "failIfUnavailable" in gate or "fail_if_unavailable" in gate


def test_warning_when_enforcement_unavailable_and_not_required(monkeypatch) -> None:
    monkeypatch.setattr(
        sandbox_guard, "_enforcement_available", lambda: False,
    )
    warning = sandbox_unsandboxed_warning(_settings(enabled=True))
    assert warning is not None
    assert "UNSANDBOXED" in warning


def test_no_warning_when_sandbox_disabled(monkeypatch) -> None:
    monkeypatch.setattr(
        sandbox_guard, "_enforcement_available", lambda: False,
    )
    assert sandbox_unsandboxed_warning(_settings(enabled=False)) is None
    assert sandbox_hard_gate_error(_settings(enabled=False)) is None


def test_enforcement_available_consults_real_backend(monkeypatch) -> None:
    """``_enforcement_available`` reads the real default backend capability."""
    import src.execution.sandbox as sandbox_mod

    monkeypatch.setattr(
        sandbox_mod, "default_sandbox_backend", lambda: _fake_backend(True),
    )
    assert sandbox_guard._enforcement_available() is True

    monkeypatch.setattr(
        sandbox_mod, "default_sandbox_backend", lambda: _fake_backend(False),
    )
    assert sandbox_guard._enforcement_available() is False


def test_bash_guard_allows_sandboxed_run_when_backend_available(monkeypatch) -> None:
    """The CLI-path backstop must NOT refuse when enforcement exists."""
    monkeypatch.setattr(
        sandbox_guard, "_enforcement_available", lambda: True,
    )
    import src.settings.settings as settings_mod
    import src.tool_system.tools.bash.bash_tool as bash_tool

    monkeypatch.setattr(
        settings_mod, "get_settings", lambda: _settings(enabled=True, fail_if_unavailable=True),
    )
    # A benign command must pass the guard (no ToolPermissionError).
    bash_command_safety_guard("echo hi")  # must not raise


def test_bash_guard_refuses_when_enforcement_unavailable_and_required(monkeypatch) -> None:
    monkeypatch.setattr(
        sandbox_guard, "_enforcement_available", lambda: False,
    )
    import src.settings.settings as settings_mod
    import src.tool_system.tools.bash.bash_tool as bash_tool

    monkeypatch.setattr(
        settings_mod, "get_settings", lambda: _settings(enabled=True, fail_if_unavailable=True),
    )
    with pytest.raises(bash_tool.ToolPermissionError):
        bash_command_safety_guard("echo hi")

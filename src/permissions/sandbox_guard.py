"""Sandbox availability guard (C8 — the silent-unsandboxed footgun).

REF-DIFF:
REF: entrypoints/sandboxTypes.ts:96-103 — enabled → warn; enabled+failIfUnavailable → refuse to start.
PY: src/permissions/sandbox_guard.py — capability-aware: when the platform
    backend really provides isolation (macOS Seatbelt / Linux bwrap), the
    requirement is satisfiable → no gate, no warning; otherwise warn (not
    required) or hard-gate (required).
DIFF: the guard consults the actual backend instead of assuming "no enforcement".
WHY: SAFETY_STRENGTHENING + RECOVERED_SOURCE_GAP (old guard predated the real backends).
USER-IMPACT: LOW; truthful messaging and a working hard-gate path on macOS.
SAFETY-IMPACT: NONE (fail-closed preserved on platforms without enforcement).
STATUS: FUNCTIONAL_ADAPTATION.

The port implements REAL sandbox enforcement on macOS (``sandbox-exec`` /
Seatbelt via ``src.execution.sandbox.MacOSSandboxBackend``) and falls back to
an explicit no-isolation backend elsewhere. The guard below decides what a
``sandbox.enabled`` setting means *based on the actual backend capability*:

* Backend provides isolation (macOS probe passes) → commands are wrapped by the
  execution boundary, so ``failIfUnavailable`` is satisfiable: no hard gate, no
  "unsandboxed" warning. The claim must never be "this build has no sandbox"
  when enforcement exists (B6: truthful ``provides_isolation``).
* Backend does NOT provide isolation (Linux/Windows/unsupported) → map onto
  Claude Code's documented sandbox-unavailable path
  (``entrypoints/sandboxTypes.ts:96-103``): ``failIfUnavailable: true``  →
  refuse to start (managed-settings HARD GATE — never silently run
  unsandboxed), ``failIfUnavailable: false`` (default) → warn once and run
  unsandboxed.

The hard gate is a REFUSE-TO-START, not a per-command refusal — Claude Code
exits at the entrypoints ("refusing to start without a working sandbox"). The
port enforces it in ``agent_server._build_runtime`` (session init_error →
MCP + hooks never run) AND in ``_handle_control_request`` (a refused session
rejects ``bg_run``/``bg_agent`` and every other control request except
``interrupt``) AND at ``_bash_call`` as a CLI-path backstop. So the "hard gate"
is truthful: nothing runs, not just Bash.

SCOPE — two distinct mechanisms (critic C8):

* The WARNING path (``enabled`` and not ``failIfUnavailable``) is
  BashTool-scoped, like TS ``shouldUseSandbox`` (called only from
  ``bashPermissions.ts``): it warns once and runs the command unsandboxed.
  Hooks/MCP/`/bg` running unsandboxed here is faithful — TS doesn't sandbox
  those either.
* The HARD GATE (``enabled`` + ``failIfUnavailable``) applies only when the
  current platform backend cannot provide isolation.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

_UNSANDBOXED_WARNING = (
    "settings.sandbox.enabled is true, but no sandbox enforcement is available "
    "on this platform — commands run UNSANDBOXED. Set "
    "sandbox.failIfUnavailable=true to make this a hard startup error instead, "
    "or unset sandbox.enabled to silence this warning."
)

_HARD_GATE_ERROR = (
    "settings.sandbox.enabled and sandbox.failIfUnavailable are both true, but "
    "no sandbox enforcement is available on this platform, so the sandbox "
    "cannot start. Refusing to run unsandboxed (the managed-settings hard "
    "gate). Unset sandbox.failIfUnavailable to fall back to a warning + "
    "unsandboxed execution."
)


def _current_platform() -> str:
    """Map sys.platform to TS's platform tokens (macos/linux/windows)."""
    import sys

    return {"darwin": "macos", "win32": "windows"}.get(
        sys.platform, "linux" if sys.platform.startswith("linux") else sys.platform
    )


def _enforcement_available() -> bool:
    """True when the current platform's default sandbox backend actually
    provides isolation (e.g. the macOS Seatbelt probe passes).

    The guard must consult the real backend instead of assuming "no
    enforcement": ``src.execution.sandbox`` implements Seatbelt on macOS, so a
    hard gate or "commands run UNSANDBOXED" warning there would be a lie and
    would block a working sandbox. Failure to query the backend is treated as
    unavailable (fail closed toward the warning/gate).
    """
    try:
        from src.execution.sandbox import default_sandbox_backend

        return bool(default_sandbox_backend().capability().provides_isolation)
    except Exception:  # noqa: BLE001 — the guard must never crash the tool
        return False


def _sandbox(settings: Any) -> Any | None:
    """The sandbox settings, or None when sandbox does not apply on this
    platform (TS enabledPlatforms: on a platform not listed, sandbox is
    treated as disabled — no gate, no warning)."""
    sb = getattr(settings, "sandbox", None)
    if sb is None:
        return None
    platforms = getattr(sb, "enabled_platforms", None) or []
    if platforms and _current_platform() not in platforms:
        return None
    return sb


def is_sandbox_requested(settings: Any) -> bool:
    sb = _sandbox(settings)
    return bool(sb is not None and getattr(sb, "enabled", False))


def sandbox_hard_gate_error(settings: Any) -> str | None:
    """The hard-gate message when the user REQUIRES a sandbox
    (``enabled`` + ``failIfUnavailable``) that the current platform cannot
    provide, else ``None``. Callers must refuse to proceed when this is
    non-None. When the backend provides real isolation the requirement is
    satisfiable, so there is no gate."""
    sb = _sandbox(settings)
    if (
        sb is not None
        and getattr(sb, "enabled", False)
        and getattr(sb, "fail_if_unavailable", False)
        and not _enforcement_available()
    ):
        return _HARD_GATE_ERROR
    return None


def sandbox_unsandboxed_warning(settings: Any) -> str | None:
    """The warning message when the user ASKED for a sandbox but the current
    platform cannot provide it and it is NOT required (``enabled`` + not
    ``failIfUnavailable``), else ``None``."""
    sb = _sandbox(settings)
    if (
        sb is not None
        and getattr(sb, "enabled", False)
        and not getattr(sb, "fail_if_unavailable", False)
        and not _enforcement_available()
    ):
        return _UNSANDBOXED_WARNING
    return None


_warned_once = False


def warn_if_unsandboxed_once(settings: Any) -> None:
    """Emit the unsandboxed warning at most once per process (so bash-per-call
    wiring doesn't spam). The hard-gate case is handled separately by callers
    that must refuse."""
    global _warned_once
    if _warned_once:
        return
    msg = sandbox_unsandboxed_warning(settings)
    if msg:
        logger.warning("[sandbox] %s", msg)
        _warned_once = True

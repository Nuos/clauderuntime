from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Protocol, Sequence


def current_sandbox_platform() -> str:
    """Return the execution platform token used by sandbox settings."""
    import sys

    return {"darwin": "macos", "win32": "windows"}.get(
        sys.platform,
        "linux" if sys.platform.startswith("linux") else sys.platform,
    )


@dataclass(frozen=True)
class SandboxCapability:
    backend_name: str
    platform: str
    available: bool
    provides_isolation: bool
    reason: str


@dataclass(frozen=True)
class SandboxPolicy:
    require_isolation: bool = False
    allow_unsandboxed: bool = True
    reason: str = "sandbox policy: default unsandboxed execution allowed"


@dataclass(frozen=True)
class SandboxRequest:
    argv: tuple[str, ...]
    cwd: Path
    env: Mapping[str, str] | None = None
    timeout_s: int | float | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class SandboxInvocation:
    request: SandboxRequest
    backend_name: str
    capability: SandboxCapability
    isolated: bool
    allowed: bool
    reason: str


@dataclass(frozen=True)
class SandboxExecutionResult:
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False


class SandboxBackend(Protocol):
    name: str

    def capability(self, *, platform: str | None = None) -> SandboxCapability: ...

    def prepare(
        self,
        request: SandboxRequest,
        policy: SandboxPolicy | None = None,
    ) -> SandboxInvocation: ...

    def run(self, invocation: SandboxInvocation) -> SandboxExecutionResult: ...


@dataclass(frozen=True)
class NoSandboxBackend:
    """Explicit local unsandboxed backend for C4.

    This backend is intentionally available everywhere but reports
    ``provides_isolation=False``. It gives the execution layer a real backend
    contract without pretending that the port has native sandbox enforcement.
    """

    name: str = "no-sandbox"

    def capability(self, *, platform: str | None = None) -> SandboxCapability:
        actual_platform = platform or current_sandbox_platform()
        return SandboxCapability(
            backend_name=self.name,
            platform=actual_platform,
            available=True,
            provides_isolation=False,
            reason="no-sandbox backend is available but does not provide isolation",
        )

    def prepare(
        self,
        request: SandboxRequest,
        policy: SandboxPolicy | None = None,
    ) -> SandboxInvocation:
        effective_policy = policy or SandboxPolicy()
        capability = self.capability()
        if effective_policy.require_isolation and not capability.provides_isolation:
            return SandboxInvocation(
                request=request,
                backend_name=self.name,
                capability=capability,
                isolated=False,
                allowed=False,
                reason=(
                    "sandbox isolation required but no-sandbox backend does not "
                    "provide isolation"
                ),
            )
        if not effective_policy.allow_unsandboxed and not capability.provides_isolation:
            return SandboxInvocation(
                request=request,
                backend_name=self.name,
                capability=capability,
                isolated=False,
                allowed=False,
                reason="unsandboxed execution is not allowed by sandbox policy",
            )
        return SandboxInvocation(
            request=request,
            backend_name=self.name,
            capability=capability,
            isolated=False,
            allowed=True,
            reason=effective_policy.reason,
        )

    def run(self, invocation: SandboxInvocation) -> SandboxExecutionResult:
        if not invocation.allowed:
            return SandboxExecutionResult(
                exit_code=126,
                stderr=invocation.reason,
            )

        import subprocess

        try:
            completed = subprocess.run(
                invocation.request.argv,
                cwd=str(invocation.request.cwd),
                env=dict(invocation.request.env) if invocation.request.env else None,
                timeout=invocation.request.timeout_s,
                capture_output=True,
                text=True,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return SandboxExecutionResult(
                exit_code=124,
                stdout=exc.stdout or "",
                stderr=exc.stderr or "command timed out",
                timed_out=True,
            )
        except FileNotFoundError as exc:
            return SandboxExecutionResult(exit_code=127, stderr=str(exc))
        return SandboxExecutionResult(
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )


def sandbox_policy_from_settings(
    settings: object | None,
    *,
    platform: str | None = None,
) -> SandboxPolicy:
    sandbox = getattr(settings, "sandbox", None)
    if sandbox is None:
        return SandboxPolicy(reason="sandbox policy: settings do not request sandbox")

    actual_platform = platform or current_sandbox_platform()
    enabled_platforms = tuple(getattr(sandbox, "enabled_platforms", None) or ())
    if enabled_platforms and actual_platform not in enabled_platforms:
        return SandboxPolicy(
            reason=(
                "sandbox policy: sandbox disabled on platform "
                f"{actual_platform}"
            )
        )

    if not getattr(sandbox, "enabled", False):
        return SandboxPolicy(reason="sandbox policy: sandbox disabled")

    require_isolation = bool(getattr(sandbox, "fail_if_unavailable", False))
    allow_unsandboxed = bool(
        getattr(sandbox, "allow_unsandboxed_commands", True)
    ) and not require_isolation
    return SandboxPolicy(
        require_isolation=require_isolation,
        allow_unsandboxed=allow_unsandboxed,
        reason="sandbox policy: sandbox requested by settings",
    )


def default_sandbox_backend() -> SandboxBackend:
    return NoSandboxBackend()

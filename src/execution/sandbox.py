from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Protocol, Sequence

from src.utils.shell_platform import kill_process_tree, popen_tree_kwargs


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
    allow_read_paths: tuple[Path, ...] = ()
    deny_read_paths: tuple[Path, ...] = ()
    allow_write_paths: tuple[Path, ...] = ()
    deny_write_paths: tuple[Path, ...] = ()
    allow_all_network: bool = False
    allowed_network_hosts: tuple[str, ...] = ()


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
    policy: SandboxPolicy = field(default_factory=SandboxPolicy)


@dataclass(frozen=True)
class SandboxExecutionResult:
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False
    termination_reason: str = ""


def _text(value: str | bytes | None) -> str:
    """统一不同 Python 和操作系统下的子进程输出格式。"""
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode(errors="replace")
    return value


def run_process_tree(request: SandboxRequest) -> SandboxExecutionResult:
    """在独立进程组中执行命令，并对超时退出设置明确上限。

    这是沙箱后端共用的子进程生命周期入口，但不自行宣称命令已经隔离；隔离结论由
    ``SandboxBackend.prepare`` 给出。命令超时后先回收输出并终止整棵进程树，短暂等待
    后仍未退出则强制结束，避免后台孙进程脱离监管后继续修改工作区。
    """
    import subprocess

    try:
        process = subprocess.Popen(
            request.argv,
            cwd=str(request.cwd),
            env=dict(request.env) if request.env else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            **popen_tree_kwargs(),
        )
    except FileNotFoundError as exc:
        return SandboxExecutionResult(exit_code=127, stderr=str(exc))

    try:
        stdout, stderr = process.communicate(timeout=request.timeout_s)
        return SandboxExecutionResult(
            exit_code=process.returncode or 0,
            stdout=_text(stdout),
            stderr=_text(stderr),
        )
    except subprocess.TimeoutExpired as exc:
        # 终止信号必须覆盖整棵进程树，不能只结束工具最初启动的 shell，否则后台子进程
        # 仍可能在调用方收到超时结果后继续执行生产任务。
        kill_process_tree(process.pid, force=False)
        try:
            stdout, stderr = process.communicate(timeout=0.5)
            termination_reason = "timeout: terminated process tree"
        except subprocess.TimeoutExpired:
            kill_process_tree(process.pid, force=True)
            stdout, stderr = process.communicate()
            termination_reason = "timeout: killed process tree after grace period"
        return SandboxExecutionResult(
            exit_code=124,
            stdout=_text(stdout) or _text(exc.stdout),
            stderr=_text(stderr) or _text(exc.stderr) or "command timed out",
            timed_out=True,
            termination_reason=termination_reason,
        )


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

        return run_process_tree(invocation.request)


@dataclass(frozen=True)
class MacOSSandboxBackend:
    """使用 Seatbelt 实现 macOS 本地命令隔离。

    运行时通过一次无副作用的真实启动判断能力，不能仅因系统存在 ``sandbox-exec``
    文件就认定隔离可用；受管终端或 CI 可能保留程序但禁止应用沙箱规则。探测失败时
    必须报告无隔离能力，并在业务要求强制隔离时拒绝执行。

    当前规则只允许向任务工作目录和系统临时目录写入，默认禁止网络。为保证解释器、
    动态库和目标程序能够启动，读取能力仍较宽；完整读路径约束继续由 B4-D01 跟踪。
    """

    name: str = "macos-seatbelt"
    executable: str = "/usr/bin/sandbox-exec"

    def _probe(self) -> tuple[bool, str]:
        import os
        import subprocess

        if current_sandbox_platform() != "macos":
            return False, "macOS Seatbelt backend is only supported on macos"
        if not os.path.isfile(self.executable) or not os.access(self.executable, os.X_OK):
            return False, f"sandbox executable is unavailable: {self.executable}"
        try:
            probe = subprocess.run(
                [self.executable, "-p", "(version 1) (allow default)", "/usr/bin/true"],
                capture_output=True,
                text=True,
                timeout=2,
                check=False,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            return False, f"sandbox capability probe failed: {exc}"
        if probe.returncode != 0:
            detail = (probe.stderr or probe.stdout).strip() or f"exit {probe.returncode}"
            return False, f"sandbox capability probe failed: {detail}"
        return True, "macOS Seatbelt sandbox is available"

    def capability(self, *, platform: str | None = None) -> SandboxCapability:
        actual_platform = platform or current_sandbox_platform()
        if platform is not None and platform != "macos":
            return SandboxCapability(
                backend_name=self.name,
                platform=actual_platform,
                available=False,
                provides_isolation=False,
                reason="macOS Seatbelt backend is only supported on macos",
            )
        available, reason = self._probe()
        return SandboxCapability(
            backend_name=self.name,
            platform=actual_platform,
            available=available,
            provides_isolation=available,
            reason=reason,
        )

    @staticmethod
    def _profile(request: SandboxRequest, policy: SandboxPolicy | None = None) -> str:
        def quoted(path: Path) -> str:
            return str(path.resolve()).replace("\\", "\\\\").replace('"', '\\"')

        effective_policy = policy or SandboxPolicy()
        writable = quoted(request.cwd)
        read_allows = [f'(allow file-read* (subpath "{quoted(path)}"))' for path in effective_policy.allow_read_paths]
        write_allows = [f'(allow file-write* (subpath "{quoted(path)}"))' for path in effective_policy.allow_write_paths]
        read_denies = [f'(deny file-read* (subpath "{quoted(path)}"))' for path in effective_policy.deny_read_paths]
        write_denies = [f'(deny file-write* (subpath "{quoted(path)}"))' for path in effective_policy.deny_write_paths]
        # Darwin 实际将 ``/tmp`` 映射到 ``/private/tmp``，规则必须使用真实路径。
        clauses = [
            "(version 1)",
            "(deny default)",
            "(allow process*)",
            "(allow file-read*)",
        ]
        if effective_policy.allow_all_network:
            clauses.append("(allow network*)")
        clauses.extend(read_allows)
        clauses.extend(
            (
                f'(allow file-write* (subpath "{writable}"))',
                '(allow file-write* (subpath "/private/tmp"))',
            )
        )
        clauses.extend(write_allows)
        clauses.extend(read_denies)
        clauses.extend(write_denies)
        return "\n".join(clauses)

    def prepare(
        self,
        request: SandboxRequest,
        policy: SandboxPolicy | None = None,
    ) -> SandboxInvocation:
        effective_policy = policy or SandboxPolicy()
        capability = self.capability()
        if not capability.provides_isolation:
            return SandboxInvocation(
                request=request,
                backend_name=self.name,
                capability=capability,
                isolated=False,
                allowed=(
                    effective_policy.allow_unsandboxed
                    and not effective_policy.require_isolation
                ),
                reason=capability.reason,
                policy=effective_policy,
            )
        return SandboxInvocation(
            request=request,
            backend_name=self.name,
            capability=capability,
            isolated=True,
            allowed=True,
            reason=effective_policy.reason,
            policy=effective_policy,
        )

    def run(self, invocation: SandboxInvocation) -> SandboxExecutionResult:
        if not invocation.allowed:
            return SandboxExecutionResult(exit_code=126, stderr=invocation.reason)
        if not invocation.isolated:
            # 已选择沙箱却无法提供真实隔离时直接拒绝，不能悄悄退回普通进程执行。
            return SandboxExecutionResult(exit_code=126, stderr=invocation.reason)
        request = invocation.request
        wrapped = SandboxRequest(
            argv=sandbox_command_argv(invocation, invocation.policy),
            cwd=request.cwd,
            env=request.env,
            timeout_s=request.timeout_s,
            metadata=request.metadata,
        )
        return run_process_tree(wrapped)


def sandbox_command_argv(
    invocation: SandboxInvocation,
    policy: SandboxPolicy | None = None,
) -> tuple[str, ...]:
    """生成隔离启动参数，同时保留原 Bash 进程监管生命周期。"""
    if invocation.isolated and invocation.backend_name == "macos-seatbelt":
        backend = MacOSSandboxBackend()
        return (
            backend.executable,
            "-p",
            backend._profile(invocation.request, policy),
            *invocation.request.argv,
        )
    return invocation.request.argv


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
        allow_read_paths=tuple(Path(path) for path in getattr(sandbox, "allow_read_paths", ()) or ()),
        deny_read_paths=tuple(Path(path) for path in getattr(sandbox, "deny_read_paths", ()) or ()),
        allow_write_paths=tuple(Path(path) for path in getattr(sandbox, "allow_write_paths", ()) or ()),
        deny_write_paths=tuple(Path(path) for path in getattr(sandbox, "deny_write_paths", ()) or ()),
        allow_all_network=bool(getattr(sandbox, "allow_all_network", False)),
        allowed_network_hosts=tuple(getattr(sandbox, "allowed_network_hosts", ()) or ()),
    )


def default_sandbox_backend() -> SandboxBackend:
    if current_sandbox_platform() == "macos":
        return MacOSSandboxBackend()
    return NoSandboxBackend()

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from src.execution import (
    DefaultWorkspaceGuard,
    ExecutionBoundary,
    SandboxPolicy,
    SandboxRequest,
    WorkspaceDecision,
    minimal_execution_boundary,
)
from src.execution.sandbox import NoSandboxBackend
from src.permissions.types import ToolPermissionContext
from src.tool_system.context import ToolContext
from src.tool_system.errors import ToolPermissionError


class StrictWorkspaceGuard(DefaultWorkspaceGuard):
    """Fault-injection guard that refuses permission-layer workspace escape."""

    def check_path(
        self,
        path: Path,
        *,
        roots,
        access: str,
        allow_workspace_escape: bool = False,
    ) -> WorkspaceDecision:
        return super().check_path(
            path,
            roots=roots,
            access=access,
            allow_workspace_escape=False,
        )


def test_exit_gate_c_blocks_workspace_escape_after_permission_misgrant(tmp_path):
    """Permission says bypass, execution boundary still blocks outside root."""
    ctx = ToolContext(
        workspace_root=tmp_path,
        permission_context=ToolPermissionContext(
            mode="bypassPermissions",
            bypass_origin="test:fixture",
            bypass_reason="test fixture",
        ),
        execution_boundary=ExecutionBoundary(workspace_guard=StrictWorkspaceGuard()),
    )

    with pytest.raises(ToolPermissionError, match="outside execution workspace roots"):
        ctx.ensure_allowed_path(tmp_path.parent / "escape.txt")


def test_exit_gate_c_child_process_cannot_observe_stripped_secret(tmp_path):
    boundary = minimal_execution_boundary()
    child_env = boundary.prepare_env(
        {
            "PATH": "/bin",
            "ANTHROPIC_API_KEY": "secret",
            "INPUT_ANTHROPIC_API_KEY": "input-secret",
        }
    )
    request = SandboxRequest(
        argv=(
            sys.executable,
            "-c",
            "import os; print(os.environ.get('ANTHROPIC_API_KEY', 'missing'))",
        ),
        cwd=tmp_path,
        env=child_env,
        timeout_s=5,
    )

    result = boundary.run_sandbox(boundary.prepare_sandbox(request))

    assert result.exit_code == 0
    assert result.stdout.strip() == "missing"
    assert "ANTHROPIC_API_KEY" not in child_env
    assert "INPUT_ANTHROPIC_API_KEY" not in child_env


def test_exit_gate_c_network_escape_denied_after_permission_misgrant():
    boundary = minimal_execution_boundary(network_mode="none")

    decision = boundary.check_network(
        "https://example.com/exfiltrate",
        purpose="fault-injection",
    )

    assert decision.allow is False
    assert decision.mode == "none"
    assert "disabled" in decision.reason


def test_exit_gate_c_allowlist_blocks_unlisted_redirect_target():
    boundary = minimal_execution_boundary(
        network_mode="allowlist",
        allowed_hosts=("api.example.com",),
    )

    first = boundary.check_network(
        "https://api.example.com/start",
        purpose="fault-injection",
    )
    redirected = boundary.check_network(
        "https://evil.example.com/callback",
        purpose="fault-injection",
    )

    assert first.allow is True
    assert redirected.allow is False
    assert redirected.host == "evil.example.com"


def test_exit_gate_c_no_sandbox_backend_refuses_required_isolation(tmp_path):
    boundary = ExecutionBoundary(sandbox_backend=NoSandboxBackend())
    request = SandboxRequest(
        argv=(sys.executable, "-c", "print('should-not-run')"),
        cwd=tmp_path,
    )
    invocation = boundary.prepare_sandbox(
        request,
        SandboxPolicy(require_isolation=True, allow_unsandboxed=False),
    )

    result = boundary.run_sandbox(invocation)

    assert invocation.allowed is False
    assert result.exit_code == 126
    assert "isolation required" in result.stderr

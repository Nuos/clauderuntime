"""B6 P1 — Surface smoke compatibility suite (Wave F7).

Per supported surface the B6 bar is: startup → ordinary answer → one Read →
one permission-requiring action → interrupt → session continue. All surfaces
must enter the shared core and complete the main function; full per-field
trace differentials are explicitly NOT required (FUNCTIONAL_ADAPTATION).

Coverage here:
* **Server surface** — real DirectConnectServer + DirectConnectSessionManager
  over the actual WebSocket protocol (model provider stubbed, no network):
  startup+answer, Read tool round-trip, permission allow, interrupt, and a
  second-turn continue on the same session.
* **CLI surface** — the headless entry (``run_headless``), which is the
  non-interactive CLI's core: startup+answer and a Read tool round-trip.

TUI surface has its own dedicated suite (``ui-tui`` tests); Desktop rides the
server-side gateway exercised by ``tests/server``. Both are disclosed in the
B6 progress doc rather than duplicated here.
"""
from __future__ import annotations

import contextlib
import io
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from src.providers.base import ChatResponse
from src.tool_system.registry import ToolRegistry

from tests.server.test_agent_server_e2e import (
    _TextProvider,
    _assistant_text,
    _running_server,
    _wait_for,
)
from src.server.direct_connect_manager import (
    DirectConnectCallbacks,
    DirectConnectSessionManager,
)
from src.server.direct_connect_session import create_direct_connect_session


pytestmark = pytest.mark.integration


# ─── Server surface ──────────────────────────────────────────────────────────


async def _connect(config) -> tuple[DirectConnectSessionManager, list[dict]]:
    cfg, _ = await create_direct_connect_session(
        server_url=f"http://127.0.0.1:{config.port}", cwd=str(config.workspace)
    )
    received: list[dict] = []
    callbacks = DirectConnectCallbacks(
        on_message=lambda m: received.append(m),
        on_permission_request=lambda req, rid: None,
    )
    client = DirectConnectSessionManager(cfg, callbacks)
    await client.connect()
    return client, received


async def test_server_surface_startup_and_answer(tmp_path) -> None:
    """Startup + ordinary answer through the server surface."""
    async with _running_server(tmp_path, _TextProvider, ToolRegistry([])) as config:
        client, received = await _connect(config)
        try:
            await client.send_message("hello")
            assert await _wait_for(
                lambda: any(m.get("type") == "result" for m in received)
            ), "no server result received"
            result = next(m for m in received if m.get("type") == "result")
            assert result["subtype"] == "success"
            assert result["result"] == "hi back"
            # init envelope proves startup carried the tool schema handshake
            assert any(m.get("type") == "system" for m in received)
        finally:
            await client.disconnect()


#: The Read smoke provider reads this path (set by the test; the provider class
#: is constructed by the patched factory without extra kwargs).
_READ_TARGET: str = ""


class _ReadThenTextProvider:
    """Turn 1: call the real Read tool on ``_READ_TARGET``. Turn 2: final text."""

    def __init__(self, api_key=None, base_url=None, model=None):
        self.model = model or "fake"
        self._turn = 0

    def chat(self, messages, tools=None, **kw):
        self._turn += 1
        if self._turn == 1:
            return ChatResponse(
                content="reading the file",
                model=self.model,
                usage={"input_tokens": 4, "output_tokens": 3},
                finish_reason="tool_use",
                tool_uses=[{"id": "r1", "name": "Read", "input": {"file_path": _READ_TARGET}}],
            )
        return ChatResponse(
            content="the file was read",
            model=self.model,
            usage={"input_tokens": 6, "output_tokens": 4},
            finish_reason="stop",
            tool_uses=None,
        )

    def chat_stream_response(self, *a, **kw):
        raise NotImplementedError


async def test_server_surface_read_tool_round_trip(tmp_path) -> None:
    """One Read through the shared core: tool runs, result reaches the client."""
    from src.tool_system.tools import ReadTool

    global _READ_TARGET
    target = tmp_path / "note.txt"
    target.write_text("surface-read-ok", encoding="utf-8")
    _READ_TARGET = str(target)
    registry = ToolRegistry([ReadTool])

    async with _running_server(tmp_path, _ReadThenTextProvider, registry) as config:
        client, received = await _connect(config)
        try:
            await client.send_message("read the note")
            assert await _wait_for(
                lambda: any(m.get("type") == "result" for m in received)
            ), "no result after Read turn"
            result = next(m for m in received if m.get("type") == "result")
            assert result["result"] == "the file was read"
            # the tool_result envelope carrying the file content reached the client
            assert any(
                m.get("type") == "user" and "surface-read-ok" in str(m)
                for m in received
            ), "Read tool result never reached the client surface"
        finally:
            await client.disconnect()


class _PermThenTextProvider:
    """Turn 1: permission-requiring tool call. Turn 2: final text."""

    def __init__(self, api_key=None, base_url=None, model=None):
        self.model = model or "fake"
        self._turn = 0

    def chat(self, messages, tools=None, **kw):
        self._turn += 1
        if self._turn == 1:
            return ChatResponse(
                content="running the tool",
                model=self.model,
                usage={"input_tokens": 4, "output_tokens": 3},
                finish_reason="tool_use",
                tool_uses=[{"id": "t1", "name": "DoThing", "input": {"x": "1"}}],
            )
        return ChatResponse(
            content="all done",
            model=self.model,
            usage={"input_tokens": 6, "output_tokens": 4},
            finish_reason="stop",
            tool_uses=None,
        )

    def chat_stream_response(self, *a, **kw):
        raise NotImplementedError


def _ask_tool(ran: list):
    from src.permissions.types import PermissionPassthroughResult
    from src.tool_system.build_tool import build_tool
    from src.tool_system.protocol import ToolResult

    return build_tool(
        name="DoThing",
        description="does a thing (asks first)",
        input_schema={"type": "object", "properties": {"x": {"type": "string"}}},
        call=lambda ti, c: ran.append(dict(ti)) or ToolResult(name="DoThing", output={"ok": True}),
        check_permissions=lambda ti, c: PermissionPassthroughResult(),
    )


async def test_server_surface_permission_round_trip(tmp_path) -> None:
    """A permission-requiring action: server asks, client allows, tool runs."""
    ran: list[dict] = []
    async with _running_server(tmp_path, _PermThenTextProvider, ToolRegistry([_ask_tool(ran)])) as config:
        cfg, _ = await create_direct_connect_session(
            server_url=f"http://127.0.0.1:{config.port}", cwd=str(tmp_path)
        )
        received: list[dict] = []
        perms: list[tuple[dict, str]] = []

        async def _on_permission(request: dict, request_id: str) -> None:
            perms.append((request, request_id))
            await client.respond_to_permission_request(
                request_id,
                SimpleNamespace(behavior="allow", updated_input={}, message=""),
            )

        callbacks = DirectConnectCallbacks(
            on_message=lambda m: received.append(m),
            on_permission_request=_on_permission,
        )
        client = DirectConnectSessionManager(cfg, callbacks)
        await client.connect()
        try:
            await client.send_message("do the thing")
            assert await _wait_for(
                lambda: any(m.get("type") == "result" for m in received)
            ), "no result after permission round-trip"
            assert perms, "server never asked can_use_tool"
            assert perms[0][0]["subtype"] == "can_use_tool"
            assert perms[0][0]["tool_name"] == "DoThing"
            assert ran, "tool did not run after allow"
            assert ran[0] == {"x": "1"}
            assert any(_assistant_text(m) == "all done" for m in received if m.get("type") == "assistant")
        finally:
            await client.disconnect()


class _BlockingPermProvider(_PermThenTextProvider):
    """Turn 1 returns a permission-requiring tool call immediately; the ask
    then waits on the client. If the interrupt did NOT release the pending
    ask, the turn would only end at the 30s permission timeout — the test
    asserts it ends far sooner."""

    def __init__(self, api_key=None, base_url=None, model=None):
        super().__init__(api_key=api_key, base_url=base_url, model=model)
        self._turn = 0


async def test_server_surface_interrupt_stops_turn(tmp_path) -> None:
    """Interrupt during a permission prompt releases fast and no tool runs."""
    import asyncio
    import time

    ran: list[dict] = []
    async with _running_server(tmp_path, _BlockingPermProvider, ToolRegistry([_ask_tool(ran)])) as config:
        cfg, _ = await create_direct_connect_session(
            server_url=f"http://127.0.0.1:{config.port}", cwd=str(tmp_path)
        )
        received: list[dict] = []
        perm_asks: list[dict] = []
        callbacks = DirectConnectCallbacks(
            on_message=lambda m: received.append(m),
            on_permission_request=lambda req, rid: perm_asks.append(req),
        )
        client = DirectConnectSessionManager(cfg, callbacks)
        await client.connect()
        try:
            send_task = asyncio.create_task(client.send_message("do it"))
            assert await _wait_for(
                lambda: any(
                    req.get("subtype") == "can_use_tool" for req in perm_asks
                )
            ), "server never asked can_use_tool"
            t0 = time.monotonic()
            await client.send_interrupt()
            result = await asyncio.wait_for(send_task, timeout=8.0)
            elapsed = time.monotonic() - t0
            assert result is not None
            assert elapsed < 5.0, f"interrupt released only after {elapsed:.1f}s"
            assert ran == [], "tool ran despite interrupt"
        finally:
            await client.disconnect()


async def test_server_surface_continue_second_turn(tmp_path) -> None:
    """Session continue: two sequential messages on one session → two results."""
    async with _running_server(tmp_path, _TextProvider, ToolRegistry([])) as config:
        client, received = await _connect(config)
        try:
            await client.send_message("first question")
            assert await _wait_for(
                lambda: len([m for m in received if m.get("type") == "result"]) >= 1
            ), "first turn never completed"
            await client.send_message("second question")
            assert await _wait_for(
                lambda: len([m for m in received if m.get("type") == "result"]) >= 2
            ), "second turn never completed on the same session"
            results = [m for m in received if m.get("type") == "result"]
            assert results[1]["result"] == "hi back"
        finally:
            await client.disconnect()


# ─── CLI surface (headless entry) ────────────────────────────────────────────


def _headless_patches(provider_cls, registry):
    """Patch headless's LOCAL bindings plus the module attributes the
    at-call-time importers (``provider_validation``) read.

    ``headless.py`` imports provider helpers ``from src.providers import ...``
    at module load, so patching ``src.providers.*`` (what the server-side
    ``_patches`` does) never reaches it — the names must be patched on the
    headless module itself. ``provider_validation`` imports at call time, so it
    picks up the ``src.config`` / ``src.providers`` module patches.
    """
    return [
        patch("src.config.get_default_provider", lambda: "anthropic"),
        patch(
            "src.config.get_provider_config",
            lambda n: {"api_key": "x", "default_model": "fake", "base_url": None},
        ),
        patch("src.providers.get_provider_class", lambda n: provider_cls),
        patch("src.providers.provider_requires_api_key", lambda n: False),
        patch("src.providers.resolve_api_key", lambda n, c: "x"),
        patch(
            "src.tool_system.defaults.build_default_registry",
            lambda provider=None: registry,
        ),
        patch(
            "src.entrypoints.headless.get_default_provider", lambda: "anthropic",
        ),
        patch(
            "src.entrypoints.headless.get_provider_config",
            lambda n: {"api_key": "x", "default_model": "fake", "base_url": None},
        ),
        patch("src.entrypoints.headless.get_provider_class", lambda n: provider_cls),
        patch("src.entrypoints.headless.resolve_api_key", lambda n, c: "x"),
        patch(
            "src.entrypoints.headless.build_default_registry",
            lambda provider=None: registry,
        ),
    ]


def _run_headless(tmp_path: Path, provider_cls, registry, prompt: str) -> tuple[int, str]:
    from src.entrypoints.headless import HeadlessOptions, run_headless

    stdout = io.StringIO()
    stderr = io.StringIO()
    options = HeadlessOptions(
        prompt=prompt,
        provider_name="anthropic",
        stdout=stdout,
        stderr=stderr,
        workspace_root=tmp_path,
    )
    with contextlib.ExitStack() as stack:
        for p in _headless_patches(provider_cls, registry):
            stack.enter_context(p)
        code = run_headless(options)
    return code, stdout.getvalue() + stderr.getvalue()


def test_cli_surface_startup_and_answer(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("CLAWCODEX_CONFIG_DIR", str(tmp_path / "config"))
    code, output = _run_headless(tmp_path, _TextProvider, ToolRegistry([]), "hello")
    assert code == 0, output
    assert "hi back" in output


def test_cli_surface_read_tool_round_trip(tmp_path, monkeypatch) -> None:
    from src.tool_system.tools import ReadTool

    global _READ_TARGET
    monkeypatch.setenv("CLAWCODEX_CONFIG_DIR", str(tmp_path / "config"))
    target = tmp_path / "cli-note.txt"
    target.write_text("cli-surface-read-ok", encoding="utf-8")
    _READ_TARGET = str(target)
    registry = ToolRegistry([ReadTool])
    code, output = _run_headless(tmp_path, _ReadThenTextProvider, registry, "read the note")
    assert code == 0, output
    assert "the file was read" in output

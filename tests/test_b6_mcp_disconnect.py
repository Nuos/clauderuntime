"""B6 P0 — no stale callable MCP tools after a server disconnect.

Hard rule: "MCP 已断开后不得继续暴露 stale callable tools". Covers:

1. ``McpClient`` fires its disconnect handler when the transport closes (EOF
   or receive-loop error) — and does NOT fire on a clean ``close()`` (the
   shutdown / OAuth-reconnect path, where CancelledError escapes the loop).
2. ``McpRuntime`` drops the server's tools from its own state and notifies the
   injected callback, so the agent registry removes ``mcp__<server>__*``.
3. End-to-end: a real stdio MCP server that exits mid-session leaves no
   callable tools behind.
"""
from __future__ import annotations

import asyncio
import sys
import textwrap
import time
from pathlib import Path

from src.server.mcp_runtime import McpRuntime
from src.services.mcp.client import McpClient
from src.services.mcp.config import ScopedMcpServerConfig
from src.services.mcp.mcp_string_utils import build_mcp_tool_name
from src.services.mcp.types import McpStdioServerConfig
from src.tool_system.context import ToolContext
from src.tool_system.registry import ToolRegistry


CRASH_MCP_SERVER_SCRIPT = textwrap.dedent("""\
    import json
    import sys

    def read_message():
        line = sys.stdin.readline()
        if not line:
            return None
        text = line.rstrip()
        if not text:
            return None
        return json.loads(text)

    def send_message(msg):
        body = json.dumps(msg, separators=(",", ":"))
        sys.stdout.write(body + "\\n")
        sys.stdout.flush()

    TOOLS = [
        {
            "name": "crash",
            "description": "exits the server process mid-session",
            "inputSchema": {"type": "object", "properties": {}}
        }
    ]

    while True:
        msg = read_message()
        if msg is None:
            break
        method = msg.get("method", "")
        msg_id = msg.get("id")

        if method == "initialize":
            send_message({
                "jsonrpc": "2.0", "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {"name": "crash-server", "version": "1.0.0"}
                }
            })
        elif method == "notifications/initialized":
            pass
        elif method == "tools/list":
            send_message({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}})
        elif method == "tools/call":
            send_message({
                "jsonrpc": "2.0", "id": msg_id,
                "result": {"content": [{"type": "text", "text": "crashing now"}], "isError": False}
            })
            # Die immediately after answering — the client's receive loop must
            # observe EOF and fire the disconnect handler.
            sys.exit(0)
        else:
            send_message({
                "jsonrpc": "2.0", "id": msg_id,
                "error": {"code": -32601, "message": "method not found"}
            })
""")


def _wait_until(predicate, timeout_s: float = 8.0, interval_s: float = 0.05) -> bool:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(interval_s)
    return predicate()


# ---------------------------------------------------------------------------
# 1. Client-level: transport close fires the disconnect handler
# ---------------------------------------------------------------------------


class _EofTransport:
    """Transport whose receive() immediately returns None (peer closed)."""

    is_connected = True

    async def receive(self):
        return None

    async def send(self, message):
        return None

    async def close(self):
        return None


def test_client_fires_disconnect_on_transport_eof() -> None:
    client = McpClient()
    fired = []
    client.set_disconnect_handler(lambda: fired.append(True))
    client._transport = _EofTransport()

    async def _run() -> None:
        await client._receive_loop()

    asyncio.run(_run())
    assert fired == [True], "disconnect handler must fire on transport EOF"
    assert client.is_connected is False


class _CancelledTransport:
    is_connected = True

    async def receive(self):
        await asyncio.sleep(3600)  # never returns; loop is cancelled

    async def send(self, message):
        return None

    async def close(self):
        return None


def test_client_clean_close_does_not_fire_disconnect() -> None:
    """A deliberate ``close()`` cancels the receive loop; that must NOT be
    treated as a peer disconnect (shutdown / OAuth-reconnect semantics)."""
    client = McpClient()
    fired = []
    client.set_disconnect_handler(lambda: fired.append(True))
    client._transport = _CancelledTransport()

    async def _run() -> None:
        task = asyncio.create_task(client._receive_loop())
        await asyncio.sleep(0.05)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    asyncio.run(_run())
    assert fired == [], "clean close must not fire the disconnect handler"


# ---------------------------------------------------------------------------
# 2. Runtime-level: tools dropped + registry notified
# ---------------------------------------------------------------------------


class _FakeClient:
    """Minimal stand-in exposing just the disconnect-handler surface."""

    def __init__(self) -> None:
        self._handler = None

    def set_disconnect_handler(self, handler) -> None:
        self._handler = handler

    def fire(self) -> None:
        self._handler()


def _wrapped_tool(server: str, name: str) -> object:
    from src.tool_system.build_tool import build_tool

    return build_tool(
        name=build_mcp_tool_name(server, name),
        input_schema={"type": "object", "properties": {}},
        call=lambda args, ctx: None,
        description=f"tool {name}",
        is_mcp=True,
    )


def test_runtime_drops_tools_and_notifies_registry_on_disconnect() -> None:
    rt = McpRuntime()
    client = _FakeClient()
    server = "ghost"
    rt.clients[server] = client
    rt.servers[server] = ["tool_a", "tool_b"]
    rt.tools = [_wrapped_tool(server, "tool_a"), _wrapped_tool(server, "tool_b")]
    rt.server_infos = [type("Info", (), {"name": server})()]

    registry = ToolRegistry()
    for tool in rt.tools:
        registry.register(tool)
    assert registry.get(build_mcp_tool_name(server, "tool_a")) is not None

    notified = []

    def _cb(name, removed):
        for full in removed:
            registry.remove_tool(full)
        notified.append((name, removed))

    rt.set_server_disconnect_callback(_cb)
    rt._wire_disconnect_handler(server, client)
    client.fire()

    assert server not in rt.clients
    assert server not in rt.servers
    assert rt.tools == []
    assert registry.get(build_mcp_tool_name(server, "tool_a")) is None
    assert registry.get(build_mcp_tool_name(server, "tool_b")) is None
    assert notified == [(server, [build_mcp_tool_name(server, "tool_a"),
                                  build_mcp_tool_name(server, "tool_b")])]


def test_runtime_ignores_stale_close_from_replaced_client() -> None:
    """OAuth reconnect swaps in a newer client; the old client's late close
    must not nuke the fresh tools."""
    rt = McpRuntime()
    server = "ghost"
    old_client = _FakeClient()
    new_client = _FakeClient()
    rt.clients[server] = new_client
    rt.servers[server] = ["tool_a"]
    rt.tools = [_wrapped_tool(server, "tool_a")]

    notified = []
    rt.set_server_disconnect_callback(
        lambda name, removed: notified.append((name, removed))
    )
    # Old client's handler was wired before the swap; firing it now must no-op.
    rt._wire_disconnect_handler(server, old_client)
    old_client.fire()

    assert server in rt.clients
    assert rt.clients[server] is new_client
    assert len(rt.tools) == 1
    assert notified == []


# ---------------------------------------------------------------------------
# 3. End-to-end: real stdio server dies mid-session
# ---------------------------------------------------------------------------


def _configure_crash_server(monkeypatch, tmp_path: Path) -> Path:
    script = tmp_path / "crash_mcp_server.py"
    script.write_text(CRASH_MCP_SERVER_SCRIPT)
    cfg = {
        "crash-server": ScopedMcpServerConfig(
            config=McpStdioServerConfig(command=sys.executable, args=[str(script)]),
            scope="project",
        )
    }
    import src.services.mcp.config as mcpconfig

    monkeypatch.setattr(mcpconfig, "get_all_mcp_configs", lambda: cfg)
    return script


def test_end_to_end_crash_leaves_no_stale_tools(monkeypatch, tmp_path: Path) -> None:
    _configure_crash_server(monkeypatch, tmp_path)
    rt = McpRuntime()
    try:
        assert rt.start() is True
        full = build_mcp_tool_name("crash-server", "crash")
        crash = next(t for t in rt.tools if t.name == full)

        res = crash.call({}, ToolContext(workspace_root="."))
        assert res.is_error is False  # the server answered before dying

        # The server process exited after answering → EOF → disconnect fires
        # asynchronously on the runtime loop. Poll until tools are dropped.
        assert _wait_until(lambda: "crash-server" not in rt.servers), (
            "server tools must be dropped after disconnect"
        )
        assert all(t.name != full for t in rt.tools)
        assert "crash-server" not in rt.clients
    finally:
        rt.shutdown()


def test_end_to_end_registry_removes_crashed_server_tools(monkeypatch, tmp_path: Path) -> None:
    _configure_crash_server(monkeypatch, tmp_path)
    rt = McpRuntime()
    try:
        assert rt.start() is True
        full = build_mcp_tool_name("crash-server", "crash")

        # Simulate the agent-server wiring: a live registry holding the MCP
        # tools, with the disconnect callback dropping them.
        registry = ToolRegistry()
        for tool in rt.tools:
            registry.register(tool)
        assert registry.get(full) is not None
        rt.set_server_disconnect_callback(
            lambda server, removed: [registry.remove_tool(name) for name in removed]
        )

        crash = next(t for t in rt.tools if t.name == full)
        crash.call({}, ToolContext(workspace_root="."))

        assert _wait_until(lambda: registry.get(full) is None), (
            "the live registry must lose the crashed server's tools"
        )
    finally:
        rt.shutdown()

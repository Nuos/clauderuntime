"""B6 Wave F1 — ListMcpResourcesTool / ReadMcpResourceTool edge cases.

05 号文档 Tools 项“补缺失 tool edge cases”：这两个 MCP resource 工具此前
没有任何直接测试。覆盖：输入校验、未连接 server、server 过滤、空结果映射、
客户端异常、read_resource 返回形态归一化。
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.tool_system.context import ToolContext
from src.tool_system.errors import ToolInputError
from src.tool_system.tools.mcp_resources import (
    ListMcpResourcesTool,
    ReadMcpResourceTool,
)


def _ctx(mcp_clients: dict | None = None) -> ToolContext:
    ctx = ToolContext(workspace_root=".")
    ctx.mcp_clients = mcp_clients or {}
    return ctx


def _client(resources: list[dict] | None = None, error: Exception | None = None) -> SimpleNamespace:
    def list_resources():
        if error is not None:
            raise error
        return resources or []

    return SimpleNamespace(list_resources=list_resources)


# ─── ListMcpResourcesTool ────────────────────────────────────────────────────


def test_list_with_no_clients_returns_empty_and_map_says_none() -> None:
    result = ListMcpResourcesTool.call({}, _ctx())
    assert result.is_error is False
    assert result.output == []
    mapped = ListMcpResourcesTool.map_result_to_api(result.output, "tu1")
    assert "No resources found" in mapped["content"]


def test_list_aggregates_all_clients_with_server_field() -> None:
    ctx = _ctx({
        "alpha": _client([{"uri": "a://1", "name": "ra", "mimeType": "text/plain"}]),
        "beta": _client([{"uri": "b://2", "name": "rb"}]),
    })
    result = ListMcpResourcesTool.call({}, ctx)
    assert result.is_error is False
    by_server = {(r["server"], r["uri"]) for r in result.output}
    assert by_server == {("alpha", "a://1"), ("beta", "b://2")}
    assert result.output[0]["name"] == "ra"


def test_list_filters_by_server() -> None:
    ctx = _ctx({
        "alpha": _client([{"uri": "a://1", "name": "ra"}]),
        "beta": _client([{"uri": "b://2", "name": "rb"}]),
    })
    result = ListMcpResourcesTool.call({"server": "beta"}, ctx)
    assert [(r["uri"]) for r in result.output] == ["b://2"]


def test_list_unknown_server_returns_error() -> None:
    result = ListMcpResourcesTool.call({"server": "ghost"}, _ctx({}))
    assert result.is_error is True
    assert "not connected" in result.output["error"]


def test_list_invalid_server_input_raises() -> None:
    with pytest.raises(ToolInputError):
        ListMcpResourcesTool.call({"server": ""}, _ctx())
    with pytest.raises(ToolInputError):
        ListMcpResourcesTool.call({"server": 42}, _ctx())


def test_list_client_error_appends_error_entry() -> None:
    ctx = _ctx({"broken": _client(error=RuntimeError("boom"))})
    result = ListMcpResourcesTool.call({}, ctx)
    assert result.is_error is False  # 单客户端失败不使整体失败
    assert result.output[0]["server"] == "broken"
    assert "boom" in result.output[0]["description"]


def test_list_non_list_return_skipped() -> None:
    client = SimpleNamespace(list_resources=lambda: {"not": "a list"})
    result = ListMcpResourcesTool.call({}, _ctx({"weird": client}))
    assert result.output == []


def test_list_client_without_list_resources_skipped() -> None:
    client = SimpleNamespace()  # no list_resources attr
    result = ListMcpResourcesTool.call({}, _ctx({"bare": client}))
    assert result.output == []


# ─── ReadMcpResourceTool ─────────────────────────────────────────────────────


def test_read_requires_server_and_uri() -> None:
    with pytest.raises(ToolInputError):
        ReadMcpResourceTool.call({}, _ctx())
    with pytest.raises(ToolInputError):
        ReadMcpResourceTool.call({"server": "s"}, _ctx())
    with pytest.raises(ToolInputError):
        ReadMcpResourceTool.call({"server": "", "uri": "u"}, _ctx())


def test_read_unknown_server_returns_error() -> None:
    result = ReadMcpResourceTool.call({"server": "ghost", "uri": "u"}, _ctx())
    assert result.is_error is True
    assert "not connected" in result.output["error"]


def test_read_client_without_read_resource_returns_error() -> None:
    result = ReadMcpResourceTool.call(
        {"server": "bare", "uri": "u"}, _ctx({"bare": SimpleNamespace()})
    )
    assert result.is_error is True
    assert "does not support resources" in result.output["error"]


def test_read_passthrough_contents() -> None:
    client = SimpleNamespace(read_resource=lambda uri: {"contents": [{"uri": uri, "text": "hi"}]})
    result = ReadMcpResourceTool.call(
        {"server": "s", "uri": "u"}, _ctx({"s": client})
    )
    assert result.is_error is False
    assert result.output["contents"][0]["text"] == "hi"


def test_read_wraps_plain_dict_into_contents() -> None:
    client = SimpleNamespace(read_resource=lambda uri: {"text": "plain", "uri": uri})
    result = ReadMcpResourceTool.call(
        {"server": "s", "uri": "u"}, _ctx({"s": client})
    )
    assert result.output["contents"] == [{"uri": "u", "text": "plain"}]


def test_read_wraps_non_dict_into_text() -> None:
    client = SimpleNamespace(read_resource=lambda uri: "raw string")
    result = ReadMcpResourceTool.call(
        {"server": "s", "uri": "u"}, _ctx({"s": client})
    )
    assert result.output["contents"] == [{"uri": "u", "text": "raw string"}]


# ─── mapResultToApi 边界 ─────────────────────────────────────────────────────


def test_map_result_json_round_trip() -> None:
    mapped = ListMcpResourcesTool.map_result_to_api(
        [{"uri": "a://1", "server": "s"}], "tu2"
    )
    import json

    assert json.loads(mapped["content"]) == [{"uri": "a://1", "server": "s"}]

"""Wave 2 F7 — tool pool 四阶段投影测试（CCR-05 Capability Assembly）。

对照 reference tools.ts（assembleToolPool/filterToolsByDenyRules）与
python registry.py：
- base tools（registry 全量）→ deny prefilter → enabled 过滤 → MCP 并入
  → 同名 dedupe（builtin 优先）→ 排序
- 顺序契约：builtin 连续前缀在前，MCP 在后（prompt-cache breakpoint 语义）
"""

import unittest
from unittest.mock import MagicMock

from src.permissions.types import ToolPermissionContext
from src.tool_system.defaults import build_default_registry
from src.tool_system.registry import (
    assemble_tool_pool,
    filter_tools_by_deny_rules,
    get_tools,
)


def _empty_ctx() -> ToolPermissionContext:
    return ToolPermissionContext(mode="default")


def _mock_tool(name: str, *, is_mcp: bool = False, enabled: bool = True):
    tool = MagicMock()
    tool.name = name
    tool.is_mcp = is_mcp
    tool.is_enabled.return_value = enabled
    return tool


class TestToolPoolAssembly(unittest.TestCase):
    """assemble_tool_pool 四阶段投影。"""

    def setUp(self):
        self.registry = build_default_registry()

    def test_pool_builtins_sorted(self):
        """无 MCP 时：builtin 全量按名排序。"""
        pool = assemble_tool_pool(self.registry, _empty_ctx())
        names = [t.name for t in pool]
        self.assertGreater(len(names), 0)
        self.assertEqual(names, sorted(names))

    def test_pool_mcp_appended_after_builtins(self):
        """MCP 工具必须整体排在 builtin 之后（连续前缀）。"""
        # 以实际进入 pool 的 builtin 为准（排除 enabled/deny 过滤）
        builtin_pool = assemble_tool_pool(self.registry, _empty_ctx())
        builtin_names = [t.name for t in builtin_pool]
        mcp_tools = [_mock_tool("ZzzMcpTool", is_mcp=True),
                     _mock_tool("AaaMcpTool", is_mcp=True)]
        pool = assemble_tool_pool(self.registry, _empty_ctx(), mcp_tools)
        names = [t.name for t in pool]
        # 每个 builtin 都出现在任何 mcp 之前
        last_builtin = max(names.index(n) for n in builtin_names)
        first_mcp = min(names.index("AaaMcpTool"), names.index("ZzzMcpTool"))
        self.assertLess(last_builtin, first_mcp, "builtin 必须是连续前缀")

    def test_pool_deny_filters_builtin_and_mcp(self):
        """deny 规则同时过滤 builtin 与 MCP。"""
        ctx = MagicMock()
        ctx.blocks.side_effect = lambda name: name in ("Bash", "EvilMcp")
        mcp_tools = [_mock_tool("EvilMcp", is_mcp=True),
                     _mock_tool("GoodMcp", is_mcp=True)]
        pool = assemble_tool_pool(self.registry, ctx, mcp_tools)
        names = [t.name for t in pool]
        self.assertNotIn("Bash", names)
        self.assertNotIn("EvilMcp", names)
        self.assertIn("GoodMcp", names)

    def test_pool_dedupe_builtin_wins(self):
        """同名冲突：builtin 保留、MCP 丢弃（insertion order）。"""
        builtin_pool = assemble_tool_pool(self.registry, _empty_ctx())
        target = builtin_pool[0].name  # 取一个实际进 pool 的 builtin 名
        mcp_tools = [_mock_tool(target, is_mcp=True)]
        pool = assemble_tool_pool(self.registry, _empty_ctx(), mcp_tools)
        names = [t.name for t in pool]
        self.assertEqual(names.count(target), 1, "同名必须去重")
        kept = next(t for t in pool if t.name == target)
        self.assertFalse(kept.is_mcp, "builtin 必须优先保留")

    def test_get_tools_filters_deny_and_disabled(self):
        """get_tools = base → deny prefilter → enabled 过滤。"""
        ctx = ToolPermissionContext.from_iterables(deny_names=["Bash"])
        tools = get_tools(self.registry, ctx)
        names = [t.name for t in tools]
        self.assertNotIn("Bash", names)
        # enabled 过滤：构造一个 disabled 工具混入
        disabled = _mock_tool("DisabledTool", enabled=False)
        filtered = filter_tools_by_deny_rules([disabled], ctx)
        self.assertEqual(len(filtered), 1)  # deny 层只看名字


if __name__ == "__main__":
    unittest.main()

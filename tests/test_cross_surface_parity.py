"""Wave 5 F19 — cross-surface 语义等价测试（R7-02 / §8 双路径）。

对照规则圣经 R7-02 与 §8：
- 所有 agent-loop surface 最终汇入 shared core path（query）
- surface 不拥有第二套 core semantics（permission engine / tool scheduler / retry）
- agent_loop_compat 是适配器（非第二 loop）
"""

import unittest
from pathlib import Path

from src.query import agent_loop_compat


class TestCrossSurfaceParity(unittest.TestCase):
    """surface 汇入与无第二套 core 语义。"""

    def test_agent_loop_compat_is_adapter(self):
        """agent_loop_compat 内部 import query（适配器，非第二 loop）。"""
        src = Path(agent_loop_compat.__file__).read_text(encoding="utf-8")
        self.assertIn("from .query import", src)
        self.assertIn("query", src)

    def test_surface_has_no_second_permission_engine(self):
        """entrypoints 不定义第二套 permission 引擎（R7-02 禁止）。"""
        entrypoints_dir = Path("src/entrypoints")
        for f in entrypoints_dir.glob("*.py"):
            if f.name.startswith("__"):
                continue
            src = f.read_text(encoding="utf-8")
            # 不"定义"permission 决策函数（deny-first 引擎仅在 permissions/）
            self.assertNotIn(
                "def has_permissions_to_use_tool",
                src,
                f"{f.name} 不应定义第二套 permission 引擎",
            )

    def test_surface_has_no_second_tool_scheduler(self):
        """entrypoints 不定义第二套 tool scheduler（R7-02 禁止）。"""
        entrypoints_dir = Path("src/entrypoints")
        for f in entrypoints_dir.glob("*.py"):
            if f.name.startswith("__"):
                continue
            src = f.read_text(encoding="utf-8")
            self.assertNotIn(
                "def assemble_tool_pool",
                src,
                f"{f.name} 不应定义第二套 tool pool 组装",
            )

    def test_tui_routes_through_agent_server(self):
        """tui_launcher 经 agent_server_cli 间接汇入（不重实现 core）。"""
        src = Path("src/entrypoints/tui_launcher.py").read_text(encoding="utf-8")
        self.assertIn("run_agent_server_subcommand", src)

    def test_daemon_stub_is_honest(self):
        """daemon 是诚实占位（不冒充实现）。"""
        src = Path("src/entrypoints/daemon.py").read_text(encoding="utf-8")
        self.assertIn("not implemented", src.lower())
        # 占位不触发 core imports（冷启动轻量）
        self.assertNotIn("from src.query", src)


if __name__ == "__main__":
    unittest.main()

"""Wave 2 F9 — tool result 契约测试（CCR-09 Result Processing）。

对照 reference toolResultStorage.ts / toolExecution.ts：
- tool result 按 tool-use contract 回写（tool_use_id 配对、type=tool_result、is_error）
- 抛错内容 RAW 上线路（无 <tool_use_error> 包裹），>40KB 中间截断
- 结果持久化：小内容内联、大内容落盘（"x" 模式防重写）+ preview
"""

import tempfile
import unittest
from pathlib import Path

from src.services.tool_execution.tool_execution import (
    _create_tool_result_stop,
    _format_error,
)
from src.services.tool_execution.tool_result_persistence import (
    PersistedToolResult,
    PersistToolResultError,
    is_persist_error,
    persist_tool_result,
)


class TestToolResultContract(unittest.TestCase):
    """tool-use contract 回写契约。"""

    def test_create_tool_result_stop_pairs_id(self):
        """取消结果：tool_use_id 配对 + type/is_error 正确。"""
        result = _create_tool_result_stop("toolu_abc")
        self.assertEqual(result["type"], "tool_result")
        self.assertEqual(result["tool_use_id"], "toolu_abc")
        self.assertTrue(result["is_error"])

    def test_format_error_raw_no_wrapping(self):
        """抛错内容 RAW 上线路：无 <tool_use_error> 包裹（TS 语义）。"""
        err = ValueError("boom: disk full")
        text = _format_error(err)
        self.assertIn("boom: disk full", text)
        self.assertNotIn("<tool_use_error>", text)

    def test_format_error_truncates_long(self):
        """>40KB 错误内容中间截断（_FORMAT_ERROR_MAX_LENGTH + 截断说明）。"""
        long_msg = "x" * 50000
        text = _format_error(ValueError(long_msg))
        self.assertLess(len(text), 41000)  # 40000 + 截断说明 ~40 字符
        self.assertIn("x", text)
        self.assertIn("truncated", text)

    def test_format_error_appends_stderr(self):
        """错误对象携带 str stderr/stdout 时追加（TS getErrorParts）。"""

        class _ProcError(Exception):
            stderr = "permission denied on /etc"
            stdout = ""

        text = _format_error(_ProcError("command failed"))
        self.assertIn("permission denied", text)


class TestResultPersistence(unittest.TestCase):
    """结果持久化契约（toolResultStorage.ts）。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.results_dir = Path(self.tmp.name) / "results"
        self.results_dir.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def test_small_content_inline_no_file(self):
        """小内容不落盘（无副作用）。"""
        result = persist_tool_result(
            "small output", "toolu_small",
            tool_results_dir=self.results_dir,
        )
        self.assertFalse(is_persist_error(result))
        self.assertIsInstance(result, PersistedToolResult)
        # 内容足够小 → 无文件（filepath 为空或预览完整）
        self.assertIn("small output", result.preview)
        self.assertFalse(result.has_more)

    def test_large_content_persists_to_disk(self):
        """大内容落盘 + 返回 preview + has_more。"""
        big = "y" * 20000  # 超过阈值（默认定 10KB 级）
        result = persist_tool_result(
            big, "toolu_big", tool_results_dir=self.results_dir,
        )
        self.assertFalse(is_persist_error(result), f"持久化失败: {result}")
        self.assertIsInstance(result, PersistedToolResult)
        self.assertNotEqual(result.filepath, "")
        self.assertTrue(Path(result.filepath).exists())
        self.assertIn("y", result.preview)
        self.assertTrue(result.has_more)

    def test_persist_uses_x_mode_no_rewrite(self):
        """同一 tool_use_id 重复持久化：'x' 模式防重写为 no-op。"""
        big = "z" * 20000
        r1 = persist_tool_result(big, "toolu_dup",
                                 tool_results_dir=self.results_dir)
        r2 = persist_tool_result(big, "toolu_dup",
                                 tool_results_dir=self.results_dir)
        self.assertFalse(is_persist_error(r1))
        self.assertFalse(is_persist_error(r2))
        # 两次返回同一文件（未重写）
        if isinstance(r1, PersistedToolResult) and isinstance(r2, PersistedToolResult):
            self.assertEqual(r1.filepath, r2.filepath)

    def test_json_content_persisted(self):
        """list 内容按 JSON 持久化（is_json=True）。"""
        content = [{"type": "text", "text": "hello"}]
        result = persist_tool_result(
            content, "toolu_json", tool_results_dir=self.results_dir,
        )
        self.assertFalse(is_persist_error(result))
        if isinstance(result, PersistedToolResult):
            self.assertTrue(result.is_json)


if __name__ == "__main__":
    unittest.main()

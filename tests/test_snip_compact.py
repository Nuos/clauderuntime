"""验证 Python-native 保守 Snip（B6 方案 B，FUNCTIONAL_ADAPTATION）。

只裁剪“可重建”的旧工具结果（只读工具 allowlist），其余内容一律保留：
- 最近 ``keep_recent`` 条可裁剪结果保留；
- 变更类工具（Write/Bash 等）的结果不裁剪（副作用不可重建）；
- assistant/user 文本与 tool_use 块不裁剪；
- 无法确定来源工具的 tool_result 不裁剪（保守）。
"""

from __future__ import annotations

import unittest

from src.types.content_blocks import ToolResultBlock, ToolUseBlock
from src.types.messages import AssistantMessage, UserMessage
from src.services.compact.snip_compact import (
    RECONSTRUCTABLE_TOOLS,
    SNIPPED_MARKER,
    snip_compact,
)


def _assistant(tool_id: str, tool_name: str = "Read") -> AssistantMessage:
    return AssistantMessage(
        role="assistant",
        content=[ToolUseBlock(id=tool_id, name=tool_name, input={})],
    )


def _result(tool_id: str, content: str = "file content here") -> UserMessage:
    return UserMessage(
        role="user",
        content=[ToolResultBlock(tool_use_id=tool_id, content=content)],
    )


class TestSnipCompact(unittest.TestCase):
    def test_empty_messages(self):
        result, saved = snip_compact([])
        self.assertEqual(result, [])
        self.assertEqual(saved, 0)

    def test_few_results_are_never_snipped(self):
        """结果数不超过 keep_recent 时完全不裁剪。"""
        messages = [
            _assistant("t1"),
            _result("t1", "old " * 200),
            _assistant("t2"),
            _result("t2", "recent result"),
        ]
        result, saved = snip_compact(messages, keep_recent=2)
        self.assertEqual(saved, 0)
        self.assertEqual(len(result), 4)
        self.assertEqual(result[1].content[0].content, "old " * 200)
        self.assertEqual(result[3].content[0].content, "recent result")

    def test_old_reconstructable_read_results_are_snipped(self):
        messages = [
            _assistant("t1", "Read"),
            _result("t1", "old " * 200),
            _assistant("t2", "Read"),
            _result("t2", "also old " * 200),
            _assistant("t3", "Read"),
            _result("t3", "recent result"),
        ]
        result, saved = snip_compact(messages, keep_recent=1)
        self.assertGreater(saved, 0)
        self.assertEqual(len(result), 6)
        self.assertEqual(result[1].content[0].content, SNIPPED_MARKER)
        self.assertEqual(result[3].content[0].content, SNIPPED_MARKER)
        # 最近的保留
        self.assertEqual(result[5].content[0].content, "recent result")
        # tool_use 块原样保留
        self.assertEqual(result[0].content[0].name, "Read")

    def test_keep_recent_controls_trim_window(self):
        messages = [
            _assistant("t1", "Read"),
            _result("t1", "old " * 200),
            _assistant("t2", "Read"),
            _result("t2", "mid " * 200),
            _assistant("t3", "Read"),
            _result("t3", "recent result"),
        ]
        result, saved = snip_compact(messages, keep_recent=2)
        self.assertGreater(saved, 0)
        self.assertEqual(result[1].content[0].content, SNIPPED_MARKER)
        self.assertEqual(result[3].content[0].content, "mid " * 200)
        self.assertEqual(result[5].content[0].content, "recent result")

    def test_mutating_tool_results_never_snipped(self):
        """Write/Bash 结果描述副作用，不可重建，必须保留。"""
        messages = [
            _assistant("t1", "Read"),
            _result("t1", "old read " * 200),
            _assistant("t2", "Write"),
            _result("t2", "wrote a file - side effect " * 200),
            _assistant("t3", "Bash"),
            _result("t3", "deployed - side effect " * 200),
        ]
        result, saved = snip_compact(messages, keep_recent=1)
        # 只有 Read 的旧结果被裁剪
        self.assertGreater(saved, 0)
        self.assertEqual(result[1].content[0].content, SNIPPED_MARKER)
        self.assertEqual(result[3].content[0].content, "wrote a file - side effect " * 200)
        self.assertEqual(result[5].content[0].content, "deployed - side effect " * 200)

    def test_unknown_source_tool_result_is_kept(self):
        """找不到对应 tool_use 的 tool_result：保守保留。"""
        messages = [
            _assistant("t1", "Read"),
            _result("t1", "old " * 200),
            _result("orphan", "no tool_use for me " * 200),
        ]
        result, saved = snip_compact(messages, keep_recent=0)
        self.assertGreater(saved, 0)
        self.assertEqual(result[1].content[0].content, SNIPPED_MARKER)
        self.assertEqual(result[2].content[0].content, "no tool_use for me " * 200)

    def test_user_text_and_assistant_text_kept(self):
        messages = [
            UserMessage(role="user", content="please read the file"),
            _assistant("t1", "Read"),
            _result("t1", "old " * 200),
            AssistantMessage(role="assistant", content="here is the file"),
        ]
        result, saved = snip_compact(messages, keep_recent=0)
        self.assertGreater(saved, 0)
        self.assertEqual(result[0].content, "please read the file")
        self.assertEqual(result[3].content, "here is the file")

    def test_dict_content_blocks_are_snipped(self):
        messages = [
            AssistantMessage(role="assistant", content=[
                {"type": "tool_use", "id": "d1", "name": "Read", "input": {}},
            ]),
            UserMessage(role="user", content=[
                {"type": "tool_result", "tool_use_id": "d1", "content": "dict content " * 200},
            ]),
            AssistantMessage(role="assistant", content=[
                {"type": "tool_use", "id": "d2", "name": "Read", "input": {}},
            ]),
            UserMessage(role="user", content=[
                {"type": "tool_result", "tool_use_id": "d2", "content": "recent dict"},
            ]),
        ]
        result, saved = snip_compact(messages, keep_recent=1)
        self.assertGreater(saved, 0)
        self.assertEqual(result[1].content[0]["content"], SNIPPED_MARKER)
        self.assertEqual(result[3].content[0]["content"], "recent dict")

    def test_error_results_preserve_is_error_flag(self):
        messages = [
            _assistant("t1", "Read"),
            UserMessage(role="user", content=[
                ToolResultBlock(tool_use_id="t1", content="boom " * 200, is_error=True),
            ]),
            _assistant("t2", "Read"),
            _result("t2", "recent"),
        ]
        result, saved = snip_compact(messages, keep_recent=1)
        self.assertGreater(saved, 0)
        block = result[1].content[0]
        self.assertEqual(block.content, SNIPPED_MARKER)
        self.assertTrue(block.is_error)

    def test_reconstructable_allowlist_is_conservative(self):
        self.assertIn("Read", RECONSTRUCTABLE_TOOLS)
        self.assertIn("Grep", RECONSTRUCTABLE_TOOLS)
        # 变更类工具绝不在 allowlist 内
        for name in ("Write", "Edit", "Bash", "Agent", "NotebookEdit"):
            self.assertNotIn(name, RECONSTRUCTABLE_TOOLS)


if __name__ == "__main__":
    unittest.main()

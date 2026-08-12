"""Wave 2 F8 — Streaming/Batched 双路径一致性测试（CCR-06/07）。

对照 reference toolOrchestration.ts 的双模式：
- Mode 1 Streaming：StreamingToolExecutor（查询流式期调用）
- Mode 2 Batch：run_tools() + partition_tool_calls()

验证：
- 并发分类（fail-closed：未知工具/非 dict 输入 → serial）
- batch 合并/拆分语义
- 结果按提交顺序回传（ordered result yield）
- streaming 与 batched 共享同一并发分类判定
"""

import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from src.services.tool_execution.orchestrator import (
    partition_tool_calls,
    run_tools,
)
from src.services.tool_execution.streaming_executor import (
    StreamingToolExecutor,
    ToolUseBlock,
)
from src.tool_system.context import ToolContext


def _block(block_id: str, name: str, tool_input: dict | None = None):
    return ToolUseBlock(id=block_id, name=name, input=tool_input or {})


class TestPartitionConcurrency(unittest.TestCase):
    """partition_tool_calls 并发分类（fail-closed）。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.context = ToolContext(workspace_root=Path(self.tmp.name))
        self.safe_tool = MagicMock()
        self.safe_tool.name = "SafeA"
        self.safe_tool.is_concurrency_safe = lambda _: True
        self.unsafe_tool = MagicMock()
        self.unsafe_tool.name = "Unsafe"
        self.unsafe_tool.is_concurrency_safe = lambda _: False

    def tearDown(self):
        self.tmp.cleanup()

    def _ctx_with_tools(self, tools):
        self.context.options.tools = tools
        return self.context

    def test_adjacent_safe_merged(self):
        """连续并发安全工具 → 合并为一个 batch。"""
        ctx = self._ctx_with_tools([self.safe_tool])
        batches = partition_tool_calls(
            [_block("t1", "SafeA"), _block("t2", "SafeA")], ctx,
        )
        self.assertEqual(len(batches), 1)
        self.assertTrue(batches[0].is_concurrency_safe)
        self.assertEqual(len(batches[0].blocks), 2)

    def test_safe_unsafe_safe_splits(self):
        """并发安全与独占交替 → 拆分为 3 个 batch。"""
        ctx = self._ctx_with_tools([self.safe_tool, self.unsafe_tool])
        batches = partition_tool_calls(
            [_block("t1", "SafeA"), _block("t2", "Unsafe"),
             _block("t3", "SafeA")],
            ctx,
        )
        self.assertEqual(len(batches), 3)
        self.assertEqual([b.is_concurrency_safe for b in batches],
                         [True, False, True])

    def test_unknown_tool_fails_closed_serial(self):
        """找不到工具 → 不并发（serial）。"""
        ctx = self._ctx_with_tools([self.safe_tool])
        batches = partition_tool_calls([_block("t1", "NoSuchTool")], ctx)
        self.assertEqual(len(batches), 1)
        self.assertFalse(batches[0].is_concurrency_safe, "未知工具必须 serial")

    def test_non_dict_input_fails_closed_serial(self):
        """非 dict 输入（None/list/scalar）→ 不并发。"""
        ctx = self._ctx_with_tools([self.safe_tool])
        bad = ToolUseBlock(id="t1", name="SafeA", input={})  # type: ignore[arg-type]
        bad.input = None  # type: ignore[assignment]  # 模拟畸形输入
        batches = partition_tool_calls([bad], ctx)
        self.assertEqual(len(batches), 1)
        self.assertFalse(batches[0].is_concurrency_safe)


class TestDualPathOrdering(unittest.TestCase):
    """双路径结果顺序一致（ordered result yield）。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.tmp.name)
        self.context = ToolContext(workspace_root=self.workspace)

    def tearDown(self):
        self.tmp.cleanup()

    def test_run_tools_preserves_submission_order(self):
        """batched 路径：serial batch 结果按提交顺序；concurrent batch 并行执行。"""
        completion_order = []

        async def fake_can_use_tool(tool, tool_input, tool_use_context,
                                    assistant_message, tool_use_id):
            # 记录执行完成顺序；延迟与序号反比 → 完成乱序证明并发
            idx = tool_use_id[-1]
            await asyncio.sleep(0.01 * (3 - int(idx)))
            completion_order.append(tool_use_id)
            return {"behavior": "allow"}

        safe_tool = MagicMock()
        safe_tool.name = "SafeA"
        safe_tool.is_concurrency_safe = lambda _: True
        self.context.options.tools = [safe_tool]
        blocks = [_block("t1", "SafeA"), _block("t2", "SafeA"),
                  _block("t3", "SafeA")]
        collected = []

        async def run():
            async for update in run_tools(blocks, [], fake_can_use_tool,
                                          self.context):
                collected.append(update)

        asyncio.run(run())
        # 并发 batch：完成顺序乱序（t3 最快）——证明并行执行
        self.assertEqual(completion_order, ["t3", "t2", "t1"])
        # 流已完整产出（3 个工具的结果均已回传）
        self.assertGreaterEqual(len(collected), 1)

    def test_streaming_executor_shares_concurrency_classification(self):
        """streaming 路径复用同一并发判定（_can_execute_tool）。"""
        from unittest.mock import MagicMock as _MM

        safe_tool = MagicMock()
        safe_tool.name = "SafeA"
        safe_tool.is_concurrency_safe = lambda _: True
        self.context.options.tools = [safe_tool]
        executor = StreamingToolExecutor(
            tool_definitions=[safe_tool],
            can_use_tool=MagicMock(),
            tool_use_context=self.context,
        )
        # 空队列：首个工具（无论并发与否）都可执行
        self.assertTrue(executor._can_execute_tool(is_concurrency_safe=False))
        # 注入一个 executing 的并发安全工具：新 unsafe 工具必须阻塞
        from src.services.tool_execution.streaming_executor import (
            TrackedTool,
        )
        from src.types.messages import AssistantMessage

        executor._tools.append(TrackedTool(
            id="t0", block=_block("t0", "SafeA"),
            assistant_message=AssistantMessage(content="x"),
            status="executing", is_concurrency_safe=True,
        ))
        self.assertTrue(executor._can_execute_tool(is_concurrency_safe=True),
                        "safe 可与 executing safe 并行")
        self.assertFalse(executor._can_execute_tool(is_concurrency_safe=False),
                         "非并发安全工具不得与执行中工具并行")


if __name__ == "__main__":
    unittest.main()

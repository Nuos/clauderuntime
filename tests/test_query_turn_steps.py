"""Wave 1 F1/F2 — 9-step turn trace 与 config 快照测试。

覆盖：
- TurnTracer 单元：emit 记录顺序、disabled 零开销、finish 快照、序列去重、turn 过滤
- query() 集成：单 turn 无工具 trace 顺序、多 turn 带工具完整 9-step 顺序
- F2 config 快照：query() 内 build_query_config 只调用一次（query-entry 快照防漂移）
"""

import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.providers.base import ChatResponse
from src.query.query import QueryParams, query
from src.query.turn_steps import (
    CANONICAL_STEP_ORDER,
    TURN_STEPS,
    TraceEntry,
    TurnTracer,
)
from src.tool_system.context import ToolContext
from src.tool_system.defaults import build_default_registry
from src.types.messages import UserMessage
from src.utils.abort_controller import AbortController


def _run(coro):
    return asyncio.run(coro)


class TestTurnTracer(unittest.TestCase):
    """TurnTracer 单元测试。"""

    def test_emit_records_in_order(self):
        tracer = TurnTracer(enabled=True)
        tracer.emit(TURN_STEPS.SETTINGS_RESOLUTION, 0, "config")
        tracer.emit(TURN_STEPS.MODEL_CALL, 0, "attempt=0")
        self.assertEqual(
            [e.step for e in tracer.entries],
            [TURN_STEPS.SETTINGS_RESOLUTION, TURN_STEPS.MODEL_CALL],
        )
        self.assertEqual(tracer.entries[0].turn, 0)
        self.assertEqual(tracer.entries[0].detail, "config")

    def test_disabled_emit_noop(self):
        """disabled 时 emit 不记录（近零开销）。"""
        tracer = TurnTracer(enabled=False)
        tracer.emit(TURN_STEPS.MODEL_CALL, 0)
        tracer.emit(TURN_STEPS.STOP_CONTINUE, 0)
        self.assertEqual(tracer.entries, [])
        self.assertFalse(tracer.enabled)

    def test_finish_returns_copy(self):
        tracer = TurnTracer(enabled=True)
        tracer.emit(TURN_STEPS.MODEL_CALL, 0)
        snapshot = tracer.finish()
        snapshot.append(TraceEntry(TURN_STEPS.STOP_CONTINUE, 0))
        self.assertEqual(len(tracer.entries), 1)  # 内部不被污染

    def test_step_sequence_dedup_first_seen(self):
        tracer = TurnTracer(enabled=True)
        tracer.emit(TURN_STEPS.MODEL_CALL, 0)
        tracer.emit(TURN_STEPS.MODEL_CALL, 1)  # 重复 step 只保留首现
        tracer.emit(TURN_STEPS.TOOL_DISPATCH, 1)
        self.assertEqual(
            tracer.step_sequence(),
            [TURN_STEPS.MODEL_CALL, TURN_STEPS.TOOL_DISPATCH],
        )

    def test_turn_steps_filters_by_turn(self):
        tracer = TurnTracer(enabled=True)
        tracer.emit(TURN_STEPS.SETTINGS_RESOLUTION, 0)
        tracer.emit(TURN_STEPS.MODEL_CALL, 0)
        tracer.emit(TURN_STEPS.MODEL_CALL, 1)
        tracer.emit(TURN_STEPS.STOP_CONTINUE, 1)
        self.assertEqual(
            tracer.turn_steps(1),
            [TURN_STEPS.MODEL_CALL, TURN_STEPS.STOP_CONTINUE],
        )

    def test_canonical_order_is_9_steps(self):
        """规范顺序必须正好 9 步且与 B3 9-step 一致。"""
        self.assertEqual(len(CANONICAL_STEP_ORDER), 9)
        self.assertEqual(
            CANONICAL_STEP_ORDER[0], TURN_STEPS.SETTINGS_RESOLUTION
        )
        self.assertEqual(CANONICAL_STEP_ORDER[4], TURN_STEPS.MODEL_CALL)
        self.assertEqual(CANONICAL_STEP_ORDER[-1], TURN_STEPS.STOP_CONTINUE)


class TestQueryTrace(unittest.TestCase):
    """query() 集成：9-step trace 顺序 + config 快照。"""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp_dir.name)
        self.registry = build_default_registry()
        self.context = ToolContext(workspace_root=self.workspace)
        self.abort = AbortController()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _collect(self, params):
        collected = []

        async def run():
            async for msg in query(params):
                collected.append(msg)

        _run(run())
        return collected

    def test_single_turn_no_tools_step_order(self):
        """单 turn 无工具：仅 settings→state→context→shapers→model（无 tool 步）。"""
        provider = MagicMock()
        provider.chat_stream_response.side_effect = NotImplementedError()
        provider.chat.return_value = ChatResponse(
            content="Hello",
            model="test",
            usage={"input_tokens": 10, "output_tokens": 5},
            finish_reason="end_turn",
            tool_uses=None,
        )
        params = QueryParams(
            messages=[UserMessage(content="Hi")],
            system_prompt="You are helpful.",
            tools=self.registry.list_tools(),
            tool_registry=self.registry,
            tool_use_context=self.context,
            provider=provider,
            abort_controller=self.abort,
            max_turns=10,
            trace_steps=True,
        )
        captured = {}

        class RecordingTracer(TurnTracer):
            def emit(self, step, turn, detail=""):
                super().emit(step, turn, detail)
                captured.setdefault("seq", []).append(step)

        with patch("src.query.query.TurnTracer", RecordingTracer):
            self._collect(params)

        seq = captured.get("seq", [])
        # 单 turn 无工具：9-step 只走前 5 步（无 tool dispatch/permission/execution）
        expected = list(CANONICAL_STEP_ORDER[:5])
        self.assertEqual(
            seq, expected,
            f"无工具单 turn 序列不符: {seq}（期望 {expected}）",
        )

    def test_multi_turn_tools_full_9_steps(self):
        """多 turn 带工具：turn0 完整 9 步（含 tool dispatch/permission/execution）。"""
        provider = MagicMock()
        provider.chat_stream_response.side_effect = NotImplementedError()
        tool_use_response = ChatResponse(
            content="I'll write the file.",
            model="test",
            usage={"input_tokens": 10, "output_tokens": 20},
            finish_reason="tool_use",
            tool_uses=[{
                "id": "toolu_001",
                "name": "Write",
                "input": {
                    "file_path": str(self.workspace / "trace.txt"),
                    "content": "hello",
                },
            }],
        )
        final_response = ChatResponse(
            content="Done!",
            model="test",
            usage={"input_tokens": 30, "output_tokens": 10},
            finish_reason="end_turn",
            tool_uses=None,
        )
        provider.chat.side_effect = [tool_use_response, final_response]
        params = QueryParams(
            messages=[UserMessage(content="Create trace.txt")],
            system_prompt="You are helpful.",
            tools=self.registry.list_tools(),
            tool_registry=self.registry,
            tool_use_context=self.context,
            provider=provider,
            abort_controller=self.abort,
            max_turns=10,
            trace_steps=True,
        )
        # 包装 TurnTracer：把 query() 内部创建的 tracer 换成记录版
        captured = {}

        class RecordingTracer(TurnTracer):
            def emit(self, step, turn, detail=""):
                super().emit(step, turn, detail)
                captured.setdefault("seq", []).append(step)

        with patch("src.query.query.TurnTracer", RecordingTracer):
            self._collect(params)

        seq = captured.get("seq", [])
        # turn0 必须包含完整 9 步且顺序符合规范（settings 只出现在 turn0）
        self.assertIn(TURN_STEPS.SETTINGS_RESOLUTION, seq)
        self.assertEqual(seq[0], TURN_STEPS.SETTINGS_RESOLUTION)
        # 9 步按规范顺序出现（首现顺序 == CANONICAL 前缀）
        first_seen = []
        for step in seq:
            if step not in first_seen:
                first_seen.append(step)
        self.assertEqual(
            first_seen, list(CANONICAL_STEP_ORDER),
            f"9-step 顺序不符: {first_seen}",
        )
        # tool 段三连必须出现
        self.assertIn(TURN_STEPS.TOOL_DISPATCH, seq)
        self.assertIn(TURN_STEPS.PERMISSION_GATE, seq)
        self.assertIn(TURN_STEPS.TOOL_EXECUTION, seq)
        self.assertIn(TURN_STEPS.STOP_CONTINUE, seq)

    def test_config_snapshot_single_build(self):
        """F2 — config 快照：query() 只在入口构建一次配置（turn 内不漂移）。"""
        provider = MagicMock()
        provider.chat_stream_response.side_effect = NotImplementedError()
        provider.chat.return_value = ChatResponse(
            content="Hello",
            model="test",
            usage={"input_tokens": 10, "output_tokens": 5},
            finish_reason="end_turn",
            tool_uses=None,
        )
        params = QueryParams(
            messages=[UserMessage(content="Hi")],
            system_prompt="You are helpful.",
            tools=self.registry.list_tools(),
            tool_registry=self.registry,
            tool_use_context=self.context,
            provider=provider,
            abort_controller=self.abort,
            max_turns=10,
        )
        with patch("src.query.query.build_query_config") as mock_build:
            mock_build.return_value = MagicMock()
            self._collect(params)
            # 多 turn 时也只构建一次：快照在 query entry，turn 间复用
            self.assertEqual(mock_build.call_count, 1)


if __name__ == "__main__":
    unittest.main()

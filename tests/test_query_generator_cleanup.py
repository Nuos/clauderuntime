"""Wave 1 F3 — abort / generator-close 清理验证测试。

验证 query() async generator 被提前关闭（aclose）时：
- 不抛异常泄漏（GeneratorExit 正确传播、无二次异常）；
- 无悬挂 asyncio 任务残留（transient state 可解释清理）；
- abort 后的中断语义不破坏（沿用既有 abort lane）。

若测试失败说明需要补充 finally 清理路径（最小侵入挂接点）。
"""

import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from src.providers.base import ChatResponse
from src.query.query import QueryParams, query
from src.tool_system.context import ToolContext
from src.tool_system.defaults import build_default_registry
from src.types.messages import UserMessage
from src.utils.abort_controller import AbortController


class TestGeneratorCleanup(unittest.TestCase):
    """F3：generator aclose 清理验证。"""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp_dir.name)
        self.registry = build_default_registry()
        self.context = ToolContext(workspace_root=self.workspace)
        self.abort = AbortController()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_aclose_mid_turn_no_exception(self):
        """消费首条消息后 aclose：不抛异常、正常结束。"""
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
        errors = []

        async def run():
            gen = query(params)
            try:
                await anext(gen)  # 消费第一条
                await gen.aclose()  # 提前关闭
            except BaseException as exc:  # noqa: BLE001 — 捕获一切确认无泄漏
                errors.append(exc)
            finally:
                await gen.aclose()

        asyncio.run(run())
        self.assertEqual(errors, [], f"aclose 抛出了异常: {errors}")

    def test_aclose_mid_tool_round_no_pending_tasks(self):
        """tool round 前 aclose：无悬挂 asyncio 任务残留。"""
        provider = MagicMock()
        provider.chat_stream_response.side_effect = NotImplementedError()
        provider.chat.return_value = ChatResponse(
            content="I'll write.",
            model="test",
            usage={"input_tokens": 10, "output_tokens": 20},
            finish_reason="tool_use",
            tool_uses=[{
                "id": "toolu_001",
                "name": "Write",
                "input": {
                    "file_path": str(self.workspace / "cleanup.txt"),
                    "content": "hello",
                },
            }],
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
        errors = []

        async def run():
            loop = asyncio.get_running_loop()
            gen = query(params)
            try:
                # 消费到 tool_use 消息后关闭（tool round 尚未开始/进行中）
                for _ in range(3):
                    try:
                        await anext(gen)
                    except StopAsyncIteration:
                        break
                await gen.aclose()
            except BaseException as exc:  # noqa: BLE001
                errors.append(exc)
            finally:
                await gen.aclose()
            # 等待任务调度稳定后检查残留（排除测试自身任务）
            await asyncio.sleep(0.05)
            current = asyncio.current_task(loop)
            pending = [
                t for t in asyncio.all_tasks(loop)
                if not t.done() and t is not current
            ]
            return pending

        pending = asyncio.run(run())
        self.assertEqual(errors, [], f"aclose 抛出了异常: {errors}")
        self.assertEqual(
            pending, [],
            f"aclose 后残留悬挂任务: {pending}",
        )

    def test_abort_before_generator_start_clean(self):
        """已 abort 的 controller：query 立即产生中断消息并正常结束（无残留）。"""
        abort = AbortController()
        abort.abort("test_abort")
        provider = MagicMock()
        provider.chat_stream_response.side_effect = NotImplementedError()
        provider.chat.return_value = ChatResponse(
            content="Should not stream",
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
            abort_controller=abort,
            max_turns=10,
        )
        collected = []

        async def run():
            async for msg in query(params):
                collected.append(msg)

        asyncio.run(run())
        interruptions = [
            m for m in collected if isinstance(m, UserMessage) and m.isMeta
        ]
        self.assertGreaterEqual(len(interruptions), 1)


if __name__ == "__main__":
    unittest.main()

"""Wave 1 F4 — recovery 差分测试（对照 reference query.ts 恢复语义）。

覆盖（reference withRetry.ts / query.ts 对应行为）：
- general retryable error（429/RateLimitError）→ 指数退避重试至成功
- 529 overloaded → 529 lane 重试（MAX_529_RETRIES=3）
- fallback model：连续 529 ≥3 次 + fallback_model 配置 → provider.model
  切换（session-sticky，不持久化），yield model_fallback 消息
- max-output tokens recovery：先 escalate（override 64K）→ 恢复消息
  （count < MAX_OUTPUT_TOKENS_RECOVERY_LIMIT=3）→ 继续

backoff sleep 在测试内被 mock（避免真实延迟），重试语义不变。
"""

import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from src.providers.base import ChatResponse
from src.query.query import QueryParams, query
from src.services.api.errors import (
    MaxOutputTokensError,
    OverloadedError,
    RateLimitError,
)
from src.tool_system.context import ToolContext
from src.tool_system.defaults import build_default_registry
from src.types.messages import (
    AssistantMessage,
    SystemMessage,
    UserMessage,
)
from src.utils.abort_controller import AbortController


def _run(coro):
    return asyncio.run(coro)


class TestRecoveryParity(unittest.TestCase):
    """F4：recovery 行为差分。"""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp_dir.name)
        self.registry = build_default_registry()
        self.context = ToolContext(workspace_root=self.workspace)
        self.abort = AbortController()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _params(self, provider):
        return QueryParams(
            messages=[UserMessage(content="Hi")],
            system_prompt="You are helpful.",
            tools=self.registry.list_tools(),
            tool_registry=self.registry,
            tool_use_context=self.context,
            provider=provider,
            abort_controller=self.abort,
            max_turns=10,
        )

    def _collect(self, params):
        collected = []

        async def run():
            async for msg in query(params):
                collected.append(msg)

        with patch("src.query.query.asyncio.sleep", new=AsyncMock()):
            _run(run())
        return collected

    def _subtype_messages(self, collected, subtype):
        return [
            m for m in collected
            if isinstance(m, SystemMessage) and m.subtype == subtype
        ]

    def test_general_retry_then_success(self):
        """general retryable error（429）：重试至成功，yield api_retry。"""
        provider = MagicMock()
        provider.chat_stream_response.side_effect = NotImplementedError()
        ok = ChatResponse(
            content="Recovered!",
            model="test",
            usage={"input_tokens": 10, "output_tokens": 5},
            finish_reason="end_turn",
            tool_uses=None,
        )
        provider.chat.side_effect = [
            RateLimitError(),  # 429 retryable
            RateLimitError(),
            ok,
        ]
        params = self._params(provider)
        collected = self._collect(params)

        retries = self._subtype_messages(collected, "api_retry")
        self.assertGreaterEqual(len(retries), 2, "应至少 yield 2 次 api_retry")
        self.assertEqual(provider.chat.call_count, 3, "应重试 2 次后成功")
        assistants = [m for m in collected if isinstance(m, AssistantMessage)]
        self.assertGreaterEqual(len(assistants), 1)
        self.assertIn("retrying", retries[0].content)

    def test_529_retry_then_success(self):
        """529 overloaded：529 lane 重试至成功。"""
        provider = MagicMock()
        provider.chat_stream_response.side_effect = NotImplementedError()
        ok = ChatResponse(
            content="Recovered!",
            model="test",
            usage={"input_tokens": 10, "output_tokens": 5},
            finish_reason="end_turn",
            tool_uses=None,
        )
        provider.chat.side_effect = [
            OverloadedError(),  # 529
            OverloadedError(),
            ok,
        ]
        params = self._params(provider)
        collected = self._collect(params)

        retries = self._subtype_messages(collected, "api_retry")
        self.assertGreaterEqual(len(retries), 2)
        self.assertIn("overloaded", retries[0].content.lower())
        self.assertEqual(provider.chat.call_count, 3)

    def test_fallback_model_switch_after_3_consecutive_529(self):
        """连续 3 次 529 + fallback_model → provider.model 切换 + 消息。"""
        provider = MagicMock()
        provider.chat_stream_response.side_effect = NotImplementedError()
        provider.model = "primary-model"
        ok = ChatResponse(
            content="Fallback ok!",
            model="fallback-model",
            usage={"input_tokens": 10, "output_tokens": 5},
            finish_reason="end_turn",
            tool_uses=None,
        )
        provider.chat.side_effect = [
            OverloadedError(),
            OverloadedError(),
            OverloadedError(),  # 第 3 次触发 fallback 切换
            ok,
        ]
        params = QueryParams(
            messages=[UserMessage(content="Hi")],
            system_prompt="You are helpful.",
            tools=self.registry.list_tools(),
            tool_registry=self.registry,
            tool_use_context=self.context,
            provider=provider,
            abort_controller=self.abort,
            max_turns=10,
            fallback_model="fallback-model",
        )
        collected = self._collect(params)

        fallbacks = self._subtype_messages(collected, "model_fallback")
        self.assertEqual(len(fallbacks), 1, "应恰好 yield 1 次 model_fallback")
        self.assertEqual(
            provider.model, "fallback-model",
            "provider.model 应切换为 fallback_model",
        )
        self.assertIn("fallback-model", fallbacks[0].content)

    def test_max_output_tokens_escalate_then_recovery(self):
        """max_output_tokens：先 escalate（override）→ 恢复消息 → 继续成功。"""
        provider = MagicMock()
        provider.chat_stream_response.side_effect = NotImplementedError()
        ok = ChatResponse(
            content="Finished!",
            model="test",
            usage={"input_tokens": 10, "output_tokens": 5},
            finish_reason="end_turn",
            tool_uses=None,
        )
        # _call_model_sync 将含 "max_output_tokens" 子串的异常分类为
        # withheld max_output_tokens 错误消息（model_call.py:833-837，
        # 子串匹配带下划线形式）
        provider.chat.side_effect = [
            MaxOutputTokensError("request failed: max_output_tokens exceeded"),
            MaxOutputTokensError("request failed: max_output_tokens exceeded"),
            ok,
        ]
        params = self._params(provider)
        collected = self._collect(params)

        # escalate（第 1 次）+ recovery（第 2 次）后第 3 次成功：
        # 调用次数证明 recovery 路径被走过（recovery 消息不 yield，
        # 直接进入下一轮 model 输入，属设计行为）
        self.assertEqual(provider.chat.call_count, 3, "escalate+recovery 后应继续成功")
        # 无 model_error 终态（recovery 未耗尽）
        model_errors = [m for m in collected if isinstance(m, SystemMessage)
                        and m.subtype == "model_error"]
        self.assertEqual(model_errors, [], "recovery 不应以 model_error 结束")
        # 最终成功完成
        assistants = [m for m in collected if isinstance(m, AssistantMessage)]
        self.assertGreaterEqual(len(assistants), 1)


if __name__ == "__main__":
    unittest.main()

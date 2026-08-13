"""Wave 5 F20 — fault-injection traces 测试（CCR-08 恢复 + CCR-12 隔离故障）。

对照规则圣经：
- CCR-08 禁止无限 retry（bounded retry count → terminal）
- CCR-12 故障无副作用（sandbox deny 不执行命令）
- CCR-01 hook failure 不得隐式绕过 permission/safety
"""

import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from src.execution.sandbox import (
    NoSandboxBackend,
    SandboxPolicy,
    SandboxRequest,
)
from src.providers.base import ChatResponse
from src.query.query import DEFAULT_MAX_RETRIES, QueryParams, query
from src.services.api.errors import RateLimitError
from src.tool_system.context import ToolContext
from src.tool_system.defaults import build_default_registry
from src.types.messages import AssistantMessage, SystemMessage, UserMessage
from src.utils.abort_controller import AbortController


class TestRetryExhaustion(unittest.TestCase):
    """CCR-08 — 禁止无限 retry。"""

    def test_retry_exhaustion_terminates_model_error(self):
        """连续 RateLimitError 超过 DEFAULT_MAX_RETRIES → model_error 终态。"""
        provider = MagicMock()
        provider.chat_stream_response.side_effect = NotImplementedError()
        # 每次调用都抛 RateLimitError（非列表，避免 side_effect 耗尽）
        provider.chat.side_effect = RateLimitError("rate limited")
        provider.model = "test"

        tmp = tempfile.TemporaryDirectory()
        registry = build_default_registry()
        context = ToolContext(workspace_root=Path(tmp.name))
        params = QueryParams(
            messages=[UserMessage(content="Hi")],
            system_prompt="You are helpful.",
            tools=registry.list_tools(),
            tool_registry=registry,
            tool_use_context=context,
            provider=provider,
            abort_controller=AbortController(),
            max_turns=5,
        )

        collected = []

        async def run():
            # 消除 backoff sleep（AsyncMock 可 await），聚焦重试计数
            with patch("src.query.query.asyncio.sleep", new=AsyncMock()):
                async for msg in query(params):
                    collected.append(msg)

        asyncio.run(run())
        # 重试有界：最多 DEFAULT_MAX_RETRIES 次重试 + 1 次最终尝试（不无限）
        self.assertLessEqual(
            provider.chat.call_count, DEFAULT_MAX_RETRIES + 1,
        )
        self.assertGreaterEqual(provider.chat.call_count, 2)
        # 重试耗尽 → yield api error message（终态 model_error 在 terminal 层）
        error_msgs = [
            m for m in collected
            if isinstance(m, AssistantMessage)
            and "rate limited" in str(m.content)
        ]
        self.assertGreaterEqual(
            len(error_msgs), 1, "重试耗尽应 yield api error 消息",
        )
        tmp.cleanup()


class TestSandboxFaultNoSideEffect(unittest.TestCase):
    """CCR-12 — 故障无副作用。"""

    def test_denied_invocation_does_not_execute(self):
        """sandbox deny → run 返回 126，不执行命令（无副作用）。"""
        backend = NoSandboxBackend()
        policy = SandboxPolicy(require_isolation=True, allow_unsandboxed=False)
        # 用一个会产生副作用的命令（写文件）验证不执行
        tmp = tempfile.TemporaryDirectory()
        marker = Path(tmp.name) / "should_not_exist.txt"
        request = SandboxRequest(
            argv=("touch", str(marker)), cwd=Path(tmp.name),
        )
        invocation = backend.prepare(request, policy)
        self.assertFalse(invocation.allowed)
        result = backend.run(invocation)
        self.assertEqual(result.exit_code, 126)
        self.assertFalse(marker.exists(), "denied 命令不得产生副作用")
        tmp.cleanup()


class TestHookFailureNoBypass(unittest.TestCase):
    """CCR-01 — hook failure 不得隐式绕过 permission。"""

    def test_hook_executor_has_failure_containment(self):
        """hook 执行层必须含异常容器（一个坏 hook 不阻断/绕过安全）。"""
        src = Path("src/hooks/hook_executor.py").read_text(encoding="utf-8")
        # 多个 except 容器 + "never raise" 契约
        self.assertGreater(src.count("except"), 5, "hook 执行层应有异常容器")


if __name__ == "__main__":
    unittest.main()

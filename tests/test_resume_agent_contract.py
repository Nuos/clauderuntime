"""Wave 3 F12 — resume_agent_background 现状锁定测试。

锁定现有行为（B3 诊断 7.3 相关）：
- race-safe re-registration：仅终态任务可 resume、claim 单赢
- transcript replay：终态 + output_file → replayed_message_count 计数
- 重建容错：transcript 损坏不抛（resume without history）

同时固化已知缺口（不冒充完成）：
- resume_agent_background 本身不驱动 model call（docstring 声明），
  run_agent 的 context_messages 已就绪但接线未完成 —— 见 11 号文档登记。
"""

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from src.agent.resume_agent import resume_agent_background
from src.agent.transcript import TranscriptWriter
from src.tasks.local_agent import LocalAgentTaskState
from src.tool_system.context import ToolContext


def _terminal_agent_state(agent_id: str, output_file: str) -> LocalAgentTaskState:
    return LocalAgentTaskState(
        id=agent_id,
        type="local_agent",
        status="completed",
        description="test agent",
        start_time=100.0,
        output_file=output_file,
        agent_id=agent_id,
        agent_type="general-purpose",
        prompt="do the thing",
        resume_run_params=SimpleNamespace(),
    )


class _DeferredTaskManager:
    def start(self, *, name, target):
        self.name = name
        self.target = target
        return SimpleNamespace(name=name)


class TestResumeAgentContract(unittest.TestCase):
    """resume_agent_background 现状锁定。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_dir = Path(self.tmp.name)
        self.context = ToolContext(workspace_root=self.tmp_dir)
        self.context.task_manager = _DeferredTaskManager()

    def tearDown(self):
        self.tmp.cleanup()

    def _seed_transcript(self, path: Path, n: int = 3) -> None:
        writer = TranscriptWriter(path)
        for i in range(n):
            writer.append({"role": "user", "content": f"msg {i}"})

    def test_resume_task_not_found(self):
        """runtime 无此任务 → resumed=False + 原因。"""
        result = self._run_resume("agent_missing")
        self.assertFalse(result.resumed)
        self.assertIn("not found", result.reason)

    def test_resume_non_terminal_denied(self):
        """非终态任务不可 resume（race guard）。"""
        state = LocalAgentTaskState(
            id="agent_running", type="local_agent", status="running",
            description="running", start_time=100.0, output_file="",
            agent_id="agent_running",
        )
        self.context.runtime_tasks.upsert(state)
        result = self._run_resume("agent_running")
        self.assertFalse(result.resumed)
        self.assertIn("not terminal", result.reason)

    def test_resume_terminal_replays_transcript(self):
        """终态 + transcript → resumed=True + replay 计数。"""
        transcript = self.tmp_dir / "agent_done.jsonl"
        self._seed_transcript(transcript)
        state = _terminal_agent_state("agent_done", str(transcript))
        self.context.runtime_tasks.upsert(state)
        result = self._run_resume("agent_done")
        self.assertTrue(result.resumed, f"resume 失败: {result.reason}")
        self.assertGreater(result.replayed_message_count, 0)

    def test_resume_reconstruction_tolerant(self):
        """transcript 损坏 → 不抛异常，仍 resume（无历史）。"""
        transcript = self.tmp_dir / "agent_corrupt.jsonl"
        transcript.write_text('{"role": "user", "content": "partial', encoding="utf-8")
        state = _terminal_agent_state("agent_corrupt", str(transcript))
        self.context.runtime_tasks.upsert(state)
        result = self._run_resume("agent_corrupt")
        self.assertTrue(result.resumed, "损坏 transcript 不应阻断 resume")

    def _run_resume(self, agent_id: str):
        import asyncio

        return asyncio.run(resume_agent_background(
            agent_id=agent_id, prompt="resume me", context=self.context,
        ))


if __name__ == "__main__":
    unittest.main()

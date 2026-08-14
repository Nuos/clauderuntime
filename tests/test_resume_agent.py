"""验证后台 Agent 单赢恢复、transcript 重放和跨进程运行依赖重建。"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.agent.resume_agent import resume_agent_background
from src.agent.resume_metadata import metadata_path_for_output
from src.agent.transcript import TranscriptWriter, get_agent_transcript_path
from src.tasks.local_agent import (
    LocalAgentTaskState,
    complete_agent_task,
    fail_agent_task,
    register_async_agent,
)
from src.tasks_core import generate_task_id
from src.tool_system.context import ToolContext
from src.tool_system.defaults import build_default_registry


@pytest.fixture(autouse=True)
def _isolate_resume_storage(tmp_path: Path, monkeypatch) -> None:
    """把 transcript 和恢复元数据限制在单个测试目录，禁止污染用户配置。"""
    monkeypatch.setenv("CLAWCODEX_CONFIG_DIR", str(tmp_path / "config"))


class _DeferredTaskManager:
    """Capture the background target without running it in state-only tests."""

    def start(self, *, name, target):
        self.name = name
        self.target = target
        return SimpleNamespace(name=name)


def _make_terminal_agent(ctx: ToolContext, terminal_status: str = "completed") -> str:
    """Spawn → terminal. Returns the agent_id."""
    agent_id = generate_task_id("local_agent")
    register_async_agent(
        agent_id=agent_id, description="x", prompt="initial",
        agent_type="general-purpose",
        resume_run_params=SimpleNamespace(),
        registry=ctx.runtime_tasks,
    )
    ctx.task_manager = _DeferredTaskManager()
    if terminal_status == "completed":
        complete_agent_task(agent_id, result_text="done", registry=ctx.runtime_tasks)
    elif terminal_status == "failed":
        fail_agent_task(agent_id, error="boom", registry=ctx.runtime_tasks)
    return agent_id


# ---------------------------------------------------------------------------
# Happy path — terminal task → resumed
# ---------------------------------------------------------------------------


def test_resume_terminal_agent_returns_resumed_true(tmp_path: Path) -> None:
    ctx = ToolContext(workspace_root=tmp_path)
    agent_id = _make_terminal_agent(ctx)

    result = asyncio.run(resume_agent_background(
        agent_id=agent_id, prompt="wake up", context=ctx,
    ))
    assert result.resumed is True
    assert result.agent_id == agent_id

    refreshed = ctx.runtime_tasks.get(agent_id)
    assert isinstance(refreshed, LocalAgentTaskState)
    assert refreshed.status == "running"
    assert refreshed.prompt == "wake up"


def test_resume_carries_resume_prompt_into_fresh_state(tmp_path: Path) -> None:
    ctx = ToolContext(workspace_root=tmp_path)
    agent_id = _make_terminal_agent(ctx, terminal_status="failed")

    asyncio.run(resume_agent_background(
        agent_id=agent_id, prompt="retry the failed work", context=ctx,
    ))
    refreshed = ctx.runtime_tasks.get(agent_id)
    assert refreshed.prompt == "retry the failed work"


def test_resume_reads_transcript_via_transcript_reader(tmp_path: Path) -> None:
    """DIP claim — ``resume_agent_background`` consumes the transcript
    via ``TranscriptReader``. Verify by writing some entries to the
    transcript pre-resume and asserting ``replayed_message_count``."""
    ctx = ToolContext(workspace_root=tmp_path)
    agent_id = _make_terminal_agent(ctx)

    # Write 3 entries to the transcript (whatever shape — the reader
    # just yields parseable JSON objects).
    transcript_path = get_agent_transcript_path(agent_id)
    with TranscriptWriter(transcript_path) as w:
        w.append({"role": "user", "content": "hi"})
        w.append({"role": "assistant", "content": "hello"})
        w.append({"role": "user", "content": "follow-up"})

    result = asyncio.run(resume_agent_background(
        agent_id=agent_id, prompt="continue", context=ctx,
    ))
    assert result.resumed is True
    assert result.replayed_message_count == 3


def test_resume_handles_missing_transcript_gracefully(tmp_path: Path) -> None:
    """Transcript file may not exist (e.g., the agent crashed before
    the writer opened). Resume should still succeed; replay count is 0."""
    ctx = ToolContext(workspace_root=tmp_path)
    agent_id = _make_terminal_agent(ctx)

    # Don't create the transcript file. ``register_async_agent``
    # populated ``output_file`` with the path, but no writes have
    # happened.
    result = asyncio.run(resume_agent_background(
        agent_id=agent_id, prompt="x", context=ctx,
    ))
    assert result.resumed is True
    assert result.replayed_message_count == 0


def test_resume_without_live_dependencies_fails_without_false_running_state(tmp_path: Path) -> None:
    ctx = ToolContext(workspace_root=tmp_path)
    agent_id = generate_task_id("local_agent")
    register_async_agent(
        agent_id=agent_id, description="x", prompt="initial",
        agent_type="general-purpose", registry=ctx.runtime_tasks,
    )
    complete_agent_task(agent_id, result_text="done", registry=ctx.runtime_tasks)

    result = asyncio.run(resume_agent_background(
        agent_id=agent_id, prompt="continue", context=ctx,
    ))

    assert result.resumed is False
    assert "dependencies" in result.reason
    assert ctx.runtime_tasks.get(agent_id).status == "completed"


def test_restart_rebuilds_dependencies_from_current_runtime(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("CLAWCODEX_CONFIG_DIR", str(tmp_path / "config"))
    workspace = tmp_path / "repo"
    workspace.mkdir()
    original_context = ToolContext(workspace_root=workspace)
    agent_id = generate_task_id("local_agent")
    recipe = SimpleNamespace(parent_context=original_context, api_key="do-not-persist")
    state = register_async_agent(
        agent_id=agent_id,
        description="durable",
        prompt="initial",
        agent_type="general-purpose",
        model="test-model",
        resume_run_params=recipe,
        registry=original_context.runtime_tasks,
    )
    complete_agent_task(agent_id, result_text="done", registry=original_context.runtime_tasks)
    metadata_text = metadata_path_for_output(state.output_file).read_text(encoding="utf-8")
    assert "do-not-persist" not in metadata_text
    assert "api_key" not in metadata_text

    restarted_context = ToolContext(workspace_root=workspace)
    restarted_context.task_manager = _DeferredTaskManager()
    restarted_context.tool_registry = build_default_registry()
    current_provider = SimpleNamespace(model="current-model")
    setattr(restarted_context, "_active_provider", current_provider)

    result = asyncio.run(resume_agent_background(
        agent_id=agent_id,
        prompt="continue after restart",
        context=restarted_context,
    ))

    assert result.resumed is True
    restored = restarted_context.runtime_tasks.get(agent_id)
    assert restored.status == "running"
    rebuilt = restored.resume_run_params
    assert rebuilt.provider is current_provider
    assert rebuilt.tool_registry is restarted_context.tool_registry
    assert rebuilt.permission_mode_override is None
    assert rebuilt.system_prompt_override is None


def test_restart_rejects_missing_recorded_worktree(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("CLAWCODEX_CONFIG_DIR", str(tmp_path / "config"))
    workspace = tmp_path / "repo"
    workspace.mkdir()
    original_context = ToolContext(workspace_root=workspace)
    original_context.worktree_root = tmp_path / "deleted-worktree"
    agent_id = generate_task_id("local_agent")
    register_async_agent(
        agent_id=agent_id,
        description="durable",
        prompt="initial",
        agent_type="general-purpose",
        resume_run_params=SimpleNamespace(parent_context=original_context),
        registry=original_context.runtime_tasks,
    )
    complete_agent_task(agent_id, result_text="done", registry=original_context.runtime_tasks)

    restarted_context = ToolContext(workspace_root=workspace)
    restarted_context.tool_registry = build_default_registry()
    setattr(restarted_context, "_active_provider", SimpleNamespace(model="current"))
    result = asyncio.run(resume_agent_background(
        agent_id=agent_id,
        prompt="continue",
        context=restarted_context,
    ))

    assert result.resumed is False
    assert "workspace is missing" in result.reason
    assert restarted_context.runtime_tasks.get(agent_id).status == "completed"


def test_resume_drives_agent_and_persists_terminal_result(tmp_path: Path, monkeypatch) -> None:
    import importlib

    from src.types.messages import AssistantMessage

    ctx = ToolContext(workspace_root=tmp_path)
    agent_id = generate_task_id("local_agent")
    recipe = SimpleNamespace()
    register_async_agent(
        agent_id=agent_id, description="x", prompt="initial",
        agent_type="general-purpose", resume_run_params=recipe,
        registry=ctx.runtime_tasks,
    )
    complete_agent_task(agent_id, result_text="done", registry=ctx.runtime_tasks)
    ran = []

    async def fake_run_agent(params):
        ran.append(params)
        yield AssistantMessage(content="resumed answer")

    run_agent_module = importlib.import_module("src.agent.run_agent")
    monkeypatch.setattr(run_agent_module, "run_agent", fake_run_agent)
    result = asyncio.run(resume_agent_background(
        agent_id=agent_id, prompt="continue now", context=ctx,
    ))
    assert result.resumed is True

    for task in ctx.task_manager.list():
        task.thread.join(timeout=2.0)
    final = ctx.runtime_tasks.get(agent_id)
    assert ran and ran[0].prompt == "continue now"
    assert final.status == "completed"
    assert final.result_text == "resumed answer"


# ---------------------------------------------------------------------------
# No-op paths — task missing / not terminal / not local_agent
# ---------------------------------------------------------------------------


def test_resume_returns_noop_for_missing_task(tmp_path: Path) -> None:
    ctx = ToolContext(workspace_root=tmp_path)
    result = asyncio.run(resume_agent_background(
        agent_id="a-ghost", prompt="x", context=ctx,
    ))
    assert result.resumed is False
    assert "not found" in result.reason.lower()


def test_resume_returns_noop_for_running_task(tmp_path: Path) -> None:
    """Auto-resume only fires for terminal tasks — running ones are
    left alone."""
    ctx = ToolContext(workspace_root=tmp_path)
    agent_id = generate_task_id("local_agent")
    register_async_agent(
        agent_id=agent_id, description="x", prompt="x",
        agent_type="general-purpose", registry=ctx.runtime_tasks,
    )
    result = asyncio.run(resume_agent_background(
        agent_id=agent_id, prompt="x", context=ctx,
    ))
    assert result.resumed is False
    assert "not terminal" in result.reason.lower()


def test_resume_returns_noop_for_non_local_agent_task(tmp_path: Path) -> None:
    """A bash task at the same id wouldn't be a local_agent — resume
    rejects it cleanly."""
    from src.tasks.local_shell import LocalShellTaskState
    import time

    ctx = ToolContext(workspace_root=tmp_path)
    state = LocalShellTaskState(
        id="b-shell",
        type="local_bash",
        status="completed",
        description="x",
        start_time=time.time(),
        output_file="/tmp/x",
        command="echo x",
        cwd="/tmp",
    )
    ctx.runtime_tasks.upsert(state)

    result = asyncio.run(resume_agent_background(
        agent_id="b-shell", prompt="x", context=ctx,
    ))
    assert result.resumed is False
    assert "not local_agent" in result.reason


# ---------------------------------------------------------------------------
# Race guard — atomic claim
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_concurrent_resume_callers_only_one_wins(tmp_path: Path) -> None:
    """asyncio.gather() races two concurrent ``resume_agent_background``
    calls against the same dead agent_id. Exactly one returns
    ``resumed=True``; the other returns ``resumed=False`` with the
    "another caller is resuming" reason.

    The atomic ``runtime_tasks.update`` mutator that performs the
    check + flip in one breath is what makes this race-safe — without
    it, both callers would proceed past the terminal-state check,
    and the second ``register_async_agent`` would silently overwrite
    the first."""
    ctx = ToolContext(workspace_root=tmp_path)
    agent_id = _make_terminal_agent(ctx)

    results = await asyncio.gather(
        resume_agent_background(
            agent_id=agent_id, prompt="A", context=ctx,
        ),
        resume_agent_background(
            agent_id=agent_id, prompt="B", context=ctx,
        ),
    )

    won = [r for r in results if r.resumed]
    lost = [r for r in results if not r.resumed]
    assert len(won) == 1, f"expected exactly 1 resumer; got {len(won)}"
    assert len(lost) == 1
    # Loser's reason is one of two valid outcomes:
    # * "another caller is resuming" — winner was mid-resume when
    #   loser hit the registry (won the claim race but hadn't
    #   finished register_async_agent yet).
    # * "task is 'running', not terminal" — winner had already
    #   re-registered the fresh state before loser even read.
    # Both prove the second resume correctly did NOT fire — that's
    # what the race guard is for. Assert either is present.
    loser_reason = lost[0].reason.lower()
    assert (
        "another caller is resuming" in loser_reason
        or "not terminal" in loser_reason
    ), f"unexpected loser reason: {loser_reason!r}"

    # Final state has the winner's prompt.
    #
    # Critic Chunk-F N1 note: this race test calls ``resume_agent_background``
    # directly, so loser callers return a no-op ``ResumeResult`` —
    # they don't carry the loser's message into pending_messages
    # (that's SendMessage's job, exercised at
    # ``tests/tool_system/test_send_message.py::
    # test_concurrent_resume_race_only_one_winner`` which asserts the
    # loser's message lands in ``final.pending_messages``). Keeping
    # the assertions narrow here so the test focuses on the resume
    # primitive's race guard, not the SendMessage flow.
    final = ctx.runtime_tasks.get(agent_id)
    assert final.status == "running"
    assert final.prompt in {"A", "B"}


# ---------------------------------------------------------------------------
# is_resuming bookkeeping
# ---------------------------------------------------------------------------


def test_resume_resets_is_resuming_on_fresh_state(tmp_path: Path) -> None:
    """After a successful resume, the fresh state has
    ``is_resuming=False`` so a future re-resume can fire if this run
    also terminates."""
    ctx = ToolContext(workspace_root=tmp_path)
    agent_id = _make_terminal_agent(ctx)

    asyncio.run(resume_agent_background(
        agent_id=agent_id, prompt="first-resume", context=ctx,
    ))
    after_first = ctx.runtime_tasks.get(agent_id)
    assert after_first.is_resuming is False

    # Drive to terminal again, resume again — works because the
    # is_resuming flag was reset.
    complete_agent_task(agent_id, result_text="re-done", registry=ctx.runtime_tasks)
    second = asyncio.run(resume_agent_background(
        agent_id=agent_id, prompt="second-resume", context=ctx,
    ))
    assert second.resumed is True

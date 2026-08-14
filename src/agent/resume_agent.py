"""跨进程恢复已经终止或因服务重启中断的本地后台 Agent。

恢复先从 JSONL transcript 重建消息，再从安全元数据恢复任务身份；provider、工具
注册表、Agent 定义、权限上下文和系统提示均从当前进程重新解析。并发调用通过
运行时注册表的一次原子更新选出唯一恢复者，其他调用方不会重复启动 Agent。
"""
from __future__ import annotations

import asyncio
import copy
import logging
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, TYPE_CHECKING

from src.agent.transcript import TranscriptReader
from src.tasks.local_agent import (
    LocalAgentTaskState,
    complete_agent_task,
    fail_agent_task,
    register_async_agent,
)
from src.tasks_core import is_terminal_task_status

if TYPE_CHECKING:
    from src.task_registry import RuntimeTaskRegistry
    from src.tool_system.context import ToolContext

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ResumeResult:
    """Outcome of a resume attempt.

    * ``resumed``: True iff this caller won the race and re-spawned
      the agent. False means another caller got there first or the
      target agent isn't actually terminal.
    * ``agent_id``: the resumed agent's id (same as the original).
    * ``output_file``: transcript path on disk.
    * ``replayed_message_count``: number of messages reconstructed
      from the transcript.
    * ``reason``: human-readable status (only populated on the loser
      / no-op paths).
    """

    resumed: bool
    agent_id: str
    output_file: str = ""
    replayed_message_count: int = 0
    reason: str = ""


def _claim_resume(
    agent_id: str,
    runtime_tasks: "RuntimeTaskRegistry",
) -> tuple[bool, LocalAgentTaskState | None]:
    """Atomic check-and-claim — race-safe resume gate.

    Returns ``(won, prev_state)``:
    * ``(True, terminal_state)`` — caller is the resume winner; the
      registry entry now has ``is_resuming=True`` so concurrent
      callers see the terminal flag and back off.
    * ``(False, None)`` — caller lost (or task isn't resumable).

    The ``is_resuming`` bookkeeping lives on
    ``LocalAgentTaskState.is_resuming`` (Chunk-F field; the dataclass
    grew the flag for this WI).

    **Load-bearing invariant (critic Chunk-F C1):** the path from this
    helper to ``register_async_agent`` (in
    ``resume_agent_background``) MUST stay synchronous. Loser callers
    rely on observing the winner's *running* fresh state — they fall
    back to ``queue_pending_message``, which refuses terminal states.
    If a future refactor makes ``_reconstruct_messages_from_transcript``
    async (e.g., streaming reads of large transcripts), the winner
    yields control mid-path; the loser then observes
    ``is_resuming=True`` on a still-terminal state and the
    ``queue_pending_message`` no-ops, silently dropping the loser's
    message. If async is needed later, the fix is to gate the
    loser's ``queue_pending_message`` with a state-refresh-loop that
    waits for the winner to land the running state.
    """
    won = False
    captured: LocalAgentTaskState | None = None

    def _maybe_claim(prev: Any) -> Any:
        nonlocal won, captured
        if not isinstance(prev, LocalAgentTaskState):
            return prev
        if not is_terminal_task_status(prev.status):
            return prev  # not terminal — nothing to resume
        if getattr(prev, "is_resuming", False):
            return prev  # someone else is already resuming
        won = True
        captured = prev
        return replace(prev, is_resuming=True)

    runtime_tasks.update(agent_id, _maybe_claim)
    return won, captured


def _reconstruct_messages_from_transcript(transcript_path: str) -> list[Any]:
    """Read the JSONL transcript and return parseable message objects.

    Tolerant of trailing partial lines (writer-crashed-mid-write —
    the same case the chapter-correct ``TranscriptReader`` already
    handles). Returns the raw dict / Message objects that the reader
    yields; the caller decides how to hydrate them into typed
    ``Message`` subclasses.
    """
    return TranscriptReader(transcript_path).read_all()


def _restore_state_from_metadata(
    agent_id: str,
    runtime: "RuntimeTaskRegistry",
) -> LocalAgentTaskState | None:
    """在进程内注册表为空时，从磁盘元数据重建可原子认领的终态。"""
    from src.agent.resume_metadata import load_metadata
    from src.agent.transcript import get_agent_transcript_path

    try:
        metadata = load_metadata(get_agent_transcript_path(agent_id))
    except ValueError:
        return None
    if metadata is None or metadata.agent_id != agent_id:
        return None
    status = metadata.status
    if not is_terminal_task_status(status):
        # 进程重启后旧的 running 状态不再对应任何执行线程，必须先视为失败终态，
        # 再由本次调用重新认领，不能把磁盘 running 直接当作仍在执行。
        status = "failed"
    state = LocalAgentTaskState(
        id=agent_id,
        type="local_agent",
        status=status,
        description=metadata.description,
        start_time=time.time(),
        output_file=metadata.output_file,
        agent_id=agent_id,
        agent_type=metadata.agent_type,
        prompt=metadata.initial_prompt,
        model=metadata.model,
        tool_use_id=metadata.tool_use_id,
        error="previous process ended before task reached a durable terminal state"
        if metadata.status == "running" else None,
    )
    runtime.upsert(state)
    return state


def _rebuild_run_params_from_current_runtime(
    state: LocalAgentTaskState,
    context: "ToolContext",
) -> Any:
    """用当前进程依赖重建 RunAgentParams，禁止复用持久化实时对象。"""
    from src.agent.agent_definitions import (
        find_agent_by_type,
        get_built_in_agents,
    )
    from src.agent.run_agent import RunAgentParams
    from src.agent.resume_metadata import load_metadata

    metadata = load_metadata(state.output_file)
    if metadata is not None:
        expected_root = metadata.worktree_root or metadata.workspace_root
        if expected_root is not None and not Path(expected_root).is_dir():
            raise RuntimeError(f"recorded workspace is missing: {expected_root}")
        current_roots = {
            Path(context.workspace_root).resolve(),
            Path(context.worktree_root).resolve()
            if context.worktree_root is not None else Path(context.workspace_root).resolve(),
        }
        if expected_root is not None and Path(expected_root).resolve() not in current_roots:
            raise RuntimeError("current workspace does not match the recorded worktree")

    provider = getattr(context, "_active_provider", None)
    registry = getattr(context, "tool_registry", None)
    if provider is None:
        raise RuntimeError("current provider factory is unavailable")
    if registry is None:
        raise RuntimeError("current tool registry is unavailable")

    definitions = list(get_built_in_agents())
    configured = getattr(context.options, "agent_definitions", {})
    if isinstance(configured, dict):
        definitions.extend(
            definition for definition in configured.values()
            if definition is not None
        )
    definition = find_agent_by_type(definitions, state.agent_type)
    if definition is None:
        raise RuntimeError(f"current agent definition {state.agent_type!r} is unavailable")

    return RunAgentParams(
        parent_context=context,
        agent_definition=definition,
        prompt=state.prompt,
        available_tools=registry.list_tools(),
        tool_registry=registry,
        provider=provider,
        model=state.model,
        agent_id=state.agent_id,
        is_async=True,
        permission_mode_override=None,
        system_prompt_override=None,
    )


async def resume_agent_background(
    *,
    agent_id: str,
    prompt: str,
    context: "ToolContext",
) -> ResumeResult:
    """Re-spawn a stopped agent's background lifecycle with ``prompt``
    as the resume message.

    Returns a ``ResumeResult`` describing the outcome:

    * Winner of the race → ``resumed=True``; the registry holds a
      fresh ``LocalAgentTaskState`` for ``agent_id`` with status
      ``"running"``. The transcript is read from disk and counted in
      ``replayed_message_count`` for the caller's diagnostics.
    * Loser → ``resumed=False``, ``reason`` describes the situation.
      Caller should typically follow up with ``queue_pending_message``
      to deliver the prompt to the now-running agent.
    * Target not terminal / not present → ``resumed=False`` with a
      reason like ``"task not terminal"`` or ``"task not found"``.

    返回成功表示已经启动真实的后台 ``run_agent`` 生命周期。如果原任务的运行依赖
    已丢失（例如服务进程重启），则恢复终态并向调用方返回明确失败，避免业务侧看到
    虚假的“运行中”状态。
    """
    runtime = context.runtime_tasks
    state = runtime.get(agent_id)

    if state is None:
        state = _restore_state_from_metadata(agent_id, runtime)
        if state is None:
            return ResumeResult(
                resumed=False, agent_id=agent_id,
                reason="task not found in runtime_tasks or durable metadata",
            )

    if not isinstance(state, LocalAgentTaskState):
        return ResumeResult(
            resumed=False, agent_id=agent_id,
            reason=f"task type {state.type!r} is not local_agent",
        )

    if not is_terminal_task_status(state.status):
        return ResumeResult(
            resumed=False, agent_id=agent_id,
            reason=f"task is {state.status!r}, not terminal",
        )

    won, prev = _claim_resume(agent_id, runtime)
    if not won or prev is None:
        # Another caller won the race; the registry entry is now
        # ``is_resuming=True`` (and likely already replaced by the
        # winner with a fresh running state). Return a no-op so the
        # SendMessage caller knows to fall back to queueing.
        return ResumeResult(
            resumed=False, agent_id=agent_id,
            reason="another caller is resuming; queue your message instead",
        )

    # Reconstruct the prior conversation. Errors here are non-fatal —
    # the resumed run still gets the new prompt; it just lacks the
    # historical context.
    transcript_path = prev.output_file
    replayed: list[Any] = []
    try:
        replayed = _reconstruct_messages_from_transcript(transcript_path)
    except Exception:
        logger.exception(
            "transcript reconstruction failed for %s; resuming without history",
            agent_id,
        )

    recipe = getattr(prev, "resume_run_params", None)
    if recipe is None:
        try:
            recipe = _rebuild_run_params_from_current_runtime(prev, context)
        except RuntimeError as exc:
            recipe = None
            rebuild_error = str(exc)
    else:
        rebuild_error = ""
    if recipe is None:
        runtime.update(
            agent_id,
            lambda current: replace(current, is_resuming=False)
            if isinstance(current, LocalAgentTaskState) else current,
        )
        return ResumeResult(
            resumed=False,
            agent_id=agent_id,
            replayed_message_count=len(replayed),
            reason=(
                f"live resume dependencies are unavailable: {rebuild_error}; "
                "spawn a fresh agent"
            ),
        )

    from src.types.messages import Message, message_from_dict
    from src.utils.abort_controller import AbortController

    hydrated: list[Message] = []
    for raw in replayed:
        if isinstance(raw, Message):
            hydrated.append(raw)
        elif isinstance(raw, dict):
            try:
                hydrated.append(message_from_dict(raw))
            except (TypeError, ValueError):
                logger.warning("skipping invalid resumed message for %s", agent_id)

    run_params = copy.copy(recipe)
    run_params.prompt = prompt
    run_params.agent_id = agent_id
    run_params.is_async = True
    run_params.context_messages = hydrated
    run_params.abort_controller = AbortController()

    # Re-register the agent with a fresh running state. ``register_async_agent``
    # ``upsert``s, replacing the terminal entry. The new state has
    # ``is_resuming=False`` (default) so a future resume can fire if
    # this run also completes. Carry the resume ``prompt`` into
    # pending_messages so the resumed run picks it up at its first
    # tool-round drain (chapter-correct behavior — Chunk D / WI-3.3).
    fresh_state = register_async_agent(
        agent_id=agent_id,
        description=prev.description,
        prompt=prompt,  # the SendMessage payload is the resume prompt
        agent_type=prev.agent_type,
        selected_agent=prev.selected_agent,
        model=prev.model,
        tool_use_id=prev.tool_use_id,
        abort_controller=run_params.abort_controller,
        resume_run_params=run_params,
        registry=runtime,
    )

    async def _drive_resumed_run() -> None:
        from src.agent.run_agent import run_agent
        from src.agent.transcript import TranscriptWriter
        from src.utils.task_notification import enqueue_agent_notification

        messages: list[Message] = []
        transcript: TranscriptWriter | None = None
        try:
            transcript = TranscriptWriter(fresh_state.output_file)
            async for message in run_agent(run_params):
                messages.append(message)
                transcript.append(message)

            result_text = ""
            for message in reversed(messages):
                if getattr(message, "role", None) != "assistant":
                    continue
                content = getattr(message, "content", "")
                if isinstance(content, str):
                    result_text = content.strip()
                elif isinstance(content, list):
                    result_text = "\n".join(
                        str(block.get("text", ""))
                        for block in content
                        if isinstance(block, dict) and block.get("type") == "text"
                    ).strip()
                if result_text:
                    break
            result_text = result_text or "(Subagent completed with no textual output.)"
            complete_agent_task(agent_id, result_text=result_text, registry=runtime)
            enqueue_agent_notification(
                task_id=agent_id,
                description=prev.description,
                status="completed",
                output_file=fresh_state.output_file,
                final_message=result_text,
                registry=runtime,
            )
        except Exception as exc:
            fail_agent_task(agent_id, error=str(exc), registry=runtime)
            enqueue_agent_notification(
                task_id=agent_id,
                description=prev.description,
                status="failed",
                output_file=fresh_state.output_file,
                error=str(exc),
                registry=runtime,
            )
            logger.exception("resumed agent %s failed", agent_id)
        finally:
            if transcript is not None:
                transcript.close()

    def _runner(_stop_event: Any) -> None:
        asyncio.run(_drive_resumed_run())

    context.task_manager.start(name=f"agent-resume:{agent_id}", target=_runner)

    return ResumeResult(
        resumed=True,
        agent_id=agent_id,
        output_file=fresh_state.output_file,
        replayed_message_count=len(replayed),
        reason="",
    )


__all__ = [
    "ResumeResult",
    "resume_agent_background",
]

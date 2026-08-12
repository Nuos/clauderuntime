"""Wave 1 F1 — 9-step turn trace（独立模块，最小侵入挂接）。

提供一次 agent turn 的 9 步追踪（与 B3 规则圣经 §7 的 9-step
Trace 完全对应）：

    1 settings_resolution     Settings Resolution
    2 mutable_state_init      Mutable State Initialization
    3 context_assembly        Context Assembly
    4 pre_model_shapers       Pre-model Context Shapers
    5 model_call              Model Call / Streaming
    6 tool_dispatch           Tool-use Dispatch
    7 permission_gate         Permission / Authorization Gate
    8 tool_execution          Tool Execution + Result Collection
    9 stop_continue           Stop / Continue Decision

默认关闭（``enabled=False`` 时 emit 为近零开销的条件守卫，不分配、
不记录），由 ``QueryParams.trace_steps`` 显式开启。查询循环只通过
:meth:`TurnTracer.emit` 打点，不改变循环控制流。

Inputs:
    enabled — 是否记录 trace；entries — 已记录条目（列表）

Outputs:
    TurnTracer.finish() 返回记录快照；step_sequence() 返回按首现顺序
    去重的 step 名序列（用于断言 9-step 顺序）。
"""

from __future__ import annotations

from dataclasses import dataclass, field


class TURN_STEPS:
    """9 步常量（B3 9-step Trace 的 step 名）。"""

    SETTINGS_RESOLUTION = "settings_resolution"
    MUTABLE_STATE_INIT = "mutable_state_init"
    CONTEXT_ASSEMBLY = "context_assembly"
    PRE_MODEL_SHAPERS = "pre_model_shapers"
    MODEL_CALL = "model_call"
    TOOL_DISPATCH = "tool_dispatch"
    PERMISSION_GATE = "permission_gate"
    TOOL_EXECUTION = "tool_execution"
    STOP_CONTINUE = "stop_continue"


# 规范顺序（9-step 唯一事实源，测试据此断言）
CANONICAL_STEP_ORDER: tuple[str, ...] = (
    TURN_STEPS.SETTINGS_RESOLUTION,
    TURN_STEPS.MUTABLE_STATE_INIT,
    TURN_STEPS.CONTEXT_ASSEMBLY,
    TURN_STEPS.PRE_MODEL_SHAPERS,
    TURN_STEPS.MODEL_CALL,
    TURN_STEPS.TOOL_DISPATCH,
    TURN_STEPS.PERMISSION_GATE,
    TURN_STEPS.TOOL_EXECUTION,
    TURN_STEPS.STOP_CONTINUE,
)


@dataclass(frozen=True)
class TraceEntry:
    """单条 9-step 记录。"""

    step: str
    turn: int
    detail: str = ""


class TurnTracer:
    """9-step turn tracer（条件守卫，默认零开销）。"""

    def __init__(self, enabled: bool = False) -> None:
        self._enabled = enabled
        self._entries: list[TraceEntry] = []

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def entries(self) -> list[TraceEntry]:
        """已记录条目（实时视图，测试与诊断用）。"""
        return self._entries

    def emit(self, step: str, turn: int, detail: str = "") -> None:
        """记录一步；disabled 时不做任何分配。"""
        if self._enabled:
            self._entries.append(TraceEntry(step=step, turn=turn, detail=detail))

    def finish(self) -> list[TraceEntry]:
        """返回记录快照副本（循环结束后调用）。"""
        return list(self._entries)

    def step_sequence(self) -> list[str]:
        """按首现顺序去重的 step 名序列（断言 9-step 顺序用）。"""
        seen: list[str] = []
        for entry in self._entries:
            if entry.step not in seen:
                seen.append(entry.step)
        return seen

    def turn_steps(self, turn: int) -> list[str]:
        """指定 turn 内记录的 step 名序列（首现去重）。"""
        seen: list[str] = []
        for entry in self._entries:
            if entry.turn == turn and entry.step not in seen:
                seen.append(entry.step)
        return seen

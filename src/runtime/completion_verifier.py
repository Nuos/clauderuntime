"""B7 W6 — completion verifier protocol (minimal wiring).

Eval / Completion Law (Behavior Bible §Q): a model saying "done" is not task
completion. The long-term pipeline is fixed as::

    Task Contract → Execution Trace → Verifier → Evidence Artifact
      → Completion Decision

Freeze-before scope (P1 spec §4): define the protocol and minimal wiring
only — no large evaluation platform. This module provides the shared types
and a structural verifier that checks the trace/evidence WITHOUT asking the
model to grade itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol, Sequence, runtime_checkable


class CompletionStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    INDETERMINATE = "indeterminate"


@dataclass(frozen=True)
class CompletionDecision:
    status: CompletionStatus
    reasons: tuple[str, ...]
    evidence_refs: tuple[str, ...] = ()


@runtime_checkable
class CompletionVerifier(Protocol):
    """Verifies task completion from contract + trace + evidence.

    Implementations must consume the task contract and execution trace;
    they must not require the model to re-grade itself.
    """

    def verify(
        self,
        task_contract: Any,
        execution_trace: Any,
        evidence: Sequence[Any],
    ) -> CompletionDecision: ...


class StructuralCompletionVerifier:
    """Minimal verifier: terminal-state + evidence presence checks.

    This is intentionally NOT an eval platform. It answers the narrow
    question "does the trace show the task reached a terminal state and is
    there at least one evidence artifact?", which is the wiring anchor for
    future scenario evaluators (see ``machine/owner-map.yaml``:
    completion_decision = CompletionVerifier).
    """

    def verify(
        self,
        task_contract: Any,
        execution_trace: Any,
        evidence: Sequence[Any],
    ) -> CompletionDecision:
        reasons: list[str] = []
        evidence_refs: list[str] = []
        terminal = None
        if execution_trace is not None:
            terminal = getattr(execution_trace, "terminal_status", None) or getattr(
                execution_trace, "status", None
            )
        if terminal in (None, "running", "pending", ""):
            reasons.append("trace has no terminal status")
        elif terminal in ("completed", "success", "passed", "succeeded", "done"):
            reasons.append(f"trace terminal status: {terminal}")
        else:
            reasons.append(f"trace terminal status: {terminal}")

        evidence_list = list(evidence or ())
        for item in evidence_list:
            ref = item if isinstance(item, str) else getattr(item, "path", None) or str(item)
            if ref:
                evidence_refs.append(ref)
        if not evidence_refs:
            reasons.append("no evidence artifacts")

        if terminal in ("completed", "success", "passed", "succeeded", "done") and evidence_refs:
            return CompletionDecision(
                status=CompletionStatus.PASS,
                reasons=tuple(reasons),
                evidence_refs=tuple(evidence_refs),
            )
        if terminal in ("failed", "error", "cancelled", "aborted"):
            return CompletionDecision(
                status=CompletionStatus.FAIL,
                reasons=tuple(reasons),
                evidence_refs=tuple(evidence_refs),
            )
        return CompletionDecision(
            status=CompletionStatus.INDETERMINATE,
            reasons=tuple(reasons),
            evidence_refs=tuple(evidence_refs),
        )

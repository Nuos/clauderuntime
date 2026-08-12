"""Phase B — Loop Governance Exit Gate tests.

The detailed behavior tests live next to their modules; this gate pins the
cross-cutting invariants the development plan calls out: stop reasons are
explicit, retry reasons are explicit, and budget checks are deterministic.
"""

from __future__ import annotations

from typing import get_args

from src.query import terminal, transitions
from src.query.budget import BudgetGuard
from src.query.query import DEFAULT_MAX_RETRIES, MAX_529_RETRIES


def test_terminal_reasons_have_one_canonical_source() -> None:
    expected = {
        "blocking_limit",
        "image_error",
        "model_error",
        "aborted_streaming",
        "prompt_too_long",
        "completed",
        "stop_hook_prevented",
        "aborted_tools",
        "hook_stopped",
        "max_turns",
        "max_cost",
        "tool_failure_loop",
        "empty_response",
    }

    assert set(get_args(terminal.TerminalReason)) == expected
    assert transitions.Terminal is terminal.Terminal
    assert transitions.TerminalHolder is terminal.TerminalHolder
    assert transitions.EARLY_STOP_SUBTYPES is terminal.EARLY_STOP_SUBTYPES


def test_error_stop_reasons_have_entrypoint_subtypes() -> None:
    expected_error_stops = {
        "tool_failure_loop",
        "empty_response",
        "blocking_limit",
        "prompt_too_long",
        "image_error",
        "max_turns",
        "max_cost",
    }

    assert set(terminal.EARLY_STOP_SUBTYPES) == expected_error_stops
    assert terminal.EARLY_STOP_SUBTYPES["max_turns"] == "error_max_turns"


def test_retry_continue_reasons_are_explicit() -> None:
    expected = {
        "next_turn",
        "max_output_tokens_recovery",
        "max_output_tokens_escalate",
        "reactive_compact_retry",
        "collapse_drain_retry",
        "stop_hook_blocking",
        "token_budget_continuation",
        "continuation_nudge",
    }

    assert set(get_args(transitions.ContinueReason)) == expected
    assert MAX_529_RETRIES == 3
    assert DEFAULT_MAX_RETRIES == 10


def test_budget_guard_is_deterministic_across_all_dimensions() -> None:
    now = 100.0
    guard = BudgetGuard(
        max_turns=2,
        max_cost_usd=1.5,
        max_input_tokens=100,
        max_output_tokens=200,
        deadline=now + 10.0,
        clock=lambda: now + 11.0,
    )

    assert guard.check(turn_count=3).reason == "max_turns"
    assert guard.check(cost_usd=1.5).reason == "max_cost"
    assert guard.check(input_tokens=100).reason == "max_input_tokens"
    assert guard.check(output_tokens=200).reason == "max_output_tokens"
    assert guard.check().reason == "deadline"

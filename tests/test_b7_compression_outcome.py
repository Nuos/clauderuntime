"""B7 W5 — compression outcome contract tests.

Context Law (Behavior Bible §H): compression must leave outcome/evidence, not
a bare bool. These tests pin the shared ``CompressionOutcome`` contract used
by both the automatic five-stage pipeline and the manual compact path:

- a no-op pass reports ``changed=False`` with a ``None`` stage;
- an active pass reports ``changed=True``, the last applied stage, and the
  token delta;
- the hard-window (autocompact) pass sets ``hard_limit_reached``;
- layer failures surface as warnings instead of being swallowed silently;
- the outcome is frozen and serializable.
"""

from __future__ import annotations

import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.services.compact.compression_outcome import (
    CompressionOutcome,
    build_outcome,
    outcome_from_layers,
)
from src.services.compact.pipeline import CompressionPipeline, PipelineConfig
from src.types.content_blocks import ToolResultBlock, ToolUseBlock
from src.types.messages import AssistantMessage, UserMessage


def _assistant(tool_id: str) -> AssistantMessage:
    return AssistantMessage(
        role="assistant",
        content=[ToolUseBlock(id=tool_id, name="Read", input={})],
    )


def _user_result(tool_id: str, content: str) -> UserMessage:
    return UserMessage(
        role="user",
        content=[ToolResultBlock(tool_use_id=tool_id, content=content)],
    )


def _conversation(count: int = 6) -> list:
    messages = []
    for i in range(count):
        messages.append(_assistant(f"t{i}"))
        messages.append(_user_result(f"t{i}", f"Result {i} " * 80))
    return messages


class TestOutcomeBuilder(unittest.TestCase):
    def test_noop_outcome(self) -> None:
        outcome = outcome_from_layers(
            layers_applied=[], warnings=[], hard_limit_reached=False,
            tokens_before=1000, tokens_saved=0,
        )
        self.assertFalse(outcome.changed)
        self.assertIsNone(outcome.stage)
        self.assertEqual(outcome.tokens_before, 1000)
        self.assertEqual(outcome.tokens_after, 1000)

    def test_active_outcome_reports_last_stage_and_delta(self) -> None:
        outcome = outcome_from_layers(
            layers_applied=["tool_result_budget", "snip_compact"],
            warnings=[], hard_limit_reached=False,
            tokens_before=1000, tokens_saved=300,
        )
        self.assertTrue(outcome.changed)
        self.assertEqual(outcome.stage, "snip_compact")
        self.assertEqual(outcome.tokens_after, 700)

    def test_hard_limit_flag(self) -> None:
        outcome = outcome_from_layers(
            layers_applied=["autocompact"], warnings=[], hard_limit_reached=True,
            tokens_before=200_000, tokens_saved=50_000,
        )
        self.assertTrue(outcome.hard_limit_reached)

    def test_warnings_carried(self) -> None:
        outcome = build_outcome(
            changed=False, warnings=("layer-1: boom",), tokens_before=10,
        )
        self.assertEqual(outcome.warnings, ("layer-1: boom",))

    def test_outcome_is_frozen(self) -> None:
        outcome = CompressionOutcome(changed=False)
        with self.assertRaises(Exception):
            outcome.changed = True  # type: ignore[misc]


class TestPipelineOutcome(unittest.TestCase):
    def test_noop_pipeline_reports_unchanged(self) -> None:
        messages = [UserMessage(content="Hello")]
        result = asyncio.run(CompressionPipeline().run(messages, input_token_count=50))
        self.assertFalse(result.outcome.changed)
        self.assertIsNone(result.outcome.stage)
        self.assertEqual(result.layers_applied, [])

    def test_active_pipeline_reports_changed_and_stage(self) -> None:
        messages = _conversation(6)
        # snip_compact trims OLD Read tool results beyond keep_recent (default 10);
        # with 6 rounds nothing is old enough → force with keep_recent=0.
        config = PipelineConfig(snip_keep_recent=0, mc_enabled=False)
        result = asyncio.run(CompressionPipeline(config).run(messages, input_token_count=5000))
        self.assertTrue(result.outcome.changed)
        self.assertIsNotNone(result.outcome.stage)
        self.assertGreater(result.tokens_saved, 0)
        self.assertIsNotNone(result.outcome.tokens_before)
        self.assertIsNotNone(result.outcome.tokens_after)
        self.assertLessEqual(result.outcome.tokens_after, result.outcome.tokens_before)

    def test_autocompact_sets_hard_limit_flag(self) -> None:
        messages = _conversation(2)
        fake_result = SimpleNamespace(
            tokens_saved=1000,
            summary_messages=[UserMessage(content="summary")],
            messages_to_keep=[UserMessage(content="keep")],
            attachments=[],
        )
        provider = SimpleNamespace(model="test-model")
        config = PipelineConfig(provider=provider, model="test-model")
        with patch(
            "src.services.compact.pipeline.auto_compact_if_needed",
            return_value=fake_result,
        ):
            result = asyncio.run(CompressionPipeline(config).run(messages, input_token_count=200_000))
        self.assertIn("autocompact", result.layers_applied)
        self.assertTrue(result.outcome.hard_limit_reached)
        self.assertEqual(result.outcome.stage, "autocompact")

    def test_layer_failure_becomes_warning(self) -> None:
        messages = _conversation(2)
        with patch(
            "src.services.compact.pipeline.snip_compact",
            side_effect=RuntimeError("snip exploded"),
        ):
            result = asyncio.run(CompressionPipeline().run(messages, input_token_count=100))
        self.assertTrue(any("snip_compact" in w for w in result.outcome.warnings))
        self.assertIn("snip_compact", result.outcome.warnings[0])


if __name__ == "__main__":
    unittest.main()

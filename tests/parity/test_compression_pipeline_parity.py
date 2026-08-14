"""WS-10: Structural parity — compression pipeline layers match TS.

Verifies:
- 5 layers execute in correct order (cheap → expensive)
- Source-Aligned mode does not skip later shaping layers
- Microcompact is called every turn and owns its no-op decision
- Pipeline continues on individual layer failure
"""
from __future__ import annotations

import asyncio
import json
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.services.compact.pipeline import (
    CompressionPipeline,
    CompressionResult,
    PipelineConfig,
    run_compression_pipeline,
)
from src.types.messages import UserMessage, AssistantMessage

REF_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "reference_data"


def _load_json(name: str) -> dict:
    return json.loads((REF_DIR / name).read_text())


def _make_messages(n: int = 5) -> list:
    msgs = []
    for i in range(n):
        if i % 2 == 0:
            msgs.append(UserMessage(content=f"User message {i}"))
        else:
            msgs.append(AssistantMessage(content=f"Assistant message {i}"))
    return msgs


class TestCompressionLayerOrderParity(unittest.TestCase):
    """Pipeline layers execute in the correct order matching TS."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.snapshot = _load_json("ts_compression_layers.json")

    def test_layer_count_is_five(self) -> None:
        layers = self.snapshot["layers_in_order"]
        self.assertEqual(len(layers), 5)

    def test_layer_names_match(self) -> None:
        expected = [layer["name"] for layer in self.snapshot["layers_in_order"]]
        self.assertEqual(expected, [
            "tool_result_budget",
            "snip_compact",
            "microcompact",
            "context_collapse",
            "autocompact",
        ])

    def test_layer_indices_sequential(self) -> None:
        for i, layer in enumerate(self.snapshot["layers_in_order"]):
            self.assertEqual(layer["index"], i + 1)

    def test_pipeline_execution_order(self) -> None:
        """Run the pipeline and verify layers are applied in order."""
        execution_log: list[str] = []

        def mock_tool_result_budget(msgs, **kwargs):
            execution_log.append("tool_result_budget")
            return msgs, 0

        def mock_snip_compact(msgs, **kwargs):
            execution_log.append("snip_compact")
            return msgs, 0

        def mock_microcompact(msgs, **kwargs):
            execution_log.append("microcompact")
            return msgs, 0

        messages = _make_messages()
        config = PipelineConfig(collapse_store=None, provider=None, mc_enabled=True)

        with patch("src.services.compact.pipeline.apply_tool_result_budget", mock_tool_result_budget), \
             patch("src.services.compact.pipeline.snip_compact", mock_snip_compact), \
             patch("src.services.compact.pipeline.microcompact_typed_messages", mock_microcompact):
            result = asyncio.run(run_compression_pipeline(messages, config=config))

        self.assertEqual(execution_log, [
            "tool_result_budget",
            "snip_compact",
            "microcompact",
        ])


class TestCompressionPipelineBehavior(unittest.TestCase):
    """验证连续 shaping、内部 feature gate 和失败隔离。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.snapshot = _load_json("ts_compression_layers.json")

    def test_execution_order_is_cheap_to_expensive(self) -> None:
        self.assertEqual(
            self.snapshot["pipeline_behavior"]["execution_order"],
            "cheap_to_expensive",
        )

    def test_failure_handling_continue(self) -> None:
        self.assertEqual(
            self.snapshot["pipeline_behavior"]["failure_handling"],
            "continue_on_failure",
        )

    def test_pipeline_config_has_early_exit_tokens(self) -> None:
        config = PipelineConfig()
        self.assertIsInstance(config.early_exit_tokens, int)
        self.assertGreater(config.early_exit_tokens, 0)

    def test_source_aligned_mode_keeps_running_after_large_savings(self) -> None:
        """早层节省大量 token 后，生产模式仍执行后续 shaping 层。"""
        layer2_called = False

        def mock_tool_result_budget(msgs, **kwargs):
            return msgs, 999_999  # Free massive tokens

        def mock_snip_compact(msgs, **kwargs):
            nonlocal layer2_called
            layer2_called = True
            return msgs, 0

        messages = _make_messages()
        config = PipelineConfig(
            early_exit_tokens=100,
            collapse_store=None,
            provider=None,
        )

        with patch("src.services.compact.pipeline.apply_tool_result_budget", mock_tool_result_budget), \
             patch("src.services.compact.pipeline.snip_compact", mock_snip_compact):
            result = asyncio.run(run_compression_pipeline(messages, config=config))

        self.assertTrue(layer2_called)
        self.assertGreater(result.tokens_saved, 0)

    def test_product_extension_can_retain_legacy_early_exit(self) -> None:
        """显式选择产品扩展时可以保留旧优化，但该路径不计入 parity。"""
        called = False

        def mock_tool_result_budget(msgs, **kwargs):
            return msgs, 999_999

        def mock_snip_compact(msgs, **kwargs):
            nonlocal called
            called = True
            return msgs, 0

        config = PipelineConfig(source_aligned=False, early_exit_tokens=100)
        with patch("src.services.compact.pipeline.apply_tool_result_budget", mock_tool_result_budget), \
             patch("src.services.compact.pipeline.snip_compact", mock_snip_compact):
            asyncio.run(run_compression_pipeline(_make_messages(), config=config))

        self.assertFalse(called)

    def test_pipeline_continues_on_layer_failure(self) -> None:
        """If one layer fails, pipeline should continue with remaining layers."""
        def mock_tool_result_budget_fail(msgs, **kwargs):
            raise RuntimeError("Layer 1 failure")

        def mock_snip_compact(msgs, **kwargs):
            return msgs, 100

        def mock_microcompact(msgs, **kwargs):
            return msgs, 0

        messages = _make_messages()
        config = PipelineConfig(collapse_store=None, provider=None)

        with patch("src.services.compact.pipeline.apply_tool_result_budget", mock_tool_result_budget_fail), \
             patch("src.services.compact.pipeline.snip_compact", mock_snip_compact), \
             patch("src.services.compact.pipeline.microcompact_typed_messages", mock_microcompact):
            result = asyncio.run(run_compression_pipeline(messages, config=config))

        self.assertIn("snip_compact", result.layers_applied)

    def test_microcompact_default_gate_is_an_internal_noop(self) -> None:
        """默认每轮进入 Microcompact，再由内部关闭的 feature gate 返回空操作。"""
        called = False

        def mock_microcompact(msgs, **kwargs):
            nonlocal called
            called = True
            self.assertFalse(kwargs["force"])
            self.assertFalse(kwargs["time_config"].enabled)
            return msgs, 0

        with patch("src.services.compact.pipeline.microcompact_typed_messages", mock_microcompact):
            result = asyncio.run(run_compression_pipeline(
                _make_messages(), config=PipelineConfig(provider=None),
            ))

        self.assertTrue(called)
        self.assertNotIn("microcompact", result.layers_applied)

    def test_autocompact_receives_tokens_after_cheap_layer_savings(self) -> None:
        """C3 accounting: layer 5 sees the remaining, not original, budget."""
        observed_input_tokens: list[int] = []

        async def mock_autocompact(messages, input_tokens, *args, **kwargs):
            observed_input_tokens.append(input_tokens)
            return None

        config = PipelineConfig(
            provider=MagicMock(), model="test-model", early_exit_tokens=999_999,
        )
        with patch(
            "src.services.compact.pipeline.apply_tool_result_budget",
            lambda msgs, **kwargs: (msgs, 23),
        ), patch(
            "src.services.compact.pipeline.auto_compact_if_needed", mock_autocompact,
        ):
            asyncio.run(run_compression_pipeline(
                _make_messages(), input_token_count=100, config=config,
            ))

        self.assertEqual(observed_input_tokens, [77])


class TestCompressionResultStructure(unittest.TestCase):
    """CompressionResult has expected fields."""

    def test_result_has_messages(self) -> None:
        r = CompressionResult(messages=[])
        self.assertIsInstance(r.messages, list)

    def test_result_has_tokens_saved(self) -> None:
        r = CompressionResult(messages=[])
        self.assertEqual(r.tokens_saved, 0)

    def test_result_has_layers_applied(self) -> None:
        r = CompressionResult(messages=[])
        self.assertIsInstance(r.layers_applied, list)


if __name__ == "__main__":
    unittest.main()

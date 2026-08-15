"""B7 W2 — canonical turn preparation contract tests.

W2 exit condition: production prompt/context owner = 1. These tests prove:

- ``TurnPreparationService.assemble_system_prompt_blocks`` is byte-equivalent
  to the legacy ``agent_loop_compat.build_effective_system_prompt`` for
  identical inputs (the cutover no-drift proof);
- ``build_effective_system_prompt`` is now a THIN adapter that delegates to
  the service and carries no assembly logic of its own;
- ``TurnPreparationService.prepare`` returns a fully-populated
  ``PreparedTurn`` (system prompt blocks, messages, visible tools, output
  style, model capability snapshot, compaction config, prompt-cache scope,
  canonical query params) without mutating the session.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from src.query.agent_loop_compat import build_effective_system_prompt
from src.runtime.turn_preparation import PreparedTurn, TurnPreparationService
from src.tool_system.context import ToolContext
from src.tool_system.defaults import build_default_registry


def _make_session(tmp: str) -> ToolContext:
    registry = build_default_registry()
    ctx = ToolContext(workspace_root=Path(tmp))
    ctx.visible_tools = [t.name for t in registry.list_tools()]  # type: ignore[attr-defined]
    ctx.messages = []  # type: ignore[attr-defined]
    return ctx


class TestServiceEquivalenceWithLegacyBuilder(unittest.TestCase):
    def test_blocks_byte_identical_to_legacy_builder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ctx = _make_session(tmp)
            provider = SimpleNamespace(model="test-model")
            kwargs = dict(
                style_prompt="Be concise.",
                tool_context=ctx,
                provider=provider,
                mcp_servers=None,
                query_source="main",
            )
            legacy = build_effective_system_prompt(**kwargs)
            service = TurnPreparationService.assemble_system_prompt_blocks(
                cwd=str(ctx.cwd or ctx.workspace_root), **kwargs
            )
            self.assertEqual(legacy, service)
            self.assertTrue(legacy, "system prompt must not be empty")

    def test_wrapper_delegates_to_service(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ctx = _make_session(tmp)
            with patch.object(
                TurnPreparationService, "assemble_system_prompt_blocks", return_value=[]
            ) as mocked:
                result = build_effective_system_prompt(
                    "style", ctx, provider=None, mcp_servers=None, query_source="main"
                )
                self.assertEqual(result, [])
                mocked.assert_called_once()
                call_kwargs = mocked.call_args.kwargs
                self.assertEqual(call_kwargs["style_prompt"], "style")
                self.assertIs(call_kwargs["tool_context"], ctx)

    def test_wrapper_has_no_assembly_imports(self) -> None:
        # The wrapper must not drag in the block assembler: delegation only.
        import inspect

        import src.query.agent_loop_compat as compat

        source = inspect.getsource(compat.build_effective_system_prompt)
        self.assertNotIn("build_full_system_prompt_blocks", source)
        self.assertNotIn("build_context_prompt_parts", source)
        self.assertIn("TurnPreparationService.assemble_system_prompt_blocks", source)


class TestPreparedTurn(unittest.TestCase):
    def test_prepare_returns_fully_populated_turn(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            session = _make_session(tmp)
            request = SimpleNamespace(
                style_prompt="Be concise.",
                provider=SimpleNamespace(model="test-model"),
                mcp_servers=None,
                query_source="main",
                model_capabilities=SimpleNamespace(adaptive_thinking=True),
                compact_config=SimpleNamespace(enabled=True),
                prompt_cache_scope="session",
                query_params=SimpleNamespace(max_turns=5),
            )
            turn = TurnPreparationService.prepare(request, session)

            self.assertIsInstance(turn, PreparedTurn)
            self.assertTrue(turn.system_prompt_blocks)
            self.assertIsInstance(turn.system_prompt_blocks, tuple)
            self.assertEqual(turn.messages, ())
            self.assertEqual(turn.visible_tools, tuple(session.visible_tools))  # type: ignore[attr-defined]
            self.assertTrue(turn.visible_tools)
            self.assertIsNotNone(turn.model_capabilities)
            self.assertIsNotNone(turn.compact_config)
            self.assertEqual(turn.prompt_cache_scope, "session")
            self.assertIsNotNone(turn.query_params)
            self.assertEqual(turn.provenance["owner"], "TurnPreparationService")

    def test_prepare_system_prompt_matches_legacy_builder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            session = _make_session(tmp)
            request = SimpleNamespace(
                style_prompt="Be concise.",
                provider=SimpleNamespace(model="test-model"),
                mcp_servers=None,
                query_source="main",
            )
            turn = TurnPreparationService.prepare(request, session)
            legacy = build_effective_system_prompt(
                "Be concise.",
                session,
                provider=request.provider,
                mcp_servers=None,
                query_source="main",
            )
            self.assertEqual(list(turn.system_prompt_blocks), legacy)

    def test_prepare_does_not_mutate_session(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            session = _make_session(tmp)
            before_messages = list(session.messages)  # type: ignore[attr-defined]
            before_tools = list(session.visible_tools)  # type: ignore[attr-defined]
            request = SimpleNamespace(style_prompt="s", query_source="main")
            TurnPreparationService.prepare(request, session)
            self.assertEqual(list(session.messages), before_messages)  # type: ignore[attr-defined]
            self.assertEqual(list(session.visible_tools), before_tools)  # type: ignore[attr-defined]

    def test_prepared_turn_is_frozen(self) -> None:
        turn = PreparedTurn(system_prompt_blocks=())
        with self.assertRaises(Exception):
            turn.system_prompt_blocks = ()  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()

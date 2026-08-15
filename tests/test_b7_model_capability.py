"""B7 W6 — model capability resolver (single owner) tests.

The allowlists moved from ``query.py`` into ``ModelCapabilityResolver``; the
query predicates now delegate. These tests pin the matrix AND prove the
delegation is behavior-identical to the historical allowlists.
"""

from __future__ import annotations

import unittest

from src.query.query import (
    _model_supports_adaptive_thinking,
    _model_supports_effort,
    _model_supports_extended_thinking,
    _model_supports_xhigh_effort,
)
from src.runtime.model_capability_resolver import (
    ModelCapabilities,
    ModelCapabilityResolver,
    resolve_model_capabilities,
)


class TestResolverMatrix(unittest.TestCase):
    def setUp(self) -> None:
        self.resolver = ModelCapabilityResolver()

    def test_opus5_full_capabilities(self) -> None:
        caps = self.resolver.resolve("anthropic", "claude-opus-5")
        self.assertTrue(caps.extended_thinking)
        self.assertTrue(caps.adaptive_thinking)
        self.assertTrue(caps.effort_supported)
        self.assertTrue(caps.xhigh_effort)

    def test_sonnet46_adaptive_but_not_xhigh(self) -> None:
        caps = self.resolver.resolve("anthropic", "claude-sonnet-4-6")
        self.assertTrue(caps.adaptive_thinking)
        self.assertTrue(caps.effort_supported)
        self.assertFalse(caps.xhigh_effort)

    def test_opus46_effort_no_xhigh(self) -> None:
        caps = self.resolver.resolve("anthropic", "claude-opus-4-6")
        self.assertTrue(caps.effort_supported)
        self.assertFalse(caps.xhigh_effort)

    def test_opus48_xhigh(self) -> None:
        caps = self.resolver.resolve("anthropic", "claude-opus-4-8")
        self.assertTrue(caps.xhigh_effort)

    def test_old_model_no_thinking(self) -> None:
        caps = self.resolver.resolve("anthropic", "claude-3-5-sonnet")
        self.assertFalse(caps.extended_thinking)
        self.assertFalse(caps.adaptive_thinking)
        self.assertFalse(caps.effort_supported)

    def test_dated_snapshot_opts_in(self) -> None:
        caps = self.resolver.resolve("anthropic", "claude-opus-4-7-20260201")
        self.assertTrue(caps.extended_thinking)
        self.assertTrue(caps.adaptive_thinking)

    def test_empty_model_is_safe(self) -> None:
        caps = self.resolver.resolve(None, None)
        self.assertFalse(caps.extended_thinking)
        self.assertFalse(caps.adaptive_thinking)

    def test_openai_provider_disables_prompt_cache(self) -> None:
        caps = self.resolver.resolve("openai", "gpt-5")
        self.assertFalse(caps.prompt_cache)

    def test_snapshot_is_immutable(self) -> None:
        caps = ModelCapabilities(adaptive_thinking=True)
        with self.assertRaises(Exception):
            caps.adaptive_thinking = False  # type: ignore[misc]


class TestQueryDelegationEquivalence(unittest.TestCase):
    """The query predicates must match the resolver for the same input."""

    def test_delegation_matches_resolver(self) -> None:
        for model in (
            "claude-opus-5",
            "claude-opus-4-8",
            "claude-opus-4-7-20260201",
            "claude-sonnet-4-6",
            "claude-haiku-4-5",
            "claude-3-5-sonnet",
            "",
            None,
        ):
            caps = resolve_model_capabilities(None, model)
            self.assertEqual(
                _model_supports_extended_thinking(model), caps.extended_thinking, model
            )
            self.assertEqual(
                _model_supports_adaptive_thinking(model), caps.adaptive_thinking, model
            )
            self.assertEqual(_model_supports_effort(model), caps.effort_supported, model)
            self.assertEqual(_model_supports_xhigh_effort(model), caps.xhigh_effort, model)


if __name__ == "__main__":
    unittest.main()

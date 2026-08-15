"""B7 W6 — model capability resolver (single owner).

The diagnostic flagged that model/provider capability decisions
(adaptive thinking, effort levels, prompt-cache scope, …) were allowlisted in
more than one place. This module is the SINGLE owner for that judgment: the
allowlists moved here from ``src/query/query.py``, and every caller reads an
immutable :class:`ModelCapabilities` snapshot instead of maintaining its own
pattern list.

No model call happens here; the resolver is pure name/provider classification.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ModelCapabilities:
    """Immutable capability snapshot for one (provider, model) pair."""

    adaptive_thinking: bool = False
    extended_thinking: bool = False
    effort_supported: bool = False
    xhigh_effort: bool = False
    prompt_cache: bool = True
    images: bool = False
    max_context_tokens: int | None = None


#: Claude 4+ models accept a ``thinking`` param (first-party endpoint).
#: Detection is by name pattern so unreleased dated snapshots opt in.
#: Pattern moved VERBATIM from ``query.py`` so behavior is byte-identical.
_THINKING_ELIGIBLE_MODEL_PATTERN = re.compile(
    r"claude-(?:sonnet|opus|haiku|fable)-(?:4-\d+|[5-9]\b|\d{2,})",
    re.IGNORECASE,
)


def _matches_any(model: str | None, *needles: str) -> bool:
    if not model:
        return False
    m = model.lower()
    return any(needle in m for needle in needles)


class ModelCapabilityResolver:
    """Resolve :class:`ModelCapabilities` for a (provider_id, model_id) pair.

    Allowlists were moved here verbatim from ``query.py``
    (``_model_supports_extended_thinking`` / ``_adaptive_thinking`` /
    ``_effort`` / ``_xhigh_effort``); the query layer now delegates here so
    there is exactly one place a new model has to be added.
    """

    def resolve(self, provider_id: str | None, model_id: str | None) -> ModelCapabilities:
        model = model_id or ""
        extended = bool(_THINKING_ELIGIBLE_MODEL_PATTERN.search(model))
        adaptive = _matches_any(
            model, "fable-5", "opus-5", "opus-4-8", "opus-4-7", "opus-4-6", "sonnet-4-6"
        )
        effort = _matches_any(
            model, "fable-5", "opus-5", "opus-4-8", "opus-4-6", "sonnet-4-6"
        )
        xhigh = _matches_any(model, "opus-5", "opus-4-8", "fable-5")

        # Prompt-cache capability: first-party Anthropic family and
        # DeepSeek-derived models cache; anything unknown defaults to True so
        # the cache-scope gate stays permissive (the cache layer re-checks
        # per request).
        provider = (provider_id or "").lower()
        prompt_cache = not any(
            marker in provider for marker in ("openai", "azure", "google", "vertex")
        )

        return ModelCapabilities(
            adaptive_thinking=adaptive,
            extended_thinking=extended,
            effort_supported=effort,
            xhigh_effort=xhigh,
            prompt_cache=prompt_cache,
            images=_matches_any(model, "vision", "opus-4-6", "sonnet-4-6"),
        )


#: Module-level convenience resolver; long-lived sessions may keep their own
#: instance (it is stateless).
_default_resolver = ModelCapabilityResolver()


def resolve_model_capabilities(
    provider: Any | None = None, model: str | None = None
) -> ModelCapabilities:
    """Convenience wrapper used by the query layer.

    ``provider`` may carry ``provider_id``/``name``/``base_url`` attributes;
    the resolver only needs a stable provider family string.
    """
    provider_id = None
    if provider is not None:
        provider_id = (
            getattr(provider, "provider_id", None)
            or getattr(provider, "name", None)
            or getattr(provider, "base_url", None)
        )
    return _default_resolver.resolve(provider_id, model)

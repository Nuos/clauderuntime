"""B7 W5 — structured compression outcome.

Context Law (Behavior Bible §H): compression must not return only a ``bool``;
it must leave outcome/evidence. Both the automatic five-stage pipeline and the
manual ``/compact`` path share this contract (without conflating their product
semantics — ``trigger`` distinguishes them).

:class:`CompressionOutcome` is the frozen, serializable evidence record every
compression entry point returns.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CompressionOutcome:
    """Evidence of one compression pass.

    Mirrors ``blueprints/compression_outcome.py``:

    - ``changed`` — any layer modified the conversation;
    - ``stage`` — the LAST layer that applied (``None`` when nothing changed);
    - ``warnings`` — non-fatal layer failures observed during the pass;
    - ``hard_limit_reached`` — the pass was forced by the hard context window
      (autocompact fired) rather than a routine budget trim;
    - ``artifacts`` — paths of artifacts produced/persisted by the pass;
    - ``tokens_before`` / ``tokens_after`` — estimated input tokens before and
      after the pass (``None`` when unknown).
    """

    changed: bool
    stage: str | None = None
    warnings: tuple[str, ...] = ()
    hard_limit_reached: bool = False
    artifacts: tuple[str, ...] = ()
    tokens_before: int | None = None
    tokens_after: int | None = None


def build_outcome(
    *,
    changed: bool,
    stage: str | None = None,
    warnings: tuple[str, ...] = (),
    hard_limit_reached: bool = False,
    artifacts: tuple[str, ...] = (),
    tokens_before: int | None = None,
    tokens_after: int | None = None,
) -> CompressionOutcome:
    """Pure builder used by every compression entry point (pipeline + manual).

    ``tokens_after`` defaults to ``tokens_before`` when only ``tokens_before``
    is known and nothing changed; callers that know a saved-token delta pass
    the exact after-count.
    """
    return CompressionOutcome(
        changed=changed,
        stage=stage,
        warnings=tuple(warnings),
        hard_limit_reached=hard_limit_reached,
        artifacts=tuple(artifacts),
        tokens_before=tokens_before,
        tokens_after=tokens_after,
    )


def outcome_from_layers(
    *,
    layers_applied: list[str],
    warnings: list[str],
    hard_limit_reached: bool,
    tokens_before: int | None,
    tokens_saved: int,
) -> CompressionOutcome:
    """Derive the outcome from pipeline bookkeeping (shared logic)."""
    changed = bool(layers_applied)
    return build_outcome(
        changed=changed,
        stage=layers_applied[-1] if layers_applied else None,
        warnings=tuple(warnings),
        hard_limit_reached=hard_limit_reached,
        tokens_before=tokens_before,
        tokens_after=(
            max(0, tokens_before - tokens_saved)
            if tokens_before is not None
            else None
        ),
    )

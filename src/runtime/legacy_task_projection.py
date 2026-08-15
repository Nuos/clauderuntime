"""B7 W4 — read-only legacy task projection.

Task Law (Behavior Bible §J): one runtime task may only have ONE writable
state owner — :class:`RuntimeTaskRegistry`. Legacy dict-of-dicts views (the
historical ``ToolContext.background_bash_tasks``) may exist only as
projections/adapters; they must never be written directly and must never
shadow the registry.

This module provides :class:`LegacyTaskProjection`, the read-only
dict-like view that replaces the legacy mutable dict. Writes raise
:class:`RuntimeError`; every read is derived live from the registry.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import Any, TypeVar

from src.task_registry import RuntimeTaskRegistry

_T = TypeVar("_T")


class LegacyTaskProjection(Mapping[str, dict[str, Any]]):
    """Read-only dict-like view over a :class:`RuntimeTaskRegistry`.

    Keeps the historical ``background_bash_tasks`` API shape (``get`` /
    ``[id]`` / ``values`` / ``items``) working for unmigrated readers while
    guaranteeing single-writer semantics: any attempt to mutate the view
    raises, and all values are projected on demand from the registry via
    ``TaskStateBase.to_legacy_dict``.
    """

    def __init__(self, registry: RuntimeTaskRegistry) -> None:
        self._registry = registry

    # -- reads -----------------------------------------------------------

    def get(self, task_id: str, default: _T | None = None) -> dict[str, Any] | _T | None:
        state = self._registry.get(task_id)
        if state is None:
            return default
        return state.to_legacy_dict()

    def __getitem__(self, task_id: str) -> dict[str, Any]:
        state = self._registry.get(task_id)
        if state is None:
            raise KeyError(task_id)
        return state.to_legacy_dict()

    def __iter__(self) -> Iterator[str]:
        return (state.id for state in self._registry.all())

    def __len__(self) -> int:
        return len(self._registry)

    def __contains__(self, task_id: object) -> bool:
        return task_id in self._registry

    def keys(self):
        return [state.id for state in self._registry.all()]

    def values(self):
        return [state.to_legacy_dict() for state in self._registry.all()]

    def items(self):
        return [(state.id, state.to_legacy_dict()) for state in self._registry.all()]

    def list(self) -> list[dict[str, Any]]:
        """Blueprint-compatible alias of ``values``."""
        return self.values()

    # -- writes: forbidden ----------------------------------------------

    def __setitem__(self, key: str, value: Any) -> None:
        raise RuntimeError(
            "legacy task projection is read-only; mutate RuntimeTaskRegistry "
            "instead (B7 W4 single-writer contract)"
        )

    def __delitem__(self, key: str) -> None:
        raise RuntimeError(
            "legacy task projection is read-only; mutate RuntimeTaskRegistry "
            "instead (B7 W4 single-writer contract)"
        )

    def update(self, *args: Any, **kwargs: Any) -> None:
        raise RuntimeError(
            "legacy task projection is read-only; mutate RuntimeTaskRegistry "
            "instead (B7 W4 single-writer contract)"
        )

    def clear(self) -> None:
        raise RuntimeError(
            "legacy task projection is read-only; mutate RuntimeTaskRegistry "
            "instead (B7 W4 single-writer contract)"
        )

    def pop(self, *args: Any, **kwargs: Any) -> Any:
        raise RuntimeError(
            "legacy task projection is read-only; mutate RuntimeTaskRegistry "
            "instead (B7 W4 single-writer contract)"
        )

    def setdefault(self, *args: Any, **kwargs: Any) -> Any:
        raise RuntimeError(
            "legacy task projection is read-only; mutate RuntimeTaskRegistry "
            "instead (B7 W4 single-writer contract)"
        )

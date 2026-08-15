from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

@dataclass(frozen=True)
class PreparedTurn:
    system_prompt_blocks: tuple[Any, ...]
    messages: tuple[Any, ...]
    visible_tools: tuple[Any, ...]
    model_capabilities: Any
    compact_config: Any
    prompt_cache_scope: Any
    query_params: Any
    provenance: Mapping[str, Any] = field(default_factory=dict)

class TurnPreparationService:
    """Single owner for all pre-query runtime composition.

    No model call. No tool side effect. No permission bypass.
    """
    def prepare(self, request: Any, session: Any) -> PreparedTurn:
        raise NotImplementedError

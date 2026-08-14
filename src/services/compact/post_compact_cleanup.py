"""在会话压缩成功后清理下一轮必须重新构建的上下文状态。

清理范围包括系统提示缓存、文件读取状态、嵌套记忆路径和已注入路径规则登记。
失败的非关键缓存清理会被记录，但不会破坏已经生成的压缩摘要。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable

logger = logging.getLogger(__name__)


@dataclass
class PostCompactContext:
    """保存压缩成功后需要原位清空的会话状态容器。"""
    # Caches to clear (name → clear callable)
    caches: dict[str, Callable[[], None]] = field(default_factory=dict)
    # Read-file state tracking
    read_file_state: dict[str, Any] | None = None
    # Loaded nested memory paths
    loaded_nested_memory_paths: set[str] | None = None
    # 已注入的路径规则在摘要后必须允许重新加载。
    path_rule_claims: set[Any] | None = None


def run_post_compact_cleanup(
    context: PostCompactContext | None = None,
) -> list[str]:
    """
    Clear caches and tracking state after a successful compaction.

    Returns a list of cache names that were cleared.
    """
    cleared: list[str] = []

    # ch05 round-3 G3: every compaction restarts the cache epoch — reset
    # memoized prompt sections + beta-header latches (TS
    # clearSystemPromptSections, constants/systemPromptSections.ts:65-68).
    # Runs even with a None context (the reset is global state).
    try:
        from src.context_system.system_prompt_cache import (
            clear_system_prompt_sections,
        )

        clear_system_prompt_sections()
        cleared.append("system_prompt_sections")
    except Exception:
        pass

    if context is None:
        return cleared

    # Clear registered caches
    for name, clear_fn in context.caches.items():
        try:
            clear_fn()
            cleared.append(name)
        except Exception:
            logger.warning("Failed to clear cache %r during post-compact cleanup", name)

    # Clear read-file state
    if context.read_file_state is not None:
        context.read_file_state.clear()
        cleared.append("read_file_state")

    # Clear loaded nested memory paths
    if context.loaded_nested_memory_paths is not None:
        context.loaded_nested_memory_paths.clear()
        cleared.append("loaded_nested_memory_paths")

    if context.path_rule_claims is not None:
        context.path_rule_claims.clear()
        cleared.append("path_rule_claims")

    return cleared

"""按固定顺序执行五层生产会话压缩。

流水线从低成本工具结果预算开始，依次访问 Snip、Microcompact、上下文折叠和
自动摘要。Source-Aligned 模式始终进入每一层，由各层内部判断是否空操作；只有
显式产品扩展模式允许提前结束。自动摘要成功后还会清理路径规则的会话内登记，
保证被摘要移除的延迟规则能在后续 Read 时重新注入。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ...types.messages import Message
from ...providers.base import BaseProvider

from .compression_outcome import CompressionOutcome, outcome_from_layers
from .tool_result_budget import apply_tool_result_budget
from .snip_compact import snip_compact
from .context_collapse import ContextCollapseStore, get_context_collapse_state
from .autocompact import (
    AutoCompactTracking,
    auto_compact_if_needed,
    should_auto_compact,
)
from ...context_system.microcompact import (
    microcompact_typed_messages,
    TimeBasedMCConfig,
)

logger = logging.getLogger(__name__)


@dataclass
class CompressionResult:
    """Result of running the compression pipeline."""
    messages: list[Message]
    tokens_saved: int = 0
    layers_applied: list[str] = field(default_factory=list)
    autocompact_result: Any | None = None  # CompactionResult if layer 5 ran
    # B7 W5 — structured evidence of the pass (Context Law §H). Every
    # compression entry point returns one, so callers can record what
    # happened instead of a bare bool.
    outcome: CompressionOutcome = field(
        default_factory=lambda: CompressionOutcome(changed=False)
    )


@dataclass
class PipelineConfig:
    """Configuration for the compression pipeline."""
    # Layer 1: tool result budget
    budget_dir: Path | str | None = None
    max_result_tokens: int = 8_000

    # Layer 2: snip compact
    snip_keep_recent: int = 10

    # 第三层每轮都进入；开关关闭时由 Microcompact 内部返回空操作，保持 reference
    # 的调用形态，不能在 pipeline 外层把整个阶段删除。
    mc_enabled: bool = False
    mc_keep_recent: int = 5
    mc_time_config: TimeBasedMCConfig | None = None

    # Layer 4: context collapse
    collapse_store: ContextCollapseStore | None = None

    # Layer 5: autocompact
    context_window: int = 200_000
    max_output_tokens: int | None = None
    autocompact_threshold: float = 0.80
    autocompact_tracking: AutoCompactTracking | None = None

    # Layer 5: post-compact attachment context
    # Forwarded into auto_compact_if_needed → CompactContext so post-compact
    # file/plan restoration fires on auto-compact, not just /compact.
    read_file_state: dict[str, Any] | None = None
    plan_file_path: str | None = None
    memory_paths: set[str] | None = None
    path_rule_claims: set[Path] | None = None

    # Global
    provider: BaseProvider | None = None
    model: str = ""
    custom_instructions: str | None = None

    # Source-Aligned 是生产默认模式，禁止早层节省 token 后跳过后续 shaping 阶段。
    # early_exit_tokens 仅供明确选择 product extension 的调用方保留旧优化行为。
    source_aligned: bool = True
    early_exit_tokens: int = 20_000


def build_production_pipeline_config(
    provider: Any,
    tool_context: Any,
    autocompact_tracking: "AutoCompactTracking | None",
) -> PipelineConfig:
    """The minimal correct PipelineConfig for the live surfaces.

    ch05 round-4 GAP A — mirrors the test-only ``QueryEngine``'s
    construction (``query/engine.py:233-250``) exactly: provider + model +
    the read-file fingerprints (so post-compact file restoration fires) +
    the SESSION-scoped ``autocompact_tracking``. The tracking instance MUST
    outlive single turns — the 3-consecutive-failures circuit breaker
    counts across prompts; a per-turn instance would reset it every turn
    (the exact reason the engine holds one at ``engine.py:74-79``).
    """
    fingerprints = getattr(tool_context, "read_file_fingerprints", None) or {}
    read_file_state = {
        str(path): {"timestamp": fp[0]}
        for path, fp in fingerprints.items()
        if isinstance(fp, (tuple, list)) and fp
    }
    model = getattr(provider, "model", "") or ""
    context_window = 200_000
    max_output_tokens = None
    if model:
        try:
            from src.models.context import (
                get_context_window_for_model,
                get_model_max_output_tokens,
            )

            context_window = get_context_window_for_model(
                model, base_url=getattr(provider, "base_url", None)
            )
            max_output_tokens = get_model_max_output_tokens(
                model, base_url=getattr(provider, "base_url", None)
            )
        except Exception:
            logger.debug("model context-window resolution failed", exc_info=True)
    path_rule_claims = getattr(tool_context, "loaded_path_rule_files", None)
    if not isinstance(path_rule_claims, set):
        path_rule_claims = None
    return PipelineConfig(
        provider=provider,
        model=model,
        context_window=context_window,
        max_output_tokens=max_output_tokens,
        read_file_state=read_file_state or None,
        path_rule_claims=path_rule_claims,
        autocompact_tracking=autocompact_tracking,
    )


class CompressionPipeline:
    """
    Orchestrates the 5-layer compression pipeline.

    Usage::

        pipeline = CompressionPipeline(config)
        result = await pipeline.run(messages, input_token_count)
    """

    def __init__(self, config: PipelineConfig | None = None) -> None:
        self._config = config or PipelineConfig()

    async def run(
        self,
        messages: list[Message],
        input_token_count: int = 0,
    ) -> CompressionResult:
        """
        按固定顺序执行全部压缩层。生产默认的 Source-Aligned 模式不会因早层已节省
        较多 token 而提前返回；后续层仍必须自行执行 feature gate 或空操作判断。

        Args:
            messages: Current conversation messages.
            input_token_count: Estimated input token count (for autocompact decision).

        Returns:
            ``CompressionResult`` with the (potentially modified) messages,
            total tokens saved, and which layers were applied.
        """
        cfg = self._config
        total_saved = 0
        layers_applied: list[str] = []
        warnings: list[str] = []
        current_messages = messages
        autocompact_result = None

        def _result() -> CompressionResult:
            # B7 W5 — every return path carries structured outcome evidence.
            return CompressionResult(
                messages=current_messages,
                tokens_saved=total_saved,
                layers_applied=layers_applied,
                autocompact_result=autocompact_result,
                outcome=outcome_from_layers(
                    layers_applied=layers_applied,
                    warnings=warnings,
                    hard_limit_reached=autocompact_result is not None,
                    tokens_before=input_token_count,
                    tokens_saved=total_saved,
                ),
            )

        # --- Layer 1: Tool Result Budget ---
        try:
            current_messages, saved = apply_tool_result_budget(
                current_messages,
                budget_dir=cfg.budget_dir,
                max_result_tokens=cfg.max_result_tokens,
            )
            if saved > 0:
                total_saved += saved
                layers_applied.append("tool_result_budget")
                logger.debug("Layer 1 (tool_result_budget): saved %d tokens", saved)
                if not cfg.source_aligned and total_saved >= cfg.early_exit_tokens:
                    return _result()
        except Exception as e:
            warnings.append(f"tool_result_budget: {e}")
            logger.warning("Layer 1 (tool_result_budget) failed", exc_info=True)

        # --- Layer 2: Snip Compact ---
        try:
            current_messages, saved = snip_compact(
                current_messages,
                keep_recent=cfg.snip_keep_recent,
            )
            if saved > 0:
                total_saved += saved
                layers_applied.append("snip_compact")
                logger.debug("Layer 2 (snip_compact): saved %d tokens", saved)
                if not cfg.source_aligned and total_saved >= cfg.early_exit_tokens:
                    return _result()
        except Exception as e:
            warnings.append(f"snip_compact: {e}")
            logger.warning("Layer 2 (snip_compact) failed", exc_info=True)

        # --- Layer 3: Microcompact ---
        # 即使生产开关关闭也进入函数，由内部 gate 返回空操作。这保证后续新增的缓存编辑
        # 或时间策略有单一判定入口，同时避免默认情况下清除工具结果破坏文件未变判断。
        try:
            time_config = cfg.mc_time_config
            if not cfg.mc_enabled:
                time_config = TimeBasedMCConfig(enabled=False)
            current_messages, saved = microcompact_typed_messages(
                current_messages,
                keep_recent=cfg.mc_keep_recent,
                time_config=time_config,
                force=cfg.mc_enabled,
            )
            if saved > 0:
                total_saved += saved
                layers_applied.append("microcompact")
                logger.debug("Layer 3 (microcompact): saved %d tokens", saved)
                if not cfg.source_aligned and total_saved >= cfg.early_exit_tokens:
                    return _result()
        except Exception as e:
            warnings.append(f"microcompact: {e}")
            logger.warning("Layer 3 (microcompact) failed", exc_info=True)

        # --- Layer 4: Context Collapse ---
        try:
            store = cfg.collapse_store or get_context_collapse_state()
            if store is not None and store.enabled and store.commits:
                current_messages = store.project_view(current_messages)
                layers_applied.append("context_collapse")
                logger.debug("Layer 4 (context_collapse): projected %d commits", len(store.commits))
        except Exception as e:
            warnings.append(f"context_collapse: {e}")
            logger.warning("Layer 4 (context_collapse) failed", exc_info=True)

        # --- Layer 5: Autocompact ---
        if cfg.provider is not None and cfg.model:
            try:
                result = await auto_compact_if_needed(
                    current_messages,
                    input_token_count - total_saved,
                    cfg.context_window,
                    cfg.provider,
                    cfg.model,
                    max_output_tokens=cfg.max_output_tokens,
                    threshold_fraction=cfg.autocompact_threshold,
                    tracking=cfg.autocompact_tracking,
                    custom_instructions=cfg.custom_instructions,
                    read_file_state=cfg.read_file_state,
                    plan_file_path=cfg.plan_file_path,
                    memory_paths=cfg.memory_paths,
                    path_rule_claims=cfg.path_rule_claims,
                )
                if result is not None:
                    total_saved += result.tokens_saved
                    layers_applied.append("autocompact")
                    autocompact_result = result
                    # R6 — APPLY the compaction to the working messages. This
                    # was the bug: the pipeline computed the summary (an LLM
                    # call, cost incurred) but returned the UNCOMPACTED
                    # current_messages, so query() kept the full conversation
                    # and auto-compact re-fired every turn without ever
                    # shrinking the context — the exact opposite of what a
                    # long task needs. Assemble the compacted conversation the
                    # way the manual /compact path does (compact_service/
                    # service.py:101-104): the summary (a USER message — safe
                    # as the first message) + kept recent messages + the
                    # post-compact attachments (file-state a coding agent needs
                    # after compaction). The system boundary_marker is
                    # bookkeeping for the persisted conversation and is omitted
                    # from the working set (as the reactive path does), so the
                    # working messages stay API-clean.
                    n_before = len(current_messages)
                    current_messages = (
                        list(result.summary_messages)
                        + list(result.messages_to_keep)
                        + list(result.attachments)
                    )
                    logger.debug(
                        "Layer 5 (autocompact): saved %d tokens, %d -> %d msgs",
                        result.tokens_saved, n_before, len(current_messages),
                    )
            except Exception as e:
                warnings.append(f"autocompact: {e}")
                logger.warning("Layer 5 (autocompact) failed", exc_info=True)

        return _result()


async def run_compression_pipeline(
    messages: list[Message],
    input_token_count: int = 0,
    config: PipelineConfig | None = None,
) -> CompressionResult:
    """
    Convenience function: run the full compression pipeline.

    Args:
        messages: Current conversation messages.
        input_token_count: Estimated input token count.
        config: Pipeline configuration.

    Returns:
        ``CompressionResult``
    """
    pipeline = CompressionPipeline(config)
    return await pipeline.run(messages, input_token_count)

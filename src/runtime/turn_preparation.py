"""B7 W2 — canonical turn preparation owner.

Before the architecture closure there were two independent turn-preparation
owners producing the full system prompt / context:

* ``QueryEngine._build_system_prompt_parts()`` (``src/query/engine.py``)
* ``agent_loop_compat.build_effective_system_prompt()`` (``src/query/agent_loop_compat.py``)

This module introduces the single canonical owner:

    Surface → TurnPreparationService.prepare(request, session) → PreparedTurn

``PreparedTurn`` carries everything the canonical ``query()`` needs for one
turn: the full system prompt block list, conversation messages, visible
tools, output style, model capability snapshot, compaction config and the
canonical ``QueryParams`` inputs.

Migration contract (Behavior Bible §F, Turn Preparation Law):

* NO model call, NO tool side effect, NO permission bypass in this service.
* All surfaces (CLI / headless / server / TUI) obtain their pre-query
  composition through this service; the legacy builders are thin
  compatibility adapters that delegate here and carry no assembly logic of
  their own (see ``machine/deprecation-plan.yaml``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class PreparedTurn:
    """One fully-prepared turn for the canonical query loop.

    Fields mirror ``blueprints/runtime_turn_preparation.py``; every field is
    resolved by :class:`TurnPreparationService` so surfaces never assemble
    prompt/context/tools themselves.
    """

    system_prompt_blocks: tuple[dict[str, Any], ...]
    messages: tuple[Any, ...] = ()
    visible_tools: tuple[Any, ...] = ()
    model_capabilities: Any = None
    compact_config: Any = None
    prompt_cache_scope: Any = None
    query_params: Any = None
    provenance: Mapping[str, Any] = field(default_factory=dict)


class TurnPreparationService:
    """Single owner for all pre-query runtime composition.

    The service is deliberately stateless: ``prepare`` derives everything
    from the request + session inputs. The system-prompt assembly lives in
    :meth:`assemble_system_prompt_blocks` — the ONE implementation of the
    production cold-start block list — and the legacy
    ``build_effective_system_prompt`` wrapper delegates to it.
    """

    @staticmethod
    def assemble_system_prompt_blocks(
        *,
        cwd: str,
        style_prompt: str,
        tool_context: Any,
        provider: Any | None = None,
        mcp_servers: list[Any] | None = None,
        query_source: str = "main",
    ) -> list[dict[str, Any]]:
        """Canonical cold-start system prompt block list.

        Behavior is moved VERBATIM from the legacy
        ``agent_loop_compat.build_effective_system_prompt`` (which now
        delegates here) so the headless / TUI / server cutover path is
        byte-identical to the historical output — prompt construction can no
        longer drift between entry points.
        """
        # Local imports — context_system is a heavier dep; keep it off the
        # import time of the runtime spine.
        from ..context_system import build_context_prompt_parts
        from ..context_system.prompt_assembly import build_full_system_prompt_blocks
        from ..context_system.system_prompt_cache import CacheScope
        from ..coordinator.mode import is_coordinator_mode

        coordinator = is_coordinator_mode()
        if coordinator:
            # Coordinator mode: the orchestration prompt REPLACES the entire
            # base block set — no # Doing tasks, no tool guidance, no tone.
            # ``style_prompt`` is the append channel and survives; the
            # trailing workspace/git/CLAWCODEX.md context block is kept.
            from ..coordinator import get_coordinator_system_prompt
            from ..state.cache_state import should_1h_cache_ttl

            blocks: list[dict[str, Any]] = [{
                "type": "text",
                "text": get_coordinator_system_prompt(),
                "_cache_scope": CacheScope.SESSION.value,
            }]
            if style_prompt:
                blocks.append({
                    "type": "text",
                    "text": style_prompt,
                    "_cache_scope": CacheScope.SESSION.value,
                })
            blocks[-1]["cache_control"] = {
                "type": "ephemeral",
                "ttl": "1h" if should_1h_cache_ttl(query_source) else "5m",
            }
        else:
            # Skills listing (best-effort; mirrors engine.py:183).
            try:
                from ..command_system import get_skill_tool_commands
                skills = get_skill_tool_commands(cwd)
            except Exception:  # noqa: BLE001
                skills = None

            blocks = build_full_system_prompt_blocks(
                cwd=cwd,
                output_style="default",          # style is appended below
                append_system_prompt=style_prompt,
                query_source=query_source,
                provider=provider,
                mcp_servers=mcp_servers,
                skills=skills,
            )

        # Preserve the workspace + git + CLAWCODEX.md context (CLAWCODEX.md is
        # NOT in the base blocks above), as TWO trailing blocks split by
        # volatility: snapshot (REQUEST scope) first, instructions
        # (SESSION scope) second — the order build_context_prompt produced.
        try:
            context_snapshot, context_instructions = build_context_prompt_parts(
                tool_context.workspace_root,
                cwd=tool_context.cwd,
            )
        except Exception:  # noqa: BLE001
            context_snapshot, context_instructions = "", ""
        context_prompt = context_snapshot

        if coordinator:
            from ..coordinator.mode import get_coordinator_user_context

            try:
                from ..permissions.filesystem import get_scratchpad_dir
                scratchpad_dir: str | None = get_scratchpad_dir()
            except Exception:  # noqa: BLE001
                scratchpad_dir = None
            worker_ctx = get_coordinator_user_context(
                getattr(tool_context, "mcp_clients", None),
                scratchpad_dir=scratchpad_dir,
            ).get("workerToolsContext", "")
            if worker_ctx:
                entry = f"# workerToolsContext\n{worker_ctx}"
                context_instructions = (
                    f"{context_instructions}\n\n{entry}"
                    if context_instructions.strip()
                    else entry
                )

        if context_prompt.strip():
            blocks = blocks + [{
                "type": "text",
                "text": context_prompt,
                "_cache_scope": CacheScope.REQUEST.value,
            }]
        if context_instructions.strip():
            blocks = blocks + [{
                "type": "text",
                "text": context_instructions,
                "_cache_scope": CacheScope.SESSION.value,
            }]

        return blocks

    @classmethod
    def prepare(cls, request: Any, session: Any) -> PreparedTurn:
        """Compose a complete :class:`PreparedTurn` from a surface request.

        ``request`` carries per-call inputs (``query_source``, ``style``,
        provider, mcp servers, compaction config, prompt-cache scope);
        ``session`` carries the session-level context (a ``ToolContext`` with
        workspace/cwd/messages/visible tools). The service is the only place
        that resolves these into the canonical query inputs.
        """
        cwd = str(
            getattr(session, "cwd", None)
            or getattr(session, "workspace_root", None)
            or "."
        )
        style_prompt = getattr(request, "style_prompt", "") or ""
        provider = getattr(request, "provider", None)
        mcp_servers = getattr(request, "mcp_servers", None)
        query_source = getattr(request, "query_source", "main")

        system_prompt_blocks = cls.assemble_system_prompt_blocks(
            cwd=cwd,
            style_prompt=style_prompt,
            tool_context=session,
            provider=provider,
            mcp_servers=mcp_servers,
            query_source=query_source,
        )

        messages = tuple(getattr(session, "messages", ()) or ())
        visible_tools = tuple(getattr(session, "visible_tools", ()) or ())
        model_capabilities = getattr(request, "model_capabilities", None)
        compact_config = getattr(request, "compact_config", None)
        prompt_cache_scope = getattr(request, "prompt_cache_scope", None)
        query_params = getattr(request, "query_params", None)

        return PreparedTurn(
            system_prompt_blocks=tuple(system_prompt_blocks),
            messages=messages,
            visible_tools=visible_tools,
            model_capabilities=model_capabilities,
            compact_config=compact_config,
            prompt_cache_scope=prompt_cache_scope,
            query_params=query_params,
            provenance={
                "owner": "TurnPreparationService",
                "query_source": query_source,
                "coordinator": False,
            },
        )

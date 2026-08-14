"""Snip 压缩（压缩流水线第 2 层）— Python-native 保守实现。

Reference Mapping
-----------------
REF Source:
    query.ts::snipCompactIfNeeded（HISTORY_SNIP 开关下调用，消费 tokensFreed /
    boundaryMessage；参考函数体未完整恢复）
REF Behavior:
    按 HISTORY_SNIP 语义裁剪过旧的历史工具结果以释放上下文预算。
PY Owner:
    src/services/compact/snip_compact.py::snip_compact
PY Behavior:
    Python-native 保守 Snip：只裁剪“可重建”的旧工具结果 —— 只读工具
    （Read / Glob / Grep / ListDir / WebFetch / TaskOutput）的结果可以通过
    重新执行工具重建，裁剪无信息损失。以下内容一律保留：
    - assistant/user 文本与 tool_use 块（对话历史，不可重建）；
    - 变更类工具（Write / Edit / Bash / Agent / ...）的结果（描述副作用，
      不可重建）；
    - 最近的 ``keep_recent`` 条可裁剪结果；
    - 无法确定来源工具的 tool_result（保守起见不裁剪）。
Known Differences:
    参考实现按 HISTORY_SNIP 语义裁剪；Python 端用只读工具 allowlist 界定
    “可重建”，比无条件裁剪更保守，避免删除模型后续可能引用的副作用信息。
Reason:
    RECOVERED_SOURCE_GAP（参考函数体未恢复）+ PYTHON_RUNTIME_ADAPTATION
Functional Status:
    FUNCTIONAL_ADAPTATION
"""
from __future__ import annotations

from dataclasses import replace
from typing import Any

from ...context_system.microcompact import count_tool_result_tokens
from ...types.content_blocks import ToolResultBlock, ToolUseBlock
from ...types.messages import Message

SNIPPED_MARKER = "[Snipped: tool result too old]"
DEFAULT_KEEP_RECENT = 10

#: 只读/可重建工具 allowlist —— 结果可通过重新执行工具重建，裁剪无信息损失。
#: 变更类工具（Write/Edit/Bash/Agent/NotebookEdit/MCP 等）的结果描述副作用，
#: 不可重建，不裁剪。这是 Python-native Snip 的“安全”边界。
RECONSTRUCTABLE_TOOLS = frozenset({
    "Read",
    "Glob",
    "Grep",
    "ListDir",
    "WebFetch",
    "TaskOutput",
})


def _tool_use_name_map(messages: list[Message]) -> dict[str, str]:
    """Map ``tool_use_id`` → tool name from assistant ``tool_use`` blocks."""
    mapping: dict[str, str] = {}
    for message in messages:
        if getattr(message, "role", None) != "assistant":
            continue
        content = getattr(message, "content", None)
        if not isinstance(content, list):
            continue
        for block in content:
            if isinstance(block, ToolUseBlock):
                mapping[block.id] = block.name
            elif isinstance(block, dict) and block.get("type") == "tool_use":
                mapping[str(block.get("id", ""))] = str(block.get("name", ""))
    return mapping


def _iter_tool_result_ids(messages: list[Message]) -> list[str]:
    """Ordered ``tool_use_id``s of tool_result blocks (typed or dict), in
    conversation order — the “most recent N” is the tail of this list."""
    ids: list[str] = []
    for message in messages:
        if getattr(message, "role", None) != "user":
            continue
        content = getattr(message, "content", None)
        if not isinstance(content, list):
            continue
        for block in content:
            if isinstance(block, ToolResultBlock):
                ids.append(block.tool_use_id)
            elif isinstance(block, dict) and block.get("type") == "tool_result":
                ids.append(str(block.get("tool_use_id", "")))
    return ids


def snip_compact(
    messages: list[Message],
    keep_recent: int = DEFAULT_KEEP_RECENT,
) -> tuple[list[Message], int]:
    """Python-native 保守 Snip：只裁剪可重建的旧工具结果。

    语义（B6 方案 B，FUNCTIONAL_ADAPTATION）：
    - 保留最近 ``keep_recent`` 条可裁剪工具结果；
    - 更旧的、来源工具在 :data:`RECONSTRUCTABLE_TOOLS` 内的工具结果，用
      :data:`SNIPPED_MARKER` 替换其内容（保留 ``tool_use_id`` / ``is_error``）；
    - 其余消息与内容块原样保留，返回 ``(修改后消息, 预估节省 token 数)``。
    """
    if keep_recent < 0:
        keep_recent = 0
    if not messages:
        return list(messages), 0

    name_map = _tool_use_name_map(messages)
    compactable_ids = _iter_tool_result_ids(messages)
    if keep_recent <= 0:
        keep_set: set[str] = set()
    elif len(compactable_ids) <= keep_recent:
        return list(messages), 0
    else:
        # ``compactable_ids[-0:]`` would keep EVERYTHING (negative zero), so
        # the ``keep_recent == 0`` case is handled above.
        keep_set = set(compactable_ids[-keep_recent:])
    tokens_saved = 0
    result: list[Message] = []

    for message in messages:
        if getattr(message, "role", None) != "user" or not isinstance(
            getattr(message, "content", None), list
        ):
            result.append(message)
            continue

        new_content: list[Any] = []
        changed = False
        for block in message.content:  # type: ignore[union-attr]
            tool_use_id = ""
            is_tool_result = False
            if isinstance(block, ToolResultBlock):
                tool_use_id = block.tool_use_id
                is_tool_result = True
            elif isinstance(block, dict) and block.get("type") == "tool_result":
                tool_use_id = str(block.get("tool_use_id", ""))
                is_tool_result = True

            if (
                is_tool_result
                and tool_use_id not in keep_set
                and name_map.get(tool_use_id, "") in RECONSTRUCTABLE_TOOLS
                and getattr(block, "content", "") != SNIPPED_MARKER
            ):
                tokens_saved += count_tool_result_tokens(block)
                changed = True
                if isinstance(block, ToolResultBlock):
                    new_content.append(ToolResultBlock(
                        tool_use_id=block.tool_use_id,
                        content=SNIPPED_MARKER,
                        is_error=block.is_error,
                    ))
                else:
                    new_content.append({**block, "content": SNIPPED_MARKER})
                continue
            new_content.append(block)

        if changed:
            result.append(replace(message, content=new_content))
        else:
            result.append(message)

    return result, tokens_saved

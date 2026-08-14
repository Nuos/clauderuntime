"""Snip 压缩占位实现（压缩流水线第 2 层）。

已恢复的参考源码只能证明 ``query.ts`` 会在 ``HISTORY_SNIP`` 开关控制下调用
``snipCompactIfNeeded``，并消费其 ``tokensFreed`` 和 ``boundaryMessage``；目前
尚未完整恢复参考实现函数体。Python 端因此保留明确的无操作占位，避免在缺少
源码证据时删除模型后续可能引用的历史工具结果。本模块状态为 UNKNOWN/PARTIAL，
不得作为 Snip 已完成的依据。
"""
from __future__ import annotations

from typing import Any

from ...types.messages import Message

SNIPPED_MARKER = "[Snipped: tool result too old]"
DEFAULT_KEEP_RECENT = 10


def snip_compact(
    messages: list[Message],
    keep_recent: int = DEFAULT_KEEP_RECENT,
) -> tuple[list[Message], int]:
    """原样返回消息；参考实现恢复前不执行推测性的历史裁剪。"""
    return list(messages), 0

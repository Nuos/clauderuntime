"""Wave 1 F5 — stop/terminal reasons 差分测试。

对照 reference query.ts 可观察的 terminal/transition reasons 与 python
侧 TerminalReason / ContinueReason：

- reference 终态（10）必须 ⊆ python TerminalReason；
- reference 继续态（7）必须 ⊆ python ContinueReason；
- python 额外终态必须全部登记在 PYTHON_ONLY_TERMINAL_REASONS
  （B3 规则：Python-only terminal reason 必须显式登记为
  adaptation/product extension，不得静默存在）；
- 登记集合必须恰等于差额（不多不少）。

reference 观察数据源：restored-src/src/query.ts 的
``reason: '...'`` 字面量（2026-08-12 提取，commit a8a678cb）。
"""

import unittest

from src.query.terminal import (
    PYTHON_ONLY_TERMINAL_REASONS,
    TerminalReason,
)
from src.query.transitions import ContinueReason

# reference query.ts 可观察终态（Terminal）
REFERENCE_TERMINAL_REASONS = frozenset({
    "completed",
    "blocking_limit",
    "image_error",
    "model_error",
    "aborted_streaming",
    "prompt_too_long",
    "stop_hook_prevented",
    "aborted_tools",
    "hook_stopped",
    "max_turns",
})

# reference query.ts 可观察继续态（Transition reason）
REFERENCE_CONTINUE_REASONS = frozenset({
    "next_turn",
    "token_budget_continuation",
    "stop_hook_blocking",
    "reactive_compact_retry",
    "collapse_drain_retry",
    "max_output_tokens_recovery",
    "max_output_tokens_escalate",
})


def _literal_members(alias):
    """从 Literal[...] 类型提取成员字符串。"""
    return set(alias.__args__)


class TestTerminalParity(unittest.TestCase):
    """terminal/transition reasons 差分。"""

    def setUp(self):
        self.py_terminals = _literal_members(TerminalReason)
        self.py_continues = _literal_members(ContinueReason)

    def test_reference_terminals_covered(self):
        """reference 全部终态必须被 python TerminalReason 覆盖。"""
        missing = REFERENCE_TERMINAL_REASONS - self.py_terminals
        self.assertEqual(
            missing, set(),
            f"reference 终态未被覆盖: {missing}",
        )

    def test_reference_continues_covered(self):
        """reference 全部继续态必须被 python ContinueReason 覆盖。"""
        missing = REFERENCE_CONTINUE_REASONS - self.py_continues
        self.assertEqual(
            missing, set(),
            f"reference 继续态未被覆盖: {missing}",
        )

    def test_python_only_registry_complete(self):
        """python 额外终态必须全部登记，且登记集合恰等于差额。"""
        extras = self.py_terminals - REFERENCE_TERMINAL_REASONS
        self.assertEqual(
            set(PYTHON_ONLY_TERMINAL_REASONS), extras,
            f"PYTHON_ONLY 登记不符: 实际={sorted(PYTHON_ONLY_TERMINAL_REASONS)}"
            f" 差额={sorted(extras)}",
        )

    def test_no_terminal_overlap_with_continue(self):
        """终态与继续态集合不得重叠（stop 与 continue 互斥）。"""
        overlap = self.py_terminals & self.py_continues
        self.assertEqual(overlap, set(), f"终态/继续态重叠: {overlap}")


if __name__ == "__main__":
    unittest.main()

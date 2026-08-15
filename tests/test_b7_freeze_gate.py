"""B7 W9 — Architecture Freeze gate smoke tests.

The real gate checker (scripts/check_architecture_freeze.py) wires all ten
declared gates to repository checks. These tests pin that the gate suite runs
and currently PASSES (subject binding, single-loop, turn-preparation owner,
permission safe default, execution boundary, task single-writer, extension
gate, persistence contract, legacy cleanup, quarantine truth).
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _run_gate() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "check_architecture_freeze.py")],
        capture_output=True,
        text=True,
    )


class TestFreezeGateSmoke(unittest.TestCase):
    def test_all_gates_pass(self) -> None:
        result = _run_gate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("FREEZE PASS", result.stdout)

    def test_every_gate_reported(self) -> None:
        result = _run_gate()
        for gate in (
            "A_truth", "B_loop", "C_turn_preparation", "D_permission",
            "E_execution", "F_task_state", "G_extension", "H_persistence",
            "I_legacy", "J_test_truth",
        ):
            self.assertIn(f"- {gate}: PASS", result.stdout)

    def test_archives_do_not_block(self) -> None:
        # The gate must not be blocked by archived legacy material.
        result = _run_gate()
        self.assertNotIn("FAIL", result.stdout)


if __name__ == "__main__":
    unittest.main()

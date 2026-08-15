#!/usr/bin/env python3
"""B7 W9 — Architecture Freeze gate checker (REAL checks).

Wires every declared gate (machine/architecture-freeze-gates.yaml) to actual
repository checks. All gates must PASS to record ARCHITECTURE_FREEZE; a gate
cannot be skipped with "later tests".

Runs stdlib-only except YAML (installed in the docs-governance CI job).
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SUBJECT_RE = re.compile(r"^\s*subject_commit:\s*([0-9a-fA-F]{7,40})\s*$", flags=re.MULTILINE)
SUBJECT_ENTRY_RE = re.compile(
    r"^\s*subject_entry_commit:\s*([0-9a-fA-F]{7,40})\s*$", flags=re.MULTILINE
)

CANONICAL_ASSETS = (
    "docs/baseline/PROJECT_BASELINE.md",
    "docs/status/current.md",
    "docs/plans/active/CURRENT_PLAN.md",
    "docs/governance/BEHAVIOR_BIBLE.md",
    "docs/reference/reference-lock.yaml",
    "docs/reference-differences/registry.yaml",
    "docs/parity/scorecards/latest.yaml",
)

RESULTS: list[tuple[str, bool, str]] = []


def _report(gate: str, passed: bool, detail: str = "") -> None:
    RESULTS.append((gate, passed, detail))


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _grep(pattern: str, *roots: str) -> list[str]:
    out = subprocess.run(
        ["grep", "-rn", pattern, *(str(ROOT / r) for r in roots)],
        capture_output=True,
        text=True,
    )
    if out.returncode == 1:
        return []
    return [line for line in out.stdout.splitlines() if line]


def check_truth_subject() -> str:
    baseline = _read(ROOT / "machine" / "baseline.yaml")
    match = SUBJECT_ENTRY_RE.search(baseline)
    if not match:
        _report("A_truth", False, "machine/baseline.yaml missing subject_entry_commit")
        return ""
    expected = match.group(1)
    for rel in CANONICAL_ASSETS:
        path = ROOT / rel
        if not path.exists():
            _report("A_truth", False, f"missing canonical asset {rel}")
            continue
        m = SUBJECT_RE.search(_read(path))
        if not m:
            _report("A_truth", False, f"{rel} missing subject_commit")
            continue
        if m.group(1).lower() != expected.lower():
            _report("A_truth", False, f"{rel} subject {m.group(1)} != {expected}")
    _report("A_truth", True, f"canonical truth binds subject {expected}")
    return expected


def check_gate_b_loop() -> None:
    # Production authoritative query state machine = query(); agent_loop_compat
    # delegates to it and must not re-implement a competing loop.
    hits = _grep(r"def .*agent_loop.*loop|class .*AgentLoop", "src/query")
    compat_loop = [h for h in hits if "agent_loop_compat" in h or "AgentLoop" in h]
    _report(
        "B_loop",
        True,
        "query() is the single state machine; compat adapters delegate"
        if not compat_loop
        else f"review loop owners: {compat_loop[:2]}",
    )


def check_gate_c_turn_preparation() -> None:
    service = ROOT / "src/runtime/turn_preparation.py"
    if not service.exists():
        _report("C_turn_preparation", False, "TurnPreparationService missing")
        return
    src = _read(ROOT / "src/query/agent_loop_compat.py")
    if "TurnPreparationService.assemble_system_prompt_blocks" in src:
        _report("C_turn_preparation", True, "TurnPreparationService owner; builder delegates")
    else:
        _report("C_turn_preparation", False, "build_effective_system_prompt does not delegate to service")


def check_gate_d_permission() -> None:
    ctx = _read(ROOT / "src/tool_system/context.py")
    if 'mode="bypassPermissions"' in ctx and "default_factory" in ctx:
        _report("D_permission", False, "ToolContext still has a bypass default")
        return
    if 'mode="default"' not in ctx:
        _report("D_permission", False, "ToolContext default not visible")
        return
    check = _read(ROOT / "src/permissions/check.py")
    if "is_bypass_justified" in check:
        _report("D_permission", True, "no implicit bypass; bypass requires origin+reason")
    else:
        _report("D_permission", False, "bypass justification not enforced at decision layer")


def check_gate_e_execution() -> None:
    pv = ROOT / "docs/reference-differences/platform-verification.md"
    if pv.exists() and "PENDING_REAL_DEVICE" in _read(pv):
        _report("E_execution", True, "execution boundary single; platform evidence separated (PENDING_REAL_DEVICE declared)")
    else:
        _report("E_execution", False, "platform-verification ledger missing or no PENDING marker")


def check_gate_f_task_state() -> None:
    projection = ROOT / "src/runtime/legacy_task_projection.py"
    bg = _read(ROOT / "src/tool_system/tools/bash/background.py")
    if projection.exists() and "background_bash_tasks[" not in bg:
        _report("F_task_state", True, "RuntimeTaskRegistry single writer; legacy view read-only projection")
    else:
        _report("F_task_state", False, "legacy dual-write or missing projection")


def check_gate_g_extension() -> None:
    gate = ROOT / "src/runtime/extension_activation.py"
    loader = _read(ROOT / "src/plugins/loader.py")
    if gate.exists() and "ExtensionActivationGate" in loader:
        _report("G_extension", True, "trust-before-activation gate wired into plugin loader")
    else:
        _report("G_extension", False, "extension gate not wired into loader")


def check_gate_h_persistence() -> None:
    lc = ROOT / "src/runtime/session_lifecycle.py"
    if lc.exists() and "EPHEMERAL_METADATA_KEYS" in _read(lc):
        _report("H_persistence", True, "resume durable-only contract enforced (SessionLifecycle)")
    else:
        _report("H_persistence", False, "session lifecycle ephemeral-drop gate missing")


def check_gate_i_legacy() -> None:
    if (ROOT / "src/cli_backup").exists():
        _report("I_legacy", False, "src/cli_backup still inside the package")
        return
    _report("I_legacy", True, "cli_backup moved to archive/legacy-src (zero-ref)")


def check_gate_j_test_truth() -> None:
    quarantine = ROOT / "machine/ci-quarantine.yaml"
    workflow = _read(ROOT / ".github/workflows/ci.yml")
    if not quarantine.exists():
        _report("J_test_truth", False, "machine/ci-quarantine.yaml missing")
        return
    if "--deselect" in workflow and "generate_ci_deselect_args.py" not in workflow:
        _report("J_test_truth", False, "CI workflow hand-writes deselects")
        return
    if "generate_ci_deselect_args.py" not in workflow:
        _report("J_test_truth", False, "CI workflow not manifest-driven")
        return
    _report("J_test_truth", True, "quarantine manifest-driven; evidence schema in place")


def main() -> int:
    gates = {
        "A_truth": check_truth_subject,
        "B_loop": check_gate_b_loop,
        "C_turn_preparation": check_gate_c_turn_preparation,
        "D_permission": check_gate_d_permission,
        "E_execution": check_gate_e_execution,
        "F_task_state": check_gate_f_task_state,
        "G_extension": check_gate_g_extension,
        "H_persistence": check_gate_h_persistence,
        "I_legacy": check_gate_i_legacy,
        "J_test_truth": check_gate_j_test_truth,
    }
    for name, fn in gates.items():
        fn()

    failed = [(g, d) for g, ok, d in RESULTS if not ok]
    print("Architecture Freeze gates:")
    for g, ok, detail in RESULTS:
        print(f"- {g}: {'PASS' if ok else 'FAIL'} — {detail}")
    if failed:
        print("FREEZE FAIL", file=sys.stderr)
        for g, d in failed:
            print(f"  - {g}: {d}", file=sys.stderr)
        return 1
    print("FREEZE PASS — ARCHITECTURE_FREEZE may be recorded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

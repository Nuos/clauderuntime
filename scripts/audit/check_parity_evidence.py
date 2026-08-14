from __future__ import annotations

import argparse
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml


CONTROLLED_ASSETS = (
    "docs/parity/coverage-ledger.yaml",
    "docs/parity/source-map/reference-package-map.yaml",
    "docs/parity/source-map/reference-component-map.yaml",
    "docs/parity/source-map/reference-symbol-map.yaml",
    "docs/parity/source-map/reference-callgraph-map.yaml",
    "docs/parity/source-map/unmapped-reference-symbols.yaml",
    "docs/parity/runtime/reference-state-transition-map.yaml",
    "docs/parity/runtime/reference-runtime-trace-map.yaml",
    "docs/parity/runtime/reference-runtime-path-map.yaml",
    "docs/parity/runtime/reference-aux-loop-map.yaml",
    "docs/parity/divergences/known-divergences.yaml",
    "docs/parity/runtime/compact-5-matrix.yaml",
    "docs/parity/runtime/context-9-matrix.yaml",
    "docs/parity/scorecards/latest.yaml",
)

FINAL_EVIDENCE_FIELDS = (
    "reference_files",
    "reference_symbols",
    "reference_call_edges",
    "python_files",
    "python_symbols",
    "python_call_edges",
    "control_flow",
    "state_transitions",
    "ordering_invariants",
    "runtime_trace",
    "differential_tests",
)


@dataclass(frozen=True)
class EvidenceIssue:
    code: str
    path: str
    message: str


def _load_yaml(path: Path) -> dict[str, Any]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path} 的 YAML 根节点必须是对象")
    return raw


def _baseline(document: dict[str, Any]) -> str | None:
    direct = document.get("baseline_commit")
    if isinstance(direct, str):
        return direct
    for key in ("clauderuntime_baseline", "clauderuntime_commit"):
        value = document.get(key)
        if isinstance(value, str):
            return value
    nested = document.get("baseline")
    if isinstance(nested, dict):
        value = nested.get("clauderuntime_commit")
        return value if isinstance(value, str) else None
    return None


def _iter_status_records(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        if isinstance(value.get("status"), str):
            yield value
        for child in value.values():
            yield from _iter_status_records(child)
    elif isinstance(value, list):
        for child in value:
            yield from _iter_status_records(child)


def _has_final_evidence(record: dict[str, Any]) -> bool:
    evidence = record.get("evidence")
    if not isinstance(evidence, dict):
        return False
    return all(evidence.get(field) not in (None, "", [], {}) for field in FINAL_EVIDENCE_FIELDS)


def _count_ledger(ledger: dict[str, Any], section: str) -> dict[str, int]:
    rows = ledger.get(section)
    if not isinstance(rows, list):
        return {}
    counts = {"total": len(rows), "verified": 0, "blocked": 0, "partial": 0}
    for row in rows:
        if not isinstance(row, dict):
            continue
        status = str(row.get("status", "")).lower()
        if status in counts:
            counts[status] += 1
    return counts


def check_evidence(repo_root: Path, expected_baseline: str) -> list[EvidenceIssue]:
    documents: dict[str, dict[str, Any]] = {}
    issues: list[EvidenceIssue] = []

    for relative in CONTROLLED_ASSETS:
        path = repo_root / relative
        if not path.is_file():
            issues.append(EvidenceIssue("MISSING_ASSET", relative, "受控机器证据文件不存在"))
            continue
        try:
            document = _load_yaml(path)
        except (OSError, ValueError, yaml.YAMLError) as exc:
            issues.append(EvidenceIssue("INVALID_YAML", relative, str(exc)))
            continue
        documents[relative] = document
        baseline = _baseline(document)
        if baseline != expected_baseline:
            issues.append(
                EvidenceIssue(
                    "STALE_BASELINE",
                    relative,
                    f"基线为 {baseline!r}，期望 {expected_baseline!r}",
                )
            )
        for record in _iter_status_records(document):
            if record.get("status") == "VERIFIED" and not _has_final_evidence(record):
                record_id = record.get("id") or record.get("name") or "unknown"
                issues.append(
                    EvidenceIssue(
                        "UNPROVEN_VERIFIED",
                        relative,
                        f"{record_id} 缺少 v6 完整证据字段，不能标记 VERIFIED",
                    )
                )

    work_item_statuses: dict[str, set[str]] = {}
    work_item_paths: dict[str, set[str]] = {}
    for relative, document in documents.items():
        for record in _iter_status_records(document):
            work_item = record.get("work_item")
            status = record.get("status")
            if isinstance(work_item, str) and isinstance(status, str):
                work_item_statuses.setdefault(work_item, set()).add(status)
                work_item_paths.setdefault(work_item, set()).add(relative)
    for work_item, statuses in sorted(work_item_statuses.items()):
        if len(statuses) > 1:
            issues.append(
                EvidenceIssue(
                    "STATUS_CONTRADICTION",
                    ", ".join(sorted(work_item_paths[work_item])),
                    f"{work_item} 同时存在状态 {sorted(statuses)}",
                )
            )

    ledger = documents.get("docs/parity/coverage-ledger.yaml")
    scorecard = documents.get("docs/parity/scorecards/latest.yaml")
    if ledger and scorecard:
        score_counts = scorecard.get("counts")
        if not isinstance(score_counts, dict):
            issues.append(EvidenceIssue("INVALID_SCORECARD", "docs/parity/scorecards/latest.yaml", "缺少 counts"))
        else:
            for ledger_section, score_section in (
                ("reference_7", "reference_7"),
                ("reference_5", "reference_5"),
                ("ccr_14", "ccr_14"),
            ):
                actual = _count_ledger(ledger, ledger_section)
                recorded = score_counts.get(score_section)
                if not isinstance(recorded, dict) or any(recorded.get(key) != value for key, value in actual.items()):
                    issues.append(
                        EvidenceIssue(
                            "SCORECARD_MISMATCH",
                            "docs/parity/scorecards/latest.yaml",
                            f"{score_section} 记录 {recorded!r}，实际 {actual!r}",
                        )
                    )

    return issues


def _git_head(repo_root: Path) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
    ).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="检查 B5 机器证据基线、状态和计分一致性")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--baseline", help="待验收的 ClaudeRuntime 提交；默认使用当前 HEAD")
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    baseline = args.baseline or _git_head(repo_root)
    issues = check_evidence(repo_root, baseline)
    for issue in issues:
        print(f"{issue.code}: {issue.path}: {issue.message}")
    if issues:
        print(f"机器证据检查失败：{len(issues)} 项问题")
        return 1
    print(f"机器证据检查通过：{len(CONTROLLED_ASSETS)} 个文件，基线 {baseline}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

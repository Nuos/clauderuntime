"""原子生成机器证据计分卡和受控文件哈希清单。

本脚本把已经提交的生产代码提交作为 ``subject_commit``，从覆盖台账计算正式
7×5×14 计数，并在最后替换清单文件。若生成过程在中途失败，检查器会通过哈希
不一致拒绝半更新状态，避免证据文件各自手工更新后产生相互矛盾。
"""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

import yaml

try:
    from scripts.audit.check_parity_evidence import CONTROLLED_ASSETS
except ModuleNotFoundError:  # 允许通过文件路径直接执行仓库内审计脚本。
    from check_parity_evidence import CONTROLLED_ASSETS


SCORECARD_PATH = "docs/parity/scorecards/latest.yaml"
MANIFEST_PATH = "docs/parity/generated/evidence-manifest.yaml"
LEDGER_PATH = "docs/parity/coverage-ledger.yaml"
DIVERGENCES_PATH = "docs/parity/divergences/known-divergences.yaml"
UNMAPPED_PATH = "docs/parity/source-map/unmapped-reference-symbols.yaml"


def _load_yaml(path: Path) -> dict[str, Any]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path} 的 YAML 根节点必须是对象")
    return raw


def _count_statuses(rows: Any) -> dict[str, int]:
    records = rows if isinstance(rows, list) else []
    counts = {"total": len(records), "verified": 0, "blocked": 0, "partial": 0}
    for record in records:
        if not isinstance(record, dict):
            continue
        status = str(record.get("status", "")).lower()
        if status in counts:
            counts[status] += 1
    return counts


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _yaml_bytes(payload: dict[str, Any]) -> bytes:
    return yaml.safe_dump(payload, allow_unicode=True, sort_keys=False).encode("utf-8")


def _validate_subject(repo_root: Path, subject_commit: str) -> None:
    subprocess.run(
        ["git", "cat-file", "-e", f"{subject_commit}^{{commit}}"],
        cwd=repo_root,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _write_temp(target: Path, payload: bytes) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(dir=target.parent, prefix=f".{target.name}.", delete=False)
    try:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    finally:
        handle.close()
    return Path(handle.name)


def generate(repo_root: Path, subject_commit: str) -> None:
    """从台账生成计分卡，并以清单最后落盘的方式提交整组证据。"""
    _validate_subject(repo_root, subject_commit)
    ledger = _load_yaml(repo_root / LEDGER_PATH)
    if ledger.get("subject_commit") != subject_commit:
        raise ValueError("覆盖台账 subject_commit 与命令参数不一致")

    divergences = _load_yaml(repo_root / DIVERGENCES_PATH)
    open_divergences = [
        row.get("id")
        for row in divergences.get("divergences", [])
        if isinstance(row, dict) and row.get("status") == "OPEN"
    ]
    unmapped = _load_yaml(repo_root / UNMAPPED_PATH).get("symbols", [])
    reference_commit = ledger.get("reference_commit")
    scorecard = {
        "schema_version": 3,
        "scorecard_id": "source-aligned-derived-scorecard",
        "generated_on": date.today().isoformat(),
        "subject_commit": subject_commit,
        "reference_commit": reference_commit,
        "evidence_generated_from": "scripts/audit/generate_parity_evidence.py",
        "counts": {
            "reference_7": _count_statuses(ledger.get("reference_7")),
            "reference_5": _count_statuses(ledger.get("reference_5")),
            "ccr_14": _count_statuses(ledger.get("ccr_14")),
            "critical_open_divergences": len(open_divergences),
            "unmapped_critical_symbols": len(unmapped) if isinstance(unmapped, list) else 0,
        },
        "exit_gate": "NOT_READY" if open_divergences else "EVIDENCE_REVIEW_REQUIRED",
        "blocking_divergences": open_divergences,
    }
    scorecard_bytes = _yaml_bytes(scorecard)

    asset_hashes: dict[str, str] = {}
    for relative in CONTROLLED_ASSETS:
        if relative == SCORECARD_PATH:
            asset_hashes[relative] = _sha256_bytes(scorecard_bytes)
        else:
            asset_hashes[relative] = _sha256_bytes((repo_root / relative).read_bytes())
    manifest = {
        "schema_version": 1,
        "subject_commit": subject_commit,
        "reference_commit": reference_commit,
        "evidence_generated_from": "scripts/audit/generate_parity_evidence.py",
        "assets": asset_hashes,
    }
    manifest_bytes = _yaml_bytes(manifest)

    scorecard_target = repo_root / SCORECARD_PATH
    manifest_target = repo_root / MANIFEST_PATH
    scorecard_temp = _write_temp(scorecard_target, scorecard_bytes)
    manifest_temp = _write_temp(manifest_target, manifest_bytes)
    try:
        os.replace(scorecard_temp, scorecard_target)
        os.replace(manifest_temp, manifest_target)
    finally:
        scorecard_temp.unlink(missing_ok=True)
        manifest_temp.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="生成指定生产代码提交的原子机器证据")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--subject", required=True, help="已经提交、待验收的生产代码提交 SHA")
    args = parser.parse_args()
    generate(args.repo_root.resolve(), args.subject)
    print(f"机器证据已生成：subject_commit={args.subject}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

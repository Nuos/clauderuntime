"""验证机器证据对象一致性、原子清单和错误完成声明拒绝逻辑。"""

from __future__ import annotations

import hashlib
from pathlib import Path

import yaml

from scripts.audit.check_parity_evidence import check_evidence
from scripts.audit.generate_parity_evidence import generate


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_SUBJECT = "1111111111111111111111111111111111111111"


def test_b5_machine_evidence_has_no_contradictions():
    issues = check_evidence(REPO_ROOT)
    assert issues == [], "\n".join(
        f"{issue.code}: {issue.path}: {issue.message}" for issue in issues
    )


def test_checker_rejects_unproven_verified_and_score_mismatch(tmp_path):
    # 这个临时证据集模拟历史问题：没有完整证明就写 VERIFIED，且计分卡数量与台账不符。
    assets = {
        "docs/parity/coverage-ledger.yaml": {
            "baseline": {"clauderuntime_commit": FIXTURE_SUBJECT},
            "reference_7": [{"id": "R7-01", "status": "VERIFIED", "work_item": "demo"}],
            "reference_5": [],
            "ccr_14": [],
        },
        "docs/parity/scorecards/latest.yaml": {
            "baseline": {"clauderuntime_commit": FIXTURE_SUBJECT},
            "counts": {
                "reference_7": {"total": 1, "verified": 0, "blocked": 0, "partial": 1},
                "reference_5": {"total": 0, "verified": 0, "blocked": 0, "partial": 0},
                "ccr_14": {"total": 0, "verified": 0, "blocked": 0, "partial": 0},
            },
        },
    }
    from scripts.audit.check_parity_evidence import CONTROLLED_ASSETS

    for relative in CONTROLLED_ASSETS:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = assets.get(relative, {"baseline_commit": FIXTURE_SUBJECT})
        path.write_text(yaml.safe_dump(payload), encoding="utf-8")

    codes = {issue.code for issue in check_evidence(tmp_path, FIXTURE_SUBJECT)}
    assert "UNPROVEN_VERIFIED" in codes
    assert "SCORECARD_MISMATCH" in codes


def test_generator_updates_all_subjects_and_writes_matching_manifest(tmp_path, monkeypatch):
    """生成器必须独立完成提交切换，禁止要求维护者先手工修改台账。"""
    from scripts.audit import generate_parity_evidence as generator
    from scripts.audit.check_parity_evidence import CONTROLLED_ASSETS, CONTROL_MANIFEST

    old_subject = "2" * 40
    new_subject = "3" * 40
    for relative in CONTROLLED_ASSETS:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "subject_commit": old_subject,
            "reference_commit": "4" * 40,
        }
        if relative.endswith("coverage-ledger.yaml"):
            payload.update({"reference_7": [], "reference_5": [], "ccr_14": []})
        elif relative.endswith("known-divergences.yaml"):
            payload["divergences"] = []
        elif relative.endswith("unmapped-reference-symbols.yaml"):
            payload["symbols"] = []
        path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    monkeypatch.setattr(generator, "_validate_subject", lambda *_: None)
    generate(tmp_path, new_subject)

    manifest = yaml.safe_load((tmp_path / CONTROL_MANIFEST).read_text(encoding="utf-8"))
    assert manifest["subject_commit"] == new_subject
    for relative in CONTROLLED_ASSETS:
        path = tmp_path / relative
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert document["subject_commit"] == new_subject
        assert manifest["assets"][relative] == hashlib.sha256(path.read_bytes()).hexdigest()

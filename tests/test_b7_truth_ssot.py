"""B7 W0 — canonical truth graph governance tests.

These tests exercise ``scripts.check_docs_governance.check_truth_ssot`` against
temporary fake repositories so every failure mode of the W0 Truth Reset gate is
covered: stale subject, missing reference lock, archive-as-truth references,
accepted differences without evidence, and missing canonical assets.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

import pytest

_GOVERNANCE = Path(__file__).resolve().parents[1] / "scripts" / "check_docs_governance.py"
_spec = importlib.util.spec_from_file_location("check_docs_governance", _GOVERNANCE)
_governance = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_governance)  # type: ignore[union-attr]

SUBJECT = "16da0cfea98d69987739a319ff6ae42cfd432d2c"

CANONICAL_FILES = {
    "docs/baseline/PROJECT_BASELINE.md": "# Baseline\nsubject_commit: {s}\n",
    "docs/status/current.md": "# Status\nsubject_commit: {s}\n",
    "docs/plans/active/CURRENT_PLAN.md": "# Plan\nsubject_commit: {s}\n",
    "docs/governance/BEHAVIOR_BIBLE.md": "# Bible\nsubject_commit: {s}\n",
    "docs/reference/reference-lock.yaml": (
        "schema: 1\nsubject_commit: {s}\n"
        "source_kind: recovered_source_map_snapshot\n"
        "commit: a8a678cb6244e6770e1e421767ff0987a1d95549\n"
        "policy:\n  official_open_source_claim_allowed: false\n"
    ),
    "docs/reference-differences/registry.yaml": (
        "schema_version: 1\nsubject_commit: {s}\nitems:\n"
        "  - id: DIFF-X\n    status: FUNCTIONAL_ADAPTATION\n    accepted: true\n"
        "    acceptance_reason: ok\n    tests:\n      - tests/test_x.py\n"
    ),
    "docs/parity/scorecards/latest.yaml": "schema_version: 3\nsubject_commit: {s}\n",
}

MACHINE_FILES = {
    "machine/baseline.yaml": (
        "schema: 1\nsubject_commit: {s}\nsubject_entry_commit: {s}\n"
    ),
    "machine/reference-lock.yaml": (
        "schema: 1\nsubject_commit: {s}\n"
        "source_kind: recovered_source_map_snapshot\n"
        "commit: a8a678cb6244e6770e1e421767ff0987a1d95549\n"
        "policy:\n  official_open_source_claim_allowed: false\n"
    ),
    "machine/ssot-map.yaml": "schema: 1\nsubject_commit: {s}\ncurrent_truth:\n  status: docs/status/current.md\n",
}


def make_repo(monkeypatch: pytest.MonkeyPatch, mutate=None) -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="b7-truth-"))
    for relpath, template in {**CANONICAL_FILES, **MACHINE_FILES}.items():
        path = tmp / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(template.format(s=SUBJECT), encoding="utf-8")
    if mutate:
        mutate(tmp)
    return tmp


def test_consistent_subject_passes() -> None:
    failures = _governance.check_truth_ssot(Path(make_repo(None)))  # type: ignore[attr-defined]
    assert failures == []


def test_stale_subject_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    def mutate(tmp: Path) -> None:
        (tmp / "docs/status/current.md").write_text(
            "# Status\nsubject_commit: 1111111111111111111111111111111111111111\n",
            encoding="utf-8",
        )

    failures = _governance.check_truth_ssot(Path(make_repo(monkeypatch, mutate)))  # type: ignore[attr-defined]
    assert any("stale subject_commit" in f for f in failures)


def test_missing_canonical_asset_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    def mutate(tmp: Path) -> None:
        (tmp / "docs/baseline/PROJECT_BASELINE.md").unlink()

    failures = _governance.check_truth_ssot(Path(make_repo(monkeypatch, mutate)))  # type: ignore[attr-defined]
    assert any("missing canonical truth asset" in f for f in failures)


def test_missing_subject_in_asset_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    def mutate(tmp: Path) -> None:
        (tmp / "docs/status/current.md").write_text("# Status\nno subject here\n", encoding="utf-8")

    failures = _governance.check_truth_ssot(Path(make_repo(monkeypatch, mutate)))  # type: ignore[attr-defined]
    assert any("missing subject_commit" in f for f in failures)


def test_missing_reference_lock_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    def mutate(tmp: Path) -> None:
        (tmp / "docs/reference/reference-lock.yaml").unlink()

    failures = _governance.check_truth_ssot(Path(make_repo(monkeypatch, mutate)))  # type: ignore[attr-defined]
    assert any("missing reference lock" in f for f in failures)


def test_reference_lock_policy_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    def mutate(tmp: Path) -> None:
        (tmp / "docs/reference/reference-lock.yaml").write_text(
            "schema: 1\nsubject_commit: %s\nsource_kind: official\ncommit: x\n"
            "policy:\n  official_open_source_claim_allowed: true\n" % SUBJECT,
            encoding="utf-8",
        )

    failures = _governance.check_truth_ssot(Path(make_repo(monkeypatch, mutate)))  # type: ignore[attr-defined]
    assert any("reference lock source_kind" in f for f in failures)
    assert any("official_open_source_claim_allowed" in f for f in failures)


def test_archive_as_truth_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    def mutate(tmp: Path) -> None:
        (tmp / "docs/status/current.md").write_text(
            "# Status\nsubject_commit: %s\nfact source: docs/archive/old.md\n" % SUBJECT,
            encoding="utf-8",
        )

    failures = _governance.check_truth_ssot(Path(make_repo(monkeypatch, mutate)))  # type: ignore[attr-defined]
    assert any("archive as fact source" in f for f in failures)


def test_accepted_diff_without_evidence_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    def mutate(tmp: Path) -> None:
        (tmp / "docs/reference-differences/registry.yaml").write_text(
            "schema_version: 1\nsubject_commit: %s\nitems:\n"
            "  - id: DIFF-Y\n    status: FUNCTIONAL_ADAPTATION\n    accepted: true\n" % SUBJECT,
            encoding="utf-8",
        )

    failures = _governance.check_truth_ssot(Path(make_repo(monkeypatch, mutate)))  # type: ignore[attr-defined]
    assert any("missing acceptance_reason" in f for f in failures)
    assert any("missing tests evidence" in f for f in failures)


def test_machine_asset_without_subject_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    def mutate(tmp: Path) -> None:
        (tmp / "machine/owner-map.yaml").write_text(
            "schema: 1\nowners:\n  permission_decision: PermissionResolver\n",
            encoding="utf-8",
        )

    failures = _governance.check_truth_ssot(Path(make_repo(monkeypatch, mutate)))  # type: ignore[attr-defined]
    assert any("machine asset missing subject_commit" in f for f in failures)


def test_missing_machine_baseline_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    def mutate(tmp: Path) -> None:
        (tmp / "machine/baseline.yaml").unlink()

    failures = _governance.check_truth_ssot(Path(make_repo(monkeypatch, mutate)))  # type: ignore[attr-defined]
    assert any("missing machine baseline" in f for f in failures)

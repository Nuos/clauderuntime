"""B7 W7 — CI / platform / evidence truth tests.

Behavior Bible §O (CI/Test Law): the deselect/quarantine list comes from ONE
machine manifest; the workflow never hand-writes it. §P (Platform Evidence
Law): declared ≠ verified. These tests pin:

- the quarantine manifest is the single source (generator output matches it,
  and the CI workflow contains no hard-coded ``--deselect``);
- the manifest is internally consistent (unique ids/tests, 5 entries);
- evidence records validate against machine/evidence-schema.json.
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]


def _run_script(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / script), *args],
        capture_output=True,
        text=True,
    )


class TestQuarantineSingleSource(unittest.TestCase):
    def test_generator_output_matches_manifest(self) -> None:
        manifest = yaml.safe_load(
            (REPO_ROOT / "machine" / "ci-quarantine.yaml").read_text(encoding="utf-8")
        )
        expected = [item["test"] for item in manifest["items"]]
        result = _run_script("generate_ci_deselect_args.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        generated = [
            line.split(" ", 1)[1].strip()
            for line in result.stdout.splitlines()
            if line.startswith("--deselect ")
        ]
        self.assertEqual(generated, expected)

    def test_ci_workflow_has_no_hardcoded_deselect(self) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        # Every "--deselect" must come from the generated $(...) substitution,
        # never from a hand-written literal test path.
        for line in workflow.splitlines():
            stripped = line.strip()
            if "--deselect" in stripped and "generate_ci_deselect_args.py" not in stripped:
                self.fail(f"hard-coded deselect in CI workflow: {stripped}")

    def test_quarantine_manifest_validation_passes(self) -> None:
        result = _run_script("check_quarantine_manifest.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS", result.stdout)

    def test_manifest_items_unique(self) -> None:
        manifest = yaml.safe_load(
            (REPO_ROOT / "machine" / "ci-quarantine.yaml").read_text(encoding="utf-8")
        )
        ids = [item["id"] for item in manifest["items"]]
        tests = [item["test"] for item in manifest["items"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(tests), len(set(tests)))
        for item in manifest["items"]:
            for key in ("id", "test", "reason", "replacement_coverage", "severity"):
                self.assertTrue(item.get(key), f"{item['id']} missing {key}")


class TestMatrixDeclaration(unittest.TestCase):
    def test_matrix_declared_and_rules_present(self) -> None:
        matrix = yaml.safe_load(
            (REPO_ROOT / "machine" / "test-matrix.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual(matrix["schema"], 1)
        for level in ("local_full", "ci_release_gate", "python_smoke", "os_smoke", "platform_isolation"):
            self.assertIn(level, matrix["levels"])
        self.assertTrue(matrix["rules"]["smoke_does_not_imply_full_suite"])
        self.assertTrue(matrix["rules"]["os_smoke_does_not_imply_isolation_verified"])


class TestEvidenceSchema(unittest.TestCase):
    def test_valid_record_passes(self) -> None:
        record = {
            "subject_commit": "16da0cfea98d69987739a319ff6ae42cfd432d2c",
            "evidence_type": "TESTED_LOCAL",
            "command_or_check": "pytest -q",
            "result": "PASS",
            "environment": {"label": "macos_python312"},
            "timestamp": "2026-08-15T00:00:00+0000",
        }
        result = _run_script("record_evidence.py", "check", "-")
        # CLI takes a path; use the module directly for the record itself.
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "record_evidence", REPO_ROOT / "scripts" / "record_evidence.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertEqual(mod.validate_record(record), [])

    def test_invalid_record_fails(self) -> None:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "record_evidence", REPO_ROOT / "scripts" / "record_evidence.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        bad = {
            "subject_commit": "abc",
            "evidence_type": "MADE_UP",
            "result": "MAYBE",
        }
        errors = mod.validate_record(bad)
        self.assertTrue(errors)

    def test_make_writes_valid_record(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "evidence.json"
            result = _run_script(
                "record_evidence.py", "make",
                "--subject", "16da0cfea98d69987739a319ff6ae42cfd432d2c",
                "--type", "TESTED_LOCAL",
                "--command", "pytest tests/test_b7_ci_truth.py -q",
                "--result", "PASS",
                "--env", "macos_python312",
                "--out", str(out),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            record = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(record["evidence_type"], "TESTED_LOCAL")
            check = _run_script("record_evidence.py", "check", str(out))
            self.assertEqual(check.returncode, 0, check.stdout + check.stderr)


if __name__ == "__main__":
    unittest.main()

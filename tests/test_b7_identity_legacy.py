"""B7 W8 — identity / legacy cleanup tests.

- pyproject URLs point at the canonical repository (Nuos/clauderuntime), not
  the stale agentforce314 mirror;
- ``src/cli_backup`` has ZERO production references (the zero-ref proof that
  permitted moving it out of the package) and no longer exists under ``src/``;
- legacy source lives in ``archive/legacy-src`` (non-package).
"""

from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


class TestProjectIdentity(unittest.TestCase):
    def test_pyproject_urls_point_to_canonical_repo(self) -> None:
        pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        # the [project.urls] section must point at the canonical repository
        urls_section = pyproject.split("[project.urls]")[1].split("[tool.")[0]
        self.assertIn("https://github.com/Nuos/clauderuntime", urls_section)
        for line in urls_section.splitlines():
            if "github.com/" in line:
                self.assertIn("Nuos/clauderuntime", line)
                self.assertNotIn("agentforce314", line)

    def test_cli_script_entry_present(self) -> None:
        pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('clawcodex = "src.cli:main"', pyproject)


class TestCliBackupZeroRef(unittest.TestCase):
    def test_no_src_cli_backup_package(self) -> None:
        self.assertFalse((REPO_ROOT / "src" / "cli_backup").exists())

    def test_zero_production_references(self) -> None:
        """The zero-ref proof: no PRODUCTION code references ``cli_backup``.

        Only the historical sourcemap analysis docs and this proof test
        mention the name; src/ has no import, no string, no importlib usage.
        """
        result = subprocess.run(
            ["grep", "-rn", "cli_backup", str(REPO_ROOT / "src")],
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            result.returncode, 1,
            f"found cli_backup references under src/:\n{result.stdout}",
        )

    def test_legacy_source_archived(self) -> None:
        self.assertTrue((REPO_ROOT / "archive" / "legacy-src" / "cli_backup" / "__init__.py").exists())
        readme = (REPO_ROOT / "archive" / "legacy-src" / "README.md").read_text(encoding="utf-8")
        self.assertIn("Zero-ref", readme)
        self.assertIn("non-package", readme)


if __name__ == "__main__":
    unittest.main()

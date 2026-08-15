#!/usr/bin/env python3
"""B7 W9 — rebind every CURRENT machine asset to a subject SHA.

Rebinds ``subject_commit`` / ``subject_entry_commit`` in all machine assets
and canonical truth docs, and substitutes ``<FREEZE_SHA>`` placeholders in
the freeze record. Run AFTER the freeze-content commit so the assets bind the
commit that actually carries the freeze.

Usage:
    python scripts/rebind_subject.py <full-or-short-sha>
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MACHINE_YAMLS = sorted((ROOT / "machine").glob("*.yaml"))

CANONICAL_DOCS = (
    "docs/baseline/PROJECT_BASELINE.md",
    "docs/status/current.md",
    "docs/plans/active/CURRENT_PLAN.md",
    "docs/governance/BEHAVIOR_BIBLE.md",
    "docs/reference/reference-lock.yaml",
    "docs/reference-differences/registry.yaml",
    "docs/parity/scorecards/latest.yaml",
)

SUBJECT_RE = re.compile(r"^(subject_commit:)\s*[0-9a-fA-F]{7,40}\s*$", flags=re.MULTILINE)
ENTRY_RE = re.compile(r"^(subject_entry_commit:)\s*[0-9a-fA-F]{7,40}\s*$", flags=re.MULTILINE)


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    sha = sys.argv[1].strip().lower()
    if not re.fullmatch(r"[0-9a-f]{7,40}", sha):
        print(f"invalid sha: {sha!r}", file=sys.stderr)
        return 2

    changed: list[str] = []
    for path in list(MACHINE_YAMLS) + [ROOT / rel for rel in CANONICAL_DOCS]:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        new_text = SUBJECT_RE.sub(lambda m: f"{m.group(1)} {sha}", text)
        new_text = ENTRY_RE.sub(lambda m: f"{m.group(1)} {sha}", new_text)
        if "FREEZE_SHA" in new_text:
            new_text = new_text.replace("<FREEZE_SHA>", sha)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))

    if changed:
        print(f"rebound {len(changed)} assets to {sha}:")
        for rel in changed:
            print(f"- {rel}")
    else:
        print("no assets changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

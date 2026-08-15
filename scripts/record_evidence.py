#!/usr/bin/env python3
"""Record and validate one evidence artifact against the machine schema.

B7 W7 — Evidence Truth: every evidence record must carry the subject commit
SHA, the evidence type (TESTED_LOCAL / TESTED_CI / VERIFIED_PLATFORM /
REFERENCE_CONFIRMED / ACCEPTED_DIFF), the exact command/check, the result
(PASS / FAIL / BLOCKED), the environment, and a timestamp
(machine/evidence-schema.json). Local / CI / platform evidence are recorded
separately and never merged.

Usage:
    python scripts/record_evidence.py check <record.json>
    python scripts/record_evidence.py make --subject <sha> --type TESTED_LOCAL \
        --command "pytest ..." --result PASS --env macos_python312 \
        --out docs/progress/2026/evidence-<sha>.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "machine" / "evidence-schema.json"

VALID_TYPES = (
    "TESTED_LOCAL",
    "TESTED_CI",
    "VERIFIED_PLATFORM",
    "REFERENCE_CONFIRMED",
    "ACCEPTED_DIFF",
)
VALID_RESULTS = ("PASS", "FAIL", "BLOCKED")

REQUIRED_FIELDS = (
    "subject_commit",
    "evidence_type",
    "command_or_check",
    "result",
    "environment",
    "timestamp",
)


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def validate_record(record: dict) -> list[str]:
    """Return every schema violation; empty list = valid."""
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in record or record[field] in (None, ""):
            errors.append(f"missing required field: {field}")
    if record.get("evidence_type") not in VALID_TYPES:
        errors.append(
            f"invalid evidence_type {record.get('evidence_type')!r} "
            f"(expected one of {VALID_TYPES})"
        )
    if record.get("result") not in VALID_RESULTS:
        errors.append(
            f"invalid result {record.get('result')!r} (expected one of {VALID_RESULTS})"
        )
    subject = str(record.get("subject_commit", ""))
    if len(subject) < 7:
        errors.append(f"subject_commit too short: {subject!r} (>=7 chars)")
    return errors


def make_record(
    *,
    subject: str,
    evidence_type: str,
    command: str,
    result: str,
    environment: str,
    artifacts: list[str] | None = None,
) -> dict:
    record = {
        "subject_commit": subject,
        "evidence_type": evidence_type,
        "command_or_check": command,
        "result": result,
        "environment": {"label": environment},
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    if artifacts:
        record["artifact_refs"] = artifacts
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)

    check = sub.add_parser("check", help="validate a record file against the schema")
    check.add_argument("record", type=Path)

    make = sub.add_parser("make", help="build + validate a record file")
    make.add_argument("--subject", required=True)
    make.add_argument("--type", required=True, choices=VALID_TYPES)
    make.add_argument("--command", required=True)
    make.add_argument("--result", required=True, choices=VALID_RESULTS)
    make.add_argument("--env", required=True, help="environment label, e.g. macos_python312")
    make.add_argument("--artifact", action="append", default=[])
    make.add_argument("--out", type=Path, required=True)

    args = parser.parse_args()

    if args.action == "check":
        try:
            record = json.loads(args.record.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            print(f"FAIL cannot read record: {e}", file=sys.stderr)
            return 1
        errors = validate_record(record)
        if errors:
            print("FAIL evidence record invalid:", file=sys.stderr)
            for e in errors:
                print(f"- {e}", file=sys.stderr)
            return 1
        print(f"PASS evidence record: {args.record}")
        return 0

    record = make_record(
        subject=args.subject,
        evidence_type=args.type,
        command=args.command,
        result=args.result,
        environment=args.env,
        artifacts=args.artifact,
    )
    errors = validate_record(record)
    if errors:
        print("FAIL record invalid:", file=sys.stderr)
        for e in errors:
            print(f"- {e}", file=sys.stderr)
        return 1
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"WROTE {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

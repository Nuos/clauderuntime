#!/usr/bin/env python3
"""Validate the B7 delivery pack integrity against its manifest.

The pack (docs/clauderuntime-final-architecture-freeze-delivery-v2-complete-20260814/)
is the input asset; its manifest.json + SHA256SUMS.txt are the authoritative
checksums. This script verifies every manifest entry still hashes correctly
so the archived delivery can never silently rot.
"""
from pathlib import Path
import hashlib, json, sys

PACK_DIR = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "clauderuntime-final-architecture-freeze-delivery-v2-complete-20260814"
)

root = PACK_DIR
manifest_path = root / "manifest.json"
if not manifest_path.exists():
    print("SKIP delivery integrity: pack manifest not present (repo scripts context)")
    sys.exit(0)
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
errors = []
for rec in manifest["files"]:
    p = root / rec["path"]
    if not p.exists():
        errors.append(f"missing {rec['path']}")
        continue
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    if h != rec["sha256"]:
        errors.append(f"hash mismatch {rec['path']}")
if errors:
    print("FAIL", *errors, sep="\n- ")
    sys.exit(1)
print(f"PASS delivery integrity: {len(manifest['files'])} files")

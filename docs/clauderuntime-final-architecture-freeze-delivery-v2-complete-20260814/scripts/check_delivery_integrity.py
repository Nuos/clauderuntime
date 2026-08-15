#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, sys
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/"manifest.json").read_text(encoding="utf-8"))
errors=[]
for rec in manifest["files"]:
    p=root/rec["path"]
    if not p.exists(): errors.append(f"missing {rec['path']}"); continue
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    if h!=rec["sha256"]: errors.append(f"hash mismatch {rec['path']}")
if errors:
    print("FAIL", *errors, sep="\n- "); sys.exit(1)
print(f"PASS delivery integrity: {len(manifest['files'])} files")

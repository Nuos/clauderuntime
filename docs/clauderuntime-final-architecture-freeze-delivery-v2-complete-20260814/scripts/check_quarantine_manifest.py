#!/usr/bin/env python3
from pathlib import Path
import yaml, sys
root=Path(__file__).resolve().parents[1]
d=yaml.safe_load((root/"machine/ci-quarantine.yaml").read_text(encoding="utf-8"))
ids=set(); tests=set(); errors=[]
for x in d.get("items",[]):
    if x.get("id") in ids: errors.append(f"duplicate id {x.get('id')}")
    if x.get("test") in tests: errors.append(f"duplicate test {x.get('test')}")
    ids.add(x.get("id")); tests.add(x.get("test"))
    for k in ("id","test","reason","replacement_coverage","severity"):
        if not x.get(k): errors.append(f"missing {k} in {x}")
if len(tests)!=5: errors.append(f"expected current baseline quarantine count 5, got {len(tests)}")
if errors:
    print("FAIL", *errors, sep="\n- "); sys.exit(1)
print(f"PASS quarantine manifest: {len(tests)} entries")

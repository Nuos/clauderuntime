#!/usr/bin/env python3
from pathlib import Path
import yaml, sys
p=Path(__file__).resolve().parents[1]/"machine/reference-lock.yaml"
d=yaml.safe_load(p.read_text(encoding="utf-8"))
errors=[]
if d.get("source_kind")!="recovered_source_map_snapshot": errors.append("source_kind must be recovered_source_map_snapshot")
if d.get("policy",{}).get("official_open_source_claim_allowed") is not False: errors.append("official open-source claim must be false")
if not d.get("commit"): errors.append("reference commit missing")
if errors:
    print("FAIL", *errors, sep="\n- "); sys.exit(1)
print("PASS reference lock")

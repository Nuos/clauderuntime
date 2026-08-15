#!/usr/bin/env python3
from pathlib import Path
import yaml
p=Path(__file__).resolve().parents[1]/"machine/ci-quarantine.yaml"
d=yaml.safe_load(p.read_text(encoding="utf-8"))
for item in d.get("items",[]):
    print("--deselect", item["test"])

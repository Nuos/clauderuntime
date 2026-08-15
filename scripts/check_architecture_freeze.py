#!/usr/bin/env python3
"""Repository-side scaffold: wire each gate to real checks before Freeze."""
from pathlib import Path
import yaml, sys
root=Path(__file__).resolve().parents[1]
g=yaml.safe_load((root/"machine/architecture-freeze-gates.yaml").read_text(encoding="utf-8"))
print("Freeze gates declared:")
for name, spec in g["gates"].items():
    print(f"- {name}: {spec['check']} (required={spec['required']})")
print("NOTE: this delivery-pack script validates declaration only; repository implementation must bind real checks.")

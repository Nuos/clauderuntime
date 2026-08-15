#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PY="${PYTHON:-}"
if [ -z "$PY" ]; then
  for cand in python3 python; do
    if command -v "$cand" >/dev/null 2>&1; then PY="$cand"; break; fi
  done
fi
[ -n "$PY" ] || { echo "no python interpreter found" >&2; exit 1; }
"$PY" "$HERE/check_reference_lock.py"
"$PY" "$HERE/check_quarantine_manifest.py"
"$PY" "$HERE/check_architecture_freeze.py"
"$PY" "$HERE/check_delivery_integrity.py"

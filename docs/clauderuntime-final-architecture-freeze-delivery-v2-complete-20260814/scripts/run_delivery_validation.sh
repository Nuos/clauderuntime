#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
python "$HERE/check_reference_lock.py"
python "$HERE/check_quarantine_manifest.py"
python "$HERE/check_architecture_freeze.py"
python "$HERE/check_delivery_integrity.py"

#!/usr/bin/env bash
set -euo pipefail

# Example local build script using PyInstaller
# Requires Python 3 and pyinstaller installed in the environment
# Usage: ./scripts/build_pyinstaller.sh deployment/start_assistant.py

ENTRY=${1:-deployment/start_assistant.py}
OUTDIR=dist-py

python3 -m pip install --upgrade pip
python3 -m pip install pyinstaller

pyinstaller --onefile --distpath "$OUTDIR" "$ENTRY"

echo "Built: $OUTDIR/$(basename "$ENTRY" .py).exe (on Windows) or binary at $OUTDIR/"

#!/usr/bin/env bash
# Clean common Python caches, compiled files and logs
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "Removing __pycache__ directories..."
find . -type d -name '__pycache__' -print0 | xargs -0 -r rm -rf

echo "Removing .pyc and .pyo files..."
find . -type f \( -name '*.pyc' -o -name '*.pyo' \) -print0 | xargs -0 -r rm -f

echo "Removing temporary logs..."
rm -f server_dependency.log scripts/import_report.json

echo "Clean complete."

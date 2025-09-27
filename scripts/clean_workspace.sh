#!/usr/bin/env bash
set -euo pipefail

echo "Cleaning repository workspace: removing common cached dirs and files"

ROOT_DIR="$(dirname "$(readlink -f "$0")")/.."
cd "$ROOT_DIR"

TARGETS=(
  ".venv"
  ".venv_local_for_packaging"
  "venv"
  "node_modules"
  "dist"
  "build"
  "__pycache__"
  ".pytest_cache"
  ".mypy_cache"
  ".cache"
  "tmp"
)

for t in "${TARGETS[@]}"; do
  if [ -e "$t" ]; then
    echo "Removing $t"
    rm -rf "$t"
  fi
done

# Remove pyc files
find . -type f -name "*.pyc" -print -delete || true

echo "Cleaning done. Run 'git status' to review changes."
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

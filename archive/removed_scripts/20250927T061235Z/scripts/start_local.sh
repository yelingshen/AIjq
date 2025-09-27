#!/usr/bin/env bash
# Interactive local starter: venv, dependency checks, optional model backend install, start minimal server
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

function ask_yesno() {
  local prompt="$1"
  while true; do
    read -p "$prompt [y/n]: " yn
    case "$yn" in
      [Yy]*) return 0;;
      [Nn]*) return 1;;
    esac
  done
}

if [ ! -d ".venv" ]; then
  echo "Creating virtualenv .venv..."
  if python3 -m venv .venv 2>/dev/null; then
    echo "Created .venv"
  else
    echo "Failed to create virtualenv. Running system prereq checker..."
    python3 scripts/check_system_prereqs.py || true
    echo "Please install the missing system packages and re-run this script. Exiting."
    exit 1
  fi
fi
echo "Activating virtualenv..."
source .venv/bin/activate

echo "Upgrading pip..."
python -m pip install --upgrade pip

echo "Installing base requirements..."
pip install -r deployment/requirements.base.txt

if ask_yesno "Install model backends (torch, onnxruntime, pygpt4all)? This may be large and take time."; then
  echo "Installing model backends (may take a while)..."
  pip install -r deployment/requirements.model.txt || true
fi

echo "Checking for required tools..."
MISSING=()
for tool in python3 pip; do
  if ! command -v $tool >/dev/null 2>&1; then
    MISSING+=($tool)
  fi
done
if [ ${#MISSING[@]} -gt 0 ]; then
  echo "Missing tools: ${MISSING[*]}. Please install them and re-run." >&2
fi

echo "Start options:"
echo " 1) Start minimal server (background)"
echo " 2) Start full server (foreground)"
echo " 3) Run import-only check"
echo " 4) Exit"
read -p "Choose an option [1-4]: " opt
case "$opt" in
  1)
    echo "Starting minimal server in background (logs -> server_dependency.log)..."
    nohup python3 ai/server_minimal.py > server_dependency.log 2>&1 &
    PID=$!
    echo "Started server (PID=$PID). Use 'tail -f server_dependency.log' to view logs, and 'kill $PID' to stop."
    ;;
  2)
    echo "Starting full server (foreground)..."
    python3 ai/server.py
    ;;
  3)
    echo "Running import-only checks..."
    python3 scripts/verify_imports.py || true
    ;;
  *)
    echo "Exiting."
    ;;
esac

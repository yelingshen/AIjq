#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "This script will optionally install system packages (Debian/Ubuntu), create a venv, install python deps, run import checks and pytest."

# CLI flags (non-interactive mode supported)
ASSUME_YES=0
DO_APT=1
INSTALL_MODELS=0
INSTALL_DEV=0
INSTALL_OLLAMA=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --yes|-y)
      ASSUME_YES=1; shift;;
    --no-apt)
      DO_APT=0; shift;;
    --with-models)
      INSTALL_MODELS=1; shift;;
    --with-ollama)
      INSTALL_OLLAMA=1; shift;;
    --with-dev)
      INSTALL_DEV=1; shift;;
    --help|-h)
      echo "Usage: $0 [--yes] [--no-apt] [--with-models] [--with-dev]"; exit 0;;
    *) echo "Unknown arg: $1"; exit 2;;
  esac
done

ask_yesno(){
  if [ "$ASSUME_YES" -eq 1 ]; then
    return 0
  fi
  while true; do
    read -p "$1 [y/n]: " yn
    case $yn in
      [Yy]*) return 0;;
      [Nn]*) return 1;;
    esac
  done
}

if [ "$DO_APT" -eq 1 ] && ask_yesno "Attempt to install system packages (python3-venv, python3-pip) via apt? (requires sudo)"; then
  if command -v sudo >/dev/null 2>&1; then
    echo "Running: sudo apt update && sudo apt install -y python3-venv python3-pip build-essential"
    sudo apt update
    sudo apt install -y python3-venv python3-pip build-essential
  else
    echo "sudo not available; please install python3-venv and python3-pip manually and re-run." >&2
  fi
fi

if [ ! -d ".venv" ]; then
  echo "Creating virtual environment .venv"
  python3 -m venv .venv
fi
echo "Activating venv"
source .venv/bin/activate

echo "Upgrading pip and installing base requirements"
python -m pip install --upgrade pip
pip install -r deployment/requirements.base.txt

if [ "$INSTALL_MODELS" -eq 1 ] || ask_yesno "Install model backends from deployment/requirements.model.txt? (may be large)"; then
  pip install -r deployment/requirements.model.txt || true
fi

if [ "$INSTALL_DEV" -eq 1 ] || ask_yesno "Install developer tools (pytest, bandit, safety)?"; then
  pip install -r deployment/requirements.dev.txt || true
fi

if [ "$INSTALL_OLLAMA" -eq 1 ] || ask_yesno "Attempt to install optional Ollama python client (if available via pip)?"; then
  pip install ollama || true
fi

echo "Running import-only verifier"
python3 scripts/verify_imports.py || true

echo "Running pytest"
if command -v pytest >/dev/null 2>&1; then
  pytest -q || true
else
  pip install pytest
  pytest -q || true
fi

echo "Setup and tests finished. Check scripts/import_report.json and any pytest output above."

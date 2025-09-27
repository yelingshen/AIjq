#!/usr/bin/env bash
# idempotent start script for deploying Yeling AI with virtualenv + gunicorn
set -euo pipefail

BASE_DIR="/opt/yeling-ai"
VENV_DIR="$BASE_DIR/venv"
REQ_FILE="$BASE_DIR/requirements.txt"

echo "[yeling] ensuring base dir $BASE_DIR exists"
mkdir -p "$BASE_DIR"

if [ ! -d "$VENV_DIR" ]; then
  echo "[yeling] creating virtualenv at $VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi

echo "[yeling] activating venv and installing requirements (if present)"
source "$VENV_DIR/bin/activate"
if [ -f "$REQ_FILE" ]; then
  pip install --upgrade pip
  pip install -r "$REQ_FILE"
fi

echo "[yeling] starting gunicorn (uvicorn workers)"
exec "$VENV_DIR/bin/gunicorn" -k uvicorn.workers.UvicornWorker ai.server_fastapi:app -b 127.0.0.1:5000 --workers 2

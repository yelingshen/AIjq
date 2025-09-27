#!/usr/bin/env bash
set -euo pipefail

WORKERS=${1:-2}
BIND=${2:-127.0.0.1:8000}

if [ -f .venv/bin/activate ]; then
  # shellcheck disable=SC1091
  . .venv/bin/activate
fi

echo "Starting uvicorn with ${WORKERS} workers on ${BIND}"
exec uvicorn ai.server_fastapi:app --host ${BIND%:*} --port ${BIND##*:} --workers ${WORKERS}

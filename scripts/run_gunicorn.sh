#!/usr/bin/env bash
set -euo pipefail
# Simple script to run the Flask minimal app with Gunicorn in production-like mode.
# Usage:
#   ./scripts/run_gunicorn.sh [workers] [bind]
# Example:
#   ./scripts/run_gunicorn.sh 4 127.0.0.1:5000

WORKERS=${1:-4}
BIND=${2:-127.0.0.1:5000}

echo "Starting gunicorn with ${WORKERS} workers, bind=${BIND}"
# Activate venv if present
if [ -f .venv/bin/activate ]; then
  # shellcheck disable=SC1091
  . .venv/bin/activate
fi

# Recommend using the sync workers for blocking I/O with the current Flask app.
exec gunicorn -w "$WORKERS" -b "$BIND" ai.server_minimal:app

# Notes:
# - For higher concurrency and async model backends, consider migrating to FastAPI
#   and using Uvicorn/Gunicorn with uvicorn.workers.UvicornWorker.
# - Example FastAPI + Uvicorn invocation:
#   gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 ai.server_fastapi:app

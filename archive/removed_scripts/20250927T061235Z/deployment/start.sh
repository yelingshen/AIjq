#!/usr/bin/env bash
# Simple launcher for yeling-ai deployment helpers
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON=${PYTHON:-python3}

echo "Using Python: $PYTHON"
echo "Starting assistant..."
exec "$PYTHON" "$ROOT_DIR/deployment/start_assistant.py"

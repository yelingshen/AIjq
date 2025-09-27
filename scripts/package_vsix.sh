#!/usr/bin/env bash
set -euo pipefail

echo "Packaging VS Code extension (VSIX)"

# Check for vsce
if ! command -v vsce >/dev/null 2>&1; then
  echo "vsce not found. To install: npm install -g vsce or use 'npx vsce package'"
fi

EXT_ROOT="./"
OUT="yeling-ai-extension.vsix"

if command -v vsce >/dev/null 2>&1; then
  (cd "$EXT_ROOT" && vsce package --out "$OUT")
  echo "Created $OUT"
else
  echo "Attempting with npx vsce package"
  (cd "$EXT_ROOT" && npx vsce package --out "$OUT")
  echo "Created $OUT (via npx)"
fi

echo "To install locally: code --install-extension $OUT"

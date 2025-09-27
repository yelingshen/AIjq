#!/usr/bin/env bash
set -euo pipefail

if [ -z "${DEPLOY_HOST:-}" ] || [ -z "${DEPLOY_USER:-}" ]; then
  echo "Please set DEPLOY_HOST and DEPLOY_USER environment variables"
  exit 1
fi

TARGET="$DEPLOY_USER@$DEPLOY_HOST"
echo "Deploying to $TARGET"

ssh -o StrictHostKeyChecking=no "$TARGET" 'mkdir -p ~/yeling-ai && cd ~/yeling-ai && git pull origin master || true && docker compose pull || true && docker compose up -d --build'

echo "Deployed."

#!/usr/bin/env bash
# health_check.sh - 简单健康检查（HTTP/DB）
set -euo pipefail

URL="${1:-http://localhost:8000/health}"
TIMEOUT="${2:-5}"

function check_http() {
  if command -v curl >/dev/null 2>&1; then
    http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$URL")
    if [[ "$http_code" == "200" ]]; then
      echo "{\"status\":\"success\",\"code\":200,\"url\":\"$URL\"}"; return 0
    else
      echo "{\"status\":\"fail\",\"code\":$http_code,\"url\":\"$URL\"}"; return 1
    fi
  else
    echo "curl 未安装，无法进行 HTTP 检查"; return 2
  fi
}

check_http

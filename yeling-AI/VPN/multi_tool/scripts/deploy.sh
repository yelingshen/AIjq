#!/usr/bin/env bash
# 简单部署脚本示例（骨架）
# 支持：检查环境、安装依赖、备份、启动服务、健康检查
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "Running environment checks..."
python3 scripts/check_env.py

# optional: pull from git
if [ "$1" = "pull" ] 2>/dev/null; then
  echo "Pulling latest code..."
  git pull --rebase
fi

# backup
BACKUP_DIR="$ROOT_DIR/backup_$(date +%Y%m%d%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r "$ROOT_DIR" "$BACKUP_DIR/.."

echo "Installing Python deps..."
python3 -m pip install -r requirements.txt

# run migrations or DB steps here (placeholder)
# start services (for demo, we just run a simple command)

echo "Starting services..."
# Support a docker-compose mode: `./scripts/deploy.sh docker [--start]`
if [ "$1" = "docker" ] 2>/dev/null; then
  echo "Preparing docker-compose deployment"
  # basic checks
  if ! command -v docker >/dev/null 2>&1; then
    echo "docker not found. Please install docker to use docker mode." >&2
    exit 1
  fi
  if ! command -v docker-compose >/dev/null 2>&1 && ! docker compose version >/dev/null 2>&1; then
    echo "docker-compose not found. Please install docker-compose or use Docker's built-in compose." >&2
    exit 1
  fi

  DEPLOY_DIR="$ROOT_DIR/deploy"
  mkdir -p "$DEPLOY_DIR"
  COMPOSE_FILE="$DEPLOY_DIR/docker-compose.yml"

  cat > "$COMPOSE_FILE" <<'YAML'
version: '3.8'
services:
  multi_tool:
    image: python:3.12-slim
    working_dir: /app
    volumes:
      - ./:/app:ro
    command: bash -c "python3 -m multi_tool.cli --help"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python3", "-c", "print('ok')"]
      interval: 30s
      timeout: 10s
      retries: 3
YAML

  echo "Created example docker-compose at $COMPOSE_FILE"

  # support subcommands: start|stop|status|rollback with optional --apply to actually run
  SUBCMD=${2:-}
  APPLY=false
  if [ "$3" = "--apply" ] 2>/dev/null; then APPLY=true; fi
  case "$SUBCMD" in
    start)
      echo "Docker start requested (apply=$APPLY)"
      if [ "$APPLY" = true ]; then
        if command -v docker-compose >/dev/null 2>&1; then
          docker-compose -f "$COMPOSE_FILE" up -d
        else
          docker compose -f "$COMPOSE_FILE" up -d
        fi
        # record image used for potential rollback (use compose_helper if available)
        LAST_IMAGE_FILE="$DEPLOY_DIR/last_image"
        HISTORY_FILE="$DEPLOY_DIR/history.log"
        img=''
        if command -v python3 >/dev/null 2>&1; then
          img=$(python3 -c "from multi_tool.scripts.compose_helper import get_service_image; print(get_service_image('$COMPOSE_FILE') or '')" 2>/dev/null || true)
        fi
        if [ -z "$img" ]; then
          # fallback to grep-based extraction
          img=$(grep -E '^[[:space:]]*image:' "$COMPOSE_FILE" | head -n1 | awk '{print $2}' || true)
        fi
        if [ -n "$img" ]; then
          echo "$img" > "$LAST_IMAGE_FILE"
          # record history: timestamp|gitrev|image
          gitrev=$(git rev-parse --short HEAD 2>/dev/null || true)
          ts=$(date --iso-8601=seconds)
          echo "$ts|$gitrev|$img" >> "$HISTORY_FILE"
          echo "Recorded deployed image: $img -> $LAST_IMAGE_FILE; history appended to $HISTORY_FILE"
        fi
        echo "Started. Use 'docker compose -f $COMPOSE_FILE ps' to inspect."
      else
        echo "DRY RUN: To start, run: docker compose -f $COMPOSE_FILE up -d --remove-orphans"
      fi
      ;;
    stop)
      echo "Docker stop requested (apply=$APPLY)"
      if [ "$APPLY" = true ]; then
        if command -v docker-compose >/dev/null 2>&1; then
          docker-compose -f "$COMPOSE_FILE" down
        else
          docker compose -f "$COMPOSE_FILE" down
        fi
      else
        echo "DRY RUN: To stop, run: docker compose -f $COMPOSE_FILE down"
      fi
      ;;
    status)
      echo "Docker status (no changes)"
      if command -v docker-compose >/dev/null 2>&1; then
        docker-compose -f "$COMPOSE_FILE" ps || true
      else
        docker compose -f "$COMPOSE_FILE" ps || true
      fi
      ;;
    rollback)
      echo "Docker rollback requested (apply=$APPLY)"
      echo "This is a placeholder: implement image/tag tracking and rollback strategy for your deployment."
      HISTORY_FILE="$DEPLOY_DIR/history.log"
      if [ ! -f "$HISTORY_FILE" ]; then
        echo "No deployment history found ($HISTORY_FILE)"
        exit 1
      fi
      # support optional parameter: rollback <last|id>
      RKEY=${3:-last}
      if [ "$RKEY" = "last" ]; then
        rec=$(tail -n1 "$HISTORY_FILE")
      else
        # find by line number id (1-based)
        rec=$(sed -n "${RKEY}p" "$HISTORY_FILE" || true)
      fi
      if [ -z "$rec" ]; then
        echo "No matching history record for '$RKEY'"
        exit 1
      fi
      last_img=$(echo "$rec" | awk -F'|' '{print $3}')
      echo "Rolling back to image from record: $rec"
      if [ -z "$last_img" ]; then
        echo "Record does not contain image"
        exit 1
      fi
      if [ "$APPLY" = true ]; then
        echo "Pulling $last_img and restarting services"
        docker pull "$last_img" || true
        if command -v docker-compose >/dev/null 2>&1; then
          docker-compose -f "$COMPOSE_FILE" up -d
        else
          docker compose -f "$COMPOSE_FILE" up -d
        fi
      else
        echo "DRY RUN: would pull $last_img and run docker compose -f $COMPOSE_FILE up -d"
      fi
      ;;
    "" )
      echo "To manage services, run: $0 docker <start|stop|status|rollback> [--apply]"
      ;;
    *)
      echo "Unknown docker subcommand: $SUBCMD"
      ;;
  esac
  exit 0
fi

if [ "$1" = "systemd" ] 2>/dev/null; then
  SUB=${2:-}
  DEPLOY_DIR="$ROOT_DIR/deploy"
  mkdir -p "$DEPLOY_DIR"
  UNIT_FILE="$DEPLOY_DIR/multi_tool.service"

  cat > "$UNIT_FILE" <<'UNIT'
[Unit]
Description=multi_tool service (example)
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/multi_tool
ExecStart=/usr/bin/python3 -m multi_tool.cli vpn-router --config /etc/multi_tool/config.yaml
Restart=on-failure
User=multi_tool

[Install]
WantedBy=multi-user.target
UNIT

  case "$SUB" in
    install)
      echo "Generated unit file at $UNIT_FILE"
      echo "To install on target host, copy and enable the service (dry run):"
      echo "  sudo cp $UNIT_FILE /etc/systemd/system/"
      echo "  sudo systemctl daemon-reload"
      echo "  sudo systemctl enable multi_tool.service"
      echo "  sudo systemctl start multi_tool.service"
      ;;
    start)
      echo "Start systemd service (dry run). Use --apply to actually run."
      if [ "$3" = "--apply" ] 2>/dev/null; then
        sudo systemctl start multi_tool.service
      fi
      ;;
    stop)
      echo "Stop systemd service (dry run). Use --apply to actually run."
      if [ "$3" = "--apply" ] 2>/dev/null; then
        sudo systemctl stop multi_tool.service
      fi
      ;;
    status)
      sudo systemctl status multi_tool.service || true
      ;;
    "")
      echo "Usage: $0 systemd <install|start|stop|status> [--apply]"
      ;;
    *)
      echo "Unknown systemd subcommand: $SUB"
      ;;
  esac
  exit 0
fi

# health checks (example)
python3 - <<'PY'
import sys
print('Health check placeholder')
PY

echo "Deployment done. Backup created at $BACKUP_DIR"

#!/usr/bin/env bash
# install_helpers.sh - 部署辅助函数库
set -euo pipefail

# 检测 Python
function detect_python() {
  command -v python3 || command -v python || echo ""
}

# 检测 Node.js
function detect_node() {
  command -v node || echo ""
}

# 检测 Docker
function detect_docker() {
  command -v docker || echo ""
}

# 检测 systemd
function detect_systemd() {
  if command -v systemctl >/dev/null 2>&1; then echo "systemd"; else echo "none"; fi
}

# 解压归档（zip/tar.gz）
function extract_archive() {
  local archive="$1"
  local target="$2"
  if [[ "$archive" == *.zip ]]; then
    unzip -o "$archive" -d "$target"
  elif [[ "$archive" == *.tar.gz ]]; then
    tar -xzf "$archive" -C "$target"
  else
    echo "不支持的归档格式: $archive" >&2; return 1
  fi
}

# 创建 venv 并激活
function create_venv_and_activate() {
  local pybin
  pybin="$(detect_python)"
  local target="$1"
  "$pybin" -m venv "$target/.venv"
  # shellcheck disable=SC1090
  source "$target/.venv/bin/activate"
}

# 安装 requirements
function install_requirements() {
  local req_file="$1"
  if [[ -f "$req_file" ]]; then
    pip install -r "$req_file"
  fi
}

# 自动检测启动脚本
function detect_start_script() {
  local target="$1"
  for c in "$target/deployment/start_server.py" "$target/deployment/start_gunicorn.sh" "$target/ai/server.py" "$target/start_server.py"; do
    if [[ -f "$c" ]]; then echo "$c"; return 0; fi
  done
  return 1
}

# 端口检测（优先 --port，其次脚本内容）
function detect_port_from_files() {
  local script="$1"
  local port=""
  if [[ -f "$script" ]]; then
    port=$(sed -n 's/.*--port[= ]*\([0-9]\{2,5\}\).*/\1/p' "$script" | head -n1)
    if [[ -z "$port" ]]; then
      port=$(sed -n 's/.*PORT=\([0-9]\{2,5\}\).*/\1/p' "$script" | head -n1)
    fi
    if [[ -z "$port" ]]; then
      port=$(sed -n 's/.*:\([0-9]\{2,5\}\).*/\1/p' "$script" | head -n1)
    fi
  fi
  echo "$port"
}

# 统一日志输出
function log_and_fail() {
  echo "[ERROR] $*" >&2
  exit 1
}

# 备份当前目录
function backup_current_release() {
  local target="$1"
  local backup_dir
  backup_dir="$target/_backup_$(date +%Y%m%dT%H%M%S)"
  mkdir -p "$backup_dir"
  cp -a "$target"/* "$backup_dir"/
  echo "$backup_dir"
}

# 快照文件（用于回滚）
function snapshot_files_for_rollback() {
  local target="$1"
  local snap_dir
  snap_dir="$target/_snapshot_$(date +%Y%m%dT%H%M%S)"
  mkdir -p "$snap_dir"
  cp -a "$target"/* "$snap_dir"/
  echo "$snap_dir"
}

# systemd 单元写入（模板替换）
function write_systemd_unit_from_template() {
  local template="$1"
  local output="$2"
  local target="$3"
  local venv="$4"
  local start_cmd="$5"
  local port="$6"
  sed -e "s|\${TARGET}|$target|g" \
      -e "s|\${VENV}|$venv|g" \
      -e "s|\${START_COMMAND}|$start_cmd|g" \
      -e "s|\${PORT}|$port|g" "$template" > "$output"
}

# 导出所有函数
export -f detect_python detect_node detect_docker detect_systemd extract_archive create_venv_and_activate install_requirements detect_start_script detect_port_from_files log_and_fail backup_current_release snapshot_files_for_rollback write_systemd_unit_from_template

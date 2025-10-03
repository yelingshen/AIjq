#!/usr/bin/env bash
set -euo pipefail

# yeling-ai 安装脚本（增强兼容性）
# 用法: sudo ./install_package.sh [--target /opt/yeling-ai] [--enable-service] [--start-script PATH] [--port 8000] [--dry-run]

show_help() {
  cat <<EOF
yeling-ai 安装脚本

用法:
  sudo ./install_package.sh [--target /opt/yeling-ai] [--enable-service] [--start-script PATH] [--port 8000] [--dry-run]

选项:
  --target DIR         目标安装目录（默认 /opt/yeling-ai）
  --enable-service     在安装结束后创建并启用 systemd 服务（会提示确认）
  --start-script PATH  指定启动脚本路径（相对于目标目录或绝对），如果省略脚本将自动检测常见候选项
  --port PORT          指定服务监听端口（用于写入 systemd Environment）
  --dry-run            仅显示将要执行的操作，不做真实修改
  -h, --help           显示此帮助并退出

脚本做的事:
  - 支持解压 final_package.zip 或 final_package.tar.gz 到目标目录
  - 创建 Python venv: TARGET/.venv
  - 安装 deployment/requirements.txt（如果存在）
  - 自动检测或使用指定的启动脚本（deployment/start_server.py, deployment/start_gunicorn.sh, ai/server.py 等）
  - 可选：创建 systemd 单元并启用（写入 PATH、PORT 环境变量）
EOF
}

TARGET_DIR="/opt/yeling-ai"
SERVICE_ACTION="no"
START_SCRIPT=""
FORCE_PORT=""
DRY_RUN=0

while [[ ${#} -gt 0 ]]; do
  case "$1" in
    --target)
      TARGET_DIR="$2"; shift 2;;
    --enable-service)
      SERVICE_ACTION="enable"; shift;;
    --start-script)
      START_SCRIPT="$2"; shift 2;;
    --port)
      FORCE_PORT="$2"; shift 2;;
    --dry-run)
      DRY_RUN=1; shift;;
    -h|--help)
      show_help; exit 0;;
    --)
      shift; break;;
    *)
      # 如果是单个参数且看起来像路径，则当作 target
      if [[ -z "$TARGET_DIR" || "$TARGET_DIR" == "/opt/yeling-ai" && ! "$1" =~ -- ]]; then
        TARGET_DIR="$1"; shift
      else
        echo "未知参数: $1" >&2; show_help; exit 1
      fi
      ;;
  esac
done

echo "目标目录: $TARGET_DIR"
echo "dry-run: $DRY_RUN"
if [[ $DRY_RUN -eq 0 ]]; then
  mkdir -p "$TARGET_DIR"
else
  echo "DRY RUN: 不会创建目录或写入文件"
fi

# 归档支持：zip 或 tar.gz
ARCHIVE_ZIP="final_package.zip"
ARCHIVE_TAR="final_package.tar.gz"
if [[ -f "$ARCHIVE_ZIP" ]]; then
  ARCHIVE_TYPE="zip"
elif [[ -f "$ARCHIVE_TAR" ]]; then
  ARCHIVE_TYPE="tar"
else
  echo "错误: 未找到 final_package.zip 或 final_package.tar.gz（请把安装包与本脚本放在同一目录）" >&2
  exit 1
fi

echo "检测到安装包类型: ${ARCHIVE_TYPE}"
if [[ $DRY_RUN -eq 0 ]]; then
  if [[ "$ARCHIVE_TYPE" == "zip" ]]; then
    echo "正在解压 $ARCHIVE_ZIP 到 $TARGET_DIR ..."
    unzip -o "$ARCHIVE_ZIP" -d "$TARGET_DIR"
  else
    echo "正在解压 $ARCHIVE_TAR 到 $TARGET_DIR ..."
    tar -xzf "$ARCHIVE_TAR" -C "$TARGET_DIR"
  fi
fi

# Python venv
PYTHON_BIN=$(command -v python3 || true)
if [[ -z "$PYTHON_BIN" ]]; then
  echo "错误: 找不到 python3，请在目标机器上先安装 Python 3.10+" >&2
  exit 1
fi

echo "使用 Python: $PYTHON_BIN"
if [[ $DRY_RUN -eq 0 ]]; then
  echo "创建虚拟环境..."
  $PYTHON_BIN -m venv "$TARGET_DIR/.venv"
  # shellcheck disable=SC1090
  source "$TARGET_DIR/.venv/bin/activate"

  # pip 升级
  pip install --upgrade pip setuptools wheel || true
fi

# 安装 requirements（优先 deployment/requirements.txt）
REQ_FILE="$TARGET_DIR/deployment/requirements.txt"
if [[ -f "$REQ_FILE" ]]; then
  echo "检测到 requirements 文件: $REQ_FILE"
  if [[ $DRY_RUN -eq 0 ]]; then
    pip install -r "$REQ_FILE"
  else
    echo "DRY RUN: 将执行 pip install -r $REQ_FILE"
  fi
else
  echo "未检测到 deployment/requirements.txt，跳过 Python 依赖安装。"
fi

# 提示关于 VS Code extension 的构建
if command -v npm >/dev/null 2>&1; then
  echo "\n检测到 npm，若需构建 VSIX，请在目标目录执行（可选）："
  echo "  cd $TARGET_DIR/src && npm ci && npm run compile && npx vsce package"
else
  echo "\n未检测到 npm：若需构建 VSIX，请在能访问网络并安装 Node.js 的机器上运行上述命令。"
fi

# 自动检测启动脚本候选
detect_start_script() {
  candidates=(
    "$TARGET_DIR/deployment/start_server.py"
    "$TARGET_DIR/deployment/start_gunicorn.sh"
    "$TARGET_DIR/deployment/start_gunicorn.py"
    "$TARGET_DIR/ai/server.py"
    "$TARGET_DIR/start_server.py"
  )
  for c in "${candidates[@]}"; do
    if [[ -f "$c" ]]; then
      echo "$c"
      return 0
    fi
  done
  return 1
}

if [[ -n "$START_SCRIPT" ]]; then
  # 支持相对路径
  if [[ ! "$START_SCRIPT" =~ ^/ ]]; then
    START_SCRIPT="$TARGET_DIR/$START_SCRIPT"
  fi
  echo "使用用户指定的启动脚本: $START_SCRIPT"
else
  echo "自动检测启动脚本..."
  START_SCRIPT=$(detect_start_script || true)
  if [[ -n "$START_SCRIPT" ]]; then
    echo "检测到启动脚本: $START_SCRIPT"
  else
    echo "未检测到已知的启动脚本。若需 systemd 支持，请使用 --start-script 指定启动脚本。"
  fi
fi

# 端口处理
if [[ -n "$FORCE_PORT" ]]; then
  PORT="$FORCE_PORT"
  echo "使用用户指定端口: $PORT"
else
  # 尝试从常见启动脚本中解析端口（仅简单解析）
  PORT=""
  if [[ -n "$START_SCRIPT" && -f "$START_SCRIPT" ]]; then
  # 查找数字形式的 --port 或 PORT= 或 ":<port>" 形式（兼容不同 grep）
  # 使用 sed 进行兼容性更好的提取：优先 --port，其次 PORT=，最后 :<port>
  port_match=$( (sed -n 's/.*--port[= ]*\([0-9]\{2,5\}\).*/\1/p' "$START_SCRIPT" 2>/dev/null || true; \
          sed -n 's/.*PORT=\([0-9]\{2,5\}\).*/\1/p' "$START_SCRIPT" 2>/dev/null || true; \
          sed -n 's/.*:\([0-9]\{2,5\}\).*/\1/p' "$START_SCRIPT" 2>/dev/null || true) | head -n1 || true)
  PORT="$port_match"
    if [[ -n "$PORT" ]]; then
      echo "从 $START_SCRIPT 中解析到端口: $PORT"
    fi
  fi
fi

# 可选: 创建 systemd 服务单元
if [[ "$SERVICE_ACTION" == "enable" ]]; then
  if [[ -z "$START_SCRIPT" ]]; then
    echo "错误: 要启用 systemd 服务，需要提供或自动检测到启动脚本。使用 --start-script 指定。" >&2
    exit 1
  fi

  if [[ $DRY_RUN -eq 1 ]]; then
    echo "DRY RUN: 将创建 systemd 单元（不写入系统）"
  else
    if [[ $(id -u) -ne 0 ]]; then
      echo "警告: 启用 systemd 服务通常需要 root 权限。尝试继续..."
    fi
    read -r -p "是否现在为 yeling-ai 创建并启用 systemd 服务？(y/n) " yn
    if [[ "$yn" =~ ^[Yy]$ ]]; then
      SERVICE_FILE="/etc/systemd/system/yeling-ai.service"
      echo "正在创建 $SERVICE_FILE ..."
      cat > "$SERVICE_FILE" <<EOL
[Unit]
Description=Yeling AI Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$TARGET_DIR
Environment=PATH=$TARGET_DIR/.venv/bin
EOL
      if [[ -n "$PORT" ]]; then
        echo "Environment=PORT=$PORT" >> "$SERVICE_FILE"
      fi
      # ExecStart 判断
      if [[ "$START_SCRIPT" == *.py ]]; then
        echo "ExecStart=$TARGET_DIR/.venv/bin/python3 $START_SCRIPT" >> "$SERVICE_FILE"
      else
        echo "ExecStart=$START_SCRIPT" >> "$SERVICE_FILE"
      fi
      cat >> "$SERVICE_FILE" <<EOL
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOL
      systemctl daemon-reload
      systemctl enable --now yeling-ai.service || echo "警告: 启动 systemd 服务失败，请检查日志或手动运行 systemctl";
      echo "systemd 服务已创建：$SERVICE_FILE"
    else
      echo "跳过创建 systemd 服务。"
    fi
  fi
fi

# 引入辅助脚本
source "$(dirname "$0")/install_helpers.sh"

# 检查依赖
if [[ $DRY_RUN -eq 0 ]]; then
  echo "检查系统依赖..."
  detect_python || { echo "Python 3.10+ 未安装，退出。"; exit 1; }
  detect_node || echo "警告: Node.js 未安装，某些功能可能不可用。"
  detect_docker || echo "警告: Docker 未安装，某些功能可能不可用。"
  detect_systemd || echo "警告: systemd 未检测到，无法启用服务。"
fi

# 健康检查
if [[ $DRY_RUN -eq 0 ]]; then
  echo "运行健康检查..."
  bash "$(dirname "$0")/health_check.sh" "http://localhost:${PORT:-8000}" || echo "警告: 健康检查失败。请检查服务是否正常运行。"
fi

# 生成安装完成日志
INSTALL_LOG="$TARGET_DIR/install_done.txt"
if [[ $DRY_RUN -eq 0 ]]; then
  cat > "$INSTALL_LOG" <<EOF
安装完成: $(date -Iseconds)
目标目录: $TARGET_DIR
虚拟环境: $TARGET_DIR/.venv
启动脚本: ${START_SCRIPT:-未指定}
端口: ${PORT:-未检测}
如需构建 VSIX，请参考上方说明（需要 npm/node）。
EOF
  echo "安装完成。详情见: $INSTALL_LOG"
else
  echo "DRY RUN: 安装不会写入 $INSTALL_LOG"
fi

echo "校验提示：如果你带走了安装包，请保留 scripts/checksums_SHA256.txt 用于后续校验。"

exit 0

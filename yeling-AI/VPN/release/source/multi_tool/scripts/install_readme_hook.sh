#!/usr/bin/env bash
# 简单脚本：在项目的 .git/hooks 中安装 pre-commit 钩子，触发 readme_manager.py 在提交前更新 README
set -e
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
HOOKS_DIR="$ROOT_DIR/.git/hooks"
if [ ! -d "$HOOKS_DIR" ]; then
  echo "此项目似乎不是一个 git 仓库：$HOOKS_DIR 不存在"
  exit 1
fi

HOOK_FILE="$HOOKS_DIR/pre-commit"
cat > "$HOOK_FILE" <<'HOOK'
#!/usr/bin/env bash
# 自动在 pre-commit 阶段更新 README 的自动生成部分
python3 -m multi_tool.readme_manager --update || true
HOOK
chmod +x "$HOOK_FILE"
echo "Installed pre-commit hook to $HOOK_FILE"

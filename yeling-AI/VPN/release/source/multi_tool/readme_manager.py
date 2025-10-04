"""README 管理器：自动生成/更新 README 的功能与变更记录

提供：
- generate_summary(): 基于代码检查生成功能、依赖和手动操作草稿
- append_changelog(msg): 将变更记录追加到 README 的 Changelog 段
- update_readme(): 将生成的摘要合并到 README（覆盖或插入相应区域）

设计原则：尽量不覆盖手写内容，只替换标记区域。
"""
import os
import re
import yaml
import datetime
from datetime import timezone
from pathlib import Path

ROOT = Path(__file__).parent
README_PATH = ROOT / 'README.md'

# Markers used inside README for generated sections
SUMMARY_START = '<!-- AUTO-GENERATED-SUMMARY:START -->'
SUMMARY_END = '<!-- AUTO-GENERATED-SUMMARY:END -->'
CHANGELOG_START = '<!-- AUTO-GENERATED-CHANGELOG:START -->'
CHANGELOG_END = '<!-- AUTO-GENERATED-CHANGELOG:END -->'


def _gather_basic_info():
    info = {}
    # dependencies from requirements.txt
    req = ROOT / 'requirements.txt'
    if req.exists():
        info['dependencies'] = [ln.strip() for ln in req.read_text().splitlines() if ln.strip()]
    else:
        info['dependencies'] = []

    # list entrypoints and commands (scan cli.py)
    cli_file = ROOT / 'cli.py'
    commands = []
    if cli_file.exists():
        txt = cli_file.read_text()
        # crude parse for subparser names
        for m in re.finditer(r"add_parser\('([a-zA-Z0-9-]+)'", txt):
            commands.append(m.group(1))
    info['commands'] = sorted(set(commands))

    # detect presence of key modules
    info['has_file_helper'] = (ROOT / 'file_helper').exists()
    info['has_vpn_router'] = (ROOT / 'vpn_router').exists()
    return info


def generate_summary():
    info = _gather_basic_info()
    lines = []
    lines.append('## 自动生成的项目摘要')
    lines.append('')
    lines.append('### 主要功能')
    if info['has_file_helper']:
        lines.append('- 文件助手：选择可执行文件并启动本地报告/运行服务（基于 Flask 的局部 Web UI）')
    if info['has_vpn_router']:
        lines.append('- VPN 路由器：VPN 连接管理、端口转发、虚拟设备管理工具')
    lines.append('')
    lines.append('### 命令行接口')
    if info['commands']:
        lines.append('- 可用子命令: ' + ', '.join(info['commands']))
    else:
        lines.append('- 无 CLI 子命令信息')
    lines.append('')
    lines.append('### 依赖')
    if info['dependencies']:
        for d in info['dependencies']:
            lines.append(f'- {d}')
    else:
        lines.append('- 依赖信息未检测到（请参考 requirements.txt）')
    lines.append('')
    lines.append('### 需要手动操作的部分')
    lines.append('- 生成/安装 license 文件（开发或测试时执行: `multi_tool license generate`）')
    lines.append('- 在 Linux 上某些操作需要 sudo，例如更新软件或启用内核模块')
    lines.append('- GUI 组件需要图形环境，headless 环境中只能使用 CLI 或 license 管理')
    lines.append('')
    return '\n'.join(lines)


def append_changelog(entry, author=None):
    now = datetime.datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    author = author or os.environ.get('USER') or 'unknown'
    header = f'- {now} by {author}: {entry}'

    readme = README_PATH.read_text() if README_PATH.exists() else ''
    if CHANGELOG_START in readme and CHANGELOG_END in readme:
        new = re.sub(rf"{re.escape(CHANGELOG_START)}[\s\S]*?{re.escape(CHANGELOG_END)}",
                     f"{CHANGELOG_START}\n{header}\n{CHANGELOG_END}",
                     readme)
    else:
        # append a changelog section at end
        new = readme + '\n\n' + CHANGELOG_START + '\n' + header + '\n' + CHANGELOG_END

    README_PATH.write_text(new)
    return header


def update_readme():
    summary = generate_summary()
    readme = README_PATH.read_text() if README_PATH.exists() else ''
    if SUMMARY_START in readme and SUMMARY_END in readme:
        new = re.sub(rf"{re.escape(SUMMARY_START)}[\s\S]*?{re.escape(SUMMARY_END)}",
                     f"{SUMMARY_START}\n{summary}\n{SUMMARY_END}",
                     readme)
    else:
        # insert summary at top
        new = summary + '\n\n' + SUMMARY_START + '\n' + summary + '\n' + SUMMARY_END + '\n\n' + readme
    README_PATH.write_text(new)
    return True


if __name__ == '__main__':
    # easy CLI for readme manager
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--update', action='store_true')
    p.add_argument('--changelog', help='追加一条变更记录')
    args = p.parse_args()
    if args.changelog:
        h = append_changelog(args.changelog)
        print('Appended changelog:', h)
    if args.update:
        update_readme()
        print('README updated')

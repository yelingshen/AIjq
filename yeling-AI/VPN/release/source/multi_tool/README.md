# multi_tool

[![CI](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/OWNER/REPO/actions/workflows/ci.yml)

Replace OWNER/REPO with your GitHub organization/user and repository name to enable the badge.

这是将两个项目合并后的多功能工具包，包含两大子模块：

- `file_helper`：桌面 GUI + 本地小型 HTTP 报告，用于分析单个文件并按需安装依赖后运行。来源于 `系统修复`。
- `vpn_router`：VPN 连接与本地端口转发管理，来源于 `vpn-router`。

## 快速开始

1. 安装系统依赖（Ubuntu/Debian）：

```bash
sudo apt update
sudo apt install -y python3 python3-tk net-tools netcat
```

2. 安装 Python 依赖：

```bash
python3 -m pip install -r requirements.txt
```

3. 运行子模块：

运行文件助手 GUI（图形环境）：

```bash
python3 -m multi_tool.cli file-helper
```

运行 VPN 路由器（使用示例配置 `config.yaml`）：

```bash
python3 -m multi_tool.cli vpn-router --config config.yaml
```

## 自动生成的项目摘要（由工具维护）

<!-- AUTO-GENERATED-SUMMARY:START -->
## 自动生成的项目摘要

### 主要功能
- 文件助手：选择可执行文件并启动本地报告/运行服务（基于 Flask 的局部 Web UI）
- VPN 路由器：VPN 连接管理、端口转发、虚拟设备管理工具

### 命令行接口
- 可用子命令: action, file-helper, license, list, menu, run, vpn-router

### 依赖
- flask
- requests
- pyyaml
- netifaces

### 需要手动操作的部分
- 生成/安装 license 文件（开发或测试时执行: `multi_tool license generate`）
- 在 Linux 上某些操作需要 sudo，例如更新软件或启用内核模块
- GUI 组件需要图形环境，headless 环境中只能使用 CLI 或 license 管理

<!-- AUTO-GENERATED-SUMMARY:END -->

## 变更记录（自动追加）

<!-- AUTO-GENERATED-CHANGELOG:START -->
- 2025-10-02T11:33:23+00:00 by xiedaima: 修复时间格式为 timezone-aware
<!-- AUTO-GENERATED-CHANGELOG:END -->

## 手动操作与注意事项

- 生成/安装 license 文件（开发或测试时执行: `multi_tool license generate`）
- 在 Linux 上某些操作需要 sudo，例如更新软件或启用内核模块
- GUI 组件需要图形环境，headless 环境下使用 CLI 或 license 管理

### Headless（无图形环境）使用

- 在没有 X11/Wayland 的服务器上，你仍然可以使用 CLI 子命令管理许可与 VPN：

```bash
python3 -m multi_tool.cli license generate
python3 -m multi_tool.cli menu vpn-router --config config.yaml
```

- 注意：`menu vpn-router` 会尝试打开一个简单的 tkinter 窗口；在纯 headless 环境中请直接使用 `vpn-router` 子命令并通过日志/控制台观察状态。

### 虚拟设备管理（示例）

- 虚拟设备的操作可通过 VPN 菜单中的“虚拟设备管理”按钮触发（GUI）。如果你希望在脚本中自动化这些操作，可以直接在 Python 中调用相应函数：

```python
from multi_tool.vpn_router.vpn import ip_detector as ipd
ipd.enable_virtual_device()
ipd.update_software()
ipd.restore_dns()
```

这些调用可能需要 sudo 权限（取决于命令实现）。

### 授权文件位置与格式

- 默认授权文件路径： `~/.multi_tool_license`
- 内容为单行授权密钥（当前示例逻辑接受 `VALID_LICENSE_KEY` 作为有效密钥）。
- 生产环境请替换 `vpn_router/utils/shell_utils.py` 中的验证逻辑为更安全的校验（例如在线校验、签名或哈希比对）。

### 在 CI 中使用 README 自动更新

- 在 CI（如 GitHub Actions）中，你可以在 workflow 中添加一步，在推送/合并前运行：

```yaml
- name: Update README
  run: python3 -m multi_tool.readme_manager --update
```

该步骤会更新项目的自动生成摘要；如果你希望将更改提交回仓库，需要在 CI 中配置凭据并新增提交步骤（示例略）。

## 自动化 README 更新

项目包含 `multi_tool/readme_manager.py`：

- 更新自动生成摘要：
  - `python3 -m multi_tool.readme_manager --update`
- 追加变更记录：
  - `python3 -m multi_tool.readme_manager --changelog "描述内容"`

示例：安装 git pre-commit 钩子以在每次提交前自动更新 README：

```bash
bash scripts/install_readme_hook.sh
```

钩子脚本会在 `.git/hooks/pre-commit` 中安装一个简单脚本，触发 `multi_tool.readme_manager --update`（失败不阻挡提交）。

## 其它说明

- 若要查看 CLI 可用子命令和帮助：

```bash
python3 -m multi_tool.cli --help
```

- 许可管理示例：

```bash
python3 -m multi_tool.cli license generate
python3 -m multi_tool.cli license check
```

## 动作（Actions）API

项目现在有统一的动作注册机制，使用装饰器或兼容的 `register` 函数进行注册。支持权限（`admin_only`）、`dry-run` 与参数传递。示例：

```python
from multi_tool.actions import action

@action('vdev.enable', description='启用虚拟设备', admin_only=True, supports_dry_run=False)
def enable_virtual_device(dry_run=False, params=None):
    if dry_run:
        print('[Dry-Run] 启用虚拟设备')
        return
    # 实际执行逻辑
```

CLI 支持：

```bash
python3 -m multi_tool.cli action list
python3 -m multi_tool.cli action run vdev.enable --dry-run
python3 -m multi_tool.cli action run vpn.connect --param config=custom.yaml
```

管理员权限说明：如果动作声明为 `admin_only=True`，CLI 在执行时会校验权限（POSIX 下检查 `euid==0`，Windows 下可使用环境变量 `MULTI_TOOL_IS_ADMIN=1` 来模拟）。

## 测试

项目包含基础单元测试（位于 `tests/`），测试使用 `unittest.mock` 模拟系统调用，避免修改真实系统状态：

```bash
PYTHONPATH=. python3 -m unittest discover -s tests -p 'test_*.py'
```

## 部署与环境检查

新增脚本：

- `scripts/check_env.py`：跨平台基础依赖检测（Python、pip、git、可选 docker/node）
- `scripts/deploy.sh`：示例部署脚本（检查环境、备份、安装依赖、健康检查骨架）

运行示例：

```bash
bash scripts/deploy.sh pull
```

脚本为骨架，建议根据实际服务替换启动/停止/回滚逻辑（例如 systemd 服务、docker-compose 或 Kubernetes）。

### deploy.sh 使用说明（增强版）

脚本现在支持更细粒度的子命令：

- Docker 模式（生成示例 `deploy/docker-compose.yml` 并支持管理命令）：

```bash
# 生成示例 compose 文件
bash multi_tool/scripts/deploy.sh docker

# 启动（dry-run）
bash multi_tool/scripts/deploy.sh docker start

# 启动并实际执行
bash multi_tool/scripts/deploy.sh docker start --apply

# 停止
bash multi_tool/scripts/deploy.sh docker stop --apply

# 查看状态
bash multi_tool/scripts/deploy.sh docker status

# 回滚（占位，需实现回滚策略）
bash multi_tool/scripts/deploy.sh docker rollback
```

- systemd 模式（生成示例 unit 文件并提供安装/管理说明）：

```bash
# 生成 systemd unit 文件示例
bash multi_tool/scripts/deploy.sh systemd

# 生成并显示安装说明
bash multi_tool/scripts/deploy.sh systemd install

# 启动服务（需 --apply 来实际运行）
bash multi_tool/scripts/deploy.sh systemd start --apply
```

注意：脚本默认行为为 dry-run，除非通过 `--apply`（docker: third arg or systemd: third arg）传入明确执行标志。


## CI 与 部署（新增说明）

- 项目包含一个示例 GitHub Actions workflow (`.github/workflows/ci.yml`)，在 push/PR 到 `main` 时会运行：
  - 依赖安装（推荐使用 `requirements-pin.txt`）
  - 运行单元测试
  - 运行可选 lint（ruff）
  - 非阻塞地更新 README（`multi_tool.readme_manager --update`）

- 若需在 CI 中自动提交 README 更新，需要在 workflow 中配置合适的凭据（例如 `GITHUB_TOKEN` 或 PAT），并在 workflow 中启用提交步骤（示例在 workflow 文件内注释）。

### pre-commit（本地自动格式化）

建议在本地启用 pre-commit 来在提交前自动格式化代码：

```bash
python3 -m pip install -r requirements-dev.txt
pre-commit install
pre-commit run --all-files
```

在 CI 中我们也运行 ruff format + ruff check 来保证风格一致。

### 部署历史与回滚

部署脚本现在在每次使用 `docker start --apply` 成功部署后，会记录一条历史到 `deploy/history.log`，格式为：

```
timestamp|gitrev|image
```

回滚到上一次部署：

```bash
# dry-run
bash multi_tool/scripts/deploy.sh docker rollback

# 实际执行回滚（拉取记录的 image 并重启）
bash multi_tool/scripts/deploy.sh docker rollback --apply
```

回滚到特定历史记录（按行号，1-based）：

```bash
bash multi_tool/scripts/deploy.sh docker rollback 3 --apply
```

注意：当前实现使用 `multi_tool` 服务在 `deploy/docker-compose.yml` 中指定的 `image:` 字段；复杂场景（多服务、变量替换）建议改用更稳健的解析或在部署时显式传入 IMAGE/TAG。


## Requirements（依赖与版本）

- 为降低依赖漂移风险，仓库提供了 `requirements-pin.txt`（推荐用于 CI/生产）以及 `requirements-dev.txt`（包含开发或 CI 工具，如 `pytest` 和 `ruff`）。

示例安装：

```bash
# 使用 pin 文件（推荐）
python3 -m pip install -r requirements-pin.txt

# 开发依赖
python3 -m pip install -r requirements-dev.txt
```

注意：在某些由发行版管理的 Python 环境中（例如 Debian/Ubuntu 的 system Python），直接通过 pip 全局安装可能受限，推荐使用虚拟环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements-pin.txt
```


Yeling-AI — 项目使用与操作说明
=================================

本文档覆盖从开发、测试、构建到部署的所有常用操作步骤，按模块（Python 后端 与 VS Code 扩展）分组。

先决条件
---------

- 已安装 Python 3.10+（最好 3.11/3.12）
- 已安装 Node.js 18+ 与 npm
- 可选：Docker、systemd（Linux）、vsce（用于本地打包：`npm i -g vsce`）

仓库结构概览
----------------
- `ai/`：后端助手核心 Python 代码
- `deployment/`：部署脚本与 systemd 单元文件
- `scripts/`：维护脚本（清理、去重、合并辅助）
Yeling-AI — 项目使用与操作说明
=================================

本文档覆盖从开发、测试、构建到部署的所有常用操作步骤，按模块（Python 后端 与 VS Code 扩展）分组。

先决条件
---------

- 已安装 Python 3.10+（最好 3.11/3.12）。

- 已安装 Node.js 18+ 与 npm。

- 可选：Docker、systemd（Linux）、vsce（用于本地打包，建议使用 npx 或全局安装：`npm i -g vsce`）。

仓库结构概览
----------------

- `ai/`：后端助手核心 Python 代码。

- `deployment/`：部署脚本与 systemd 单元文件。

- `scripts/`：维护脚本（清理、去重、合并辅助）。

- `src/`：VS Code 扩展 TypeScript 源码。

- `out/`：TypeScript 编译产物（被 .gitignore 忽略）。

- `archive/`：自动归档的重复或已移动文件。

快速开始（开发环境）
----------------------

1. 克隆仓库并进入目录：

   git clone REPO_URL

   cd yeling-AI

2. Python 环境：

   python3 -m venv .venv

   source .venv/bin/activate

   pip install -r deployment/requirements.txt

3. Node 环境（构建 VS Code 扩展）：

   npm ci

   npm run compile   (会将 TypeScript 编译到 out/)

4. 打包 VSIX：

   使用 npx 或全局 vsce：

   npx vsce package

5. 运行后端（快速本地）：

   运行 minimal server：

   python3 deployment/start_minimal.py

部署（生产示例）
---------------

1. 将代码放到服务器目录（例如 /opt/yeling-ai），创建 venv 并安装依赖：

   python3 -m venv /opt/yeling-ai/venv

   source /opt/yeling-ai/venv/bin/activate

   pip install -r deployment/requirements.txt

2. 拷贝 systemd 单元并启用：

   sudo cp deployment/gunicorn.service /etc/systemd/system/yeling-ai.service

   sudo systemctl daemon-reload

   sudo systemctl enable --now yeling-ai.service

容器化（Docker）
-----------------

- 使用提供的 `Dockerfile` 和 `docker-compose.yml`（如果需要自定义端口或环境变量，请修改对应文件）。

CI（GitHub Actions）
--------------------

- 工作流位于 `.github/workflows/`。若需要在 CI 中运行 lints/tests，请在 workflow 中确保安装 `python`, `pip`, `node`, `npm`，并运行 `pip install -r deployment/requirements.txt`、`npm ci`、`npm run compile`、`pytest` 等步骤。

常见问题与排查
----------------

- 打包 VSIX 报错找不到 tsconfig.json：恢复仓库根的 `tsconfig.json`，然后运行 `npm run compile`。

- pytest 报错与 `archive/` 冲突：在运行测试时忽略 `archive/` 目录（`pytest --ignore=archive`）。

- 远端 push 失败（Repository not found）：检查 git remote，确认远端仓库是否存在且你有写权限。

变更与清理策略
-----------------

- 我们的清理脚本会把重复或被移除的文件移动到 `archive/` 而不是直接删除，以便回滚。

- 若需彻底从历史中移除大文件，请使用 `git-filter-repo`（这会重写历史并需要团队协作）。

最后说明
---------

- 我已在仓库根执行并修复一系列问题：恢复 `package.json`、`tsconfig.json`，构建并打包了扩展（本地），并生成若干扫描/构建报告（存放在 `scripts/`）。

- 部分操作（如 git push）失败是因为远端访问问题，需要你检查远端仓库权限或 URL。

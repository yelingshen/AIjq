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
- Yeling-AI — 项目使用与操作说明
=================================

本文档简要说明常用的开发、构建与部署步骤，分为开发环境、部署与常见排查。

先决条件
---------

- 已安装 Python 3.10+（推荐 3.11/3.12）。

- 已安装 Node.js 18+ 与 npm。

- 可选：Docker、systemd（Linux）、vsce（用于本地打包，建议使用 npx）。

仓库结构概览
----------------

- `ai/`：后端助手核心 Python 代码。

- `deployment/`：部署脚本与 systemd 单元文件。

- `scripts/`：维护脚本（清理、去重、合并辅助）。

- `src/`：VS Code 扩展 TypeScript 源码。

- `out/`：TypeScript 编译产物（通常被 .gitignore 忽略）。

- `archive/`：自动归档的重复或被移除的历史文件。

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

   npm run compile

   （TypeScript 会被编译到 out/）

4. 打包 VSIX：

   使用 npx 或全局 vsce：

   npx vsce package

5. 运行后端（快速本地）：

   python3 deployment/start_minimal.py

部署（生产示例）
---------------

1. 将代码放到服务器目录（例如 /opt/yeling-ai），创建虚拟环境并安装依赖：

   python3 -m venv /opt/yeling-ai/venv

   source /opt/yeling-ai/venv/bin/activate

   pip install -r deployment/requirements.txt

2. 拷贝 systemd 单元并启用：

   sudo cp deployment/gunicorn.service /etc/systemd/system/yeling-ai.service

   sudo systemctl daemon-reload

   sudo systemctl enable --now yeling-ai.service

容器化（Docker）
-----------------

- 使用仓库中的 `Dockerfile` 和 `docker-compose.yml`。如需自定义端口或环境变量，修改对应文件。

CI（GitHub Actions）
--------------------

- 工作流位于 `.github/workflows/`。在 CI 中运行 lint 和测试的典型步骤：

  - 安装运行时：`python`, `pip`, `node`, `npm`

  - 安装 Python 依赖：`pip install -r deployment/requirements.txt`

  - 安装 Node 依赖并编译：`npm ci && npm run compile`

  - 运行测试：`pytest`（可在运行时忽略 `archive/`）

常见问题与排查
----------------

- 找不到 tsconfig.json：将仓库根的 `tsconfig.json` 恢复后运行 `npm run compile`。

- pytest 导致导入错误：测试可能会与 `archive/` 中的历史文件冲突。可使用 `pytest --ignore=archive` 运行当前测试集合。

- git push 报错 "Repository not found"：检查仓库 remote URL 与写权限，或使用正确的凭证登录。

变更与清理策略
-----------------

- 清理脚本会把重复或移除的文件移动到 `archive/`，以便必要时回滚。

- 若需彻底从历史中移除大文件，请使用 `git-filter-repo` 或类似工具；注意这会重写历史并需要团队协调。

最后说明
---------

- 在仓库根已修复并恢复部分关键文件（如 `package.json`、`tsconfig.json`），并在本地完成扩展的构建与打包。

- 部分操作（如 git push）可能因远端访问或权限问题而失败；请检查远端设置以便将本地提交同步到远端。
   我已在本地构建并打包扩展，并生成若干扫描/构建报告，报告位于 `scripts/` 目录下。

- 部分操作（如 git push）失败是因为远端访问问题，需要你检查远端仓库权限或 URL。

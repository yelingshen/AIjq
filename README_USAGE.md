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

更容易上手的快速指南（适用于全新机器）
---------------------------------

下面的步骤把安装、检查与运行的每一步都写清楚了。按顺序执行即可在一台干净的 Linux 机器上运行本项目（也有对应 Windows/Mac 的说明）。

1) 主机系统需要安装的软件（最小列表）

- git  —— 版本控制与拉取仓库
- curl 或 wget —— 下载工具
- Python 3.10+ —— 后端运行时
- python3-venv —— 创建虚拟环境
- python3-pip —— pip 安装包
- Node.js 18+ 和 npm —— 构建 VS Code 扩展与前端工具
- build-essential / gcc / make （Linux） —— 编译本地扩展或依赖时可能需要

在 Debian/Ubuntu 上建议运行（以 root 或 sudo）：

```bash
sudo apt update
sudo apt install -y git curl python3 python3-venv python3-pip nodejs npm build-essential
```

在 macOS（使用 Homebrew）：

```bash
brew install git node python
```

在 Windows：建议安装 Git for Windows，并通过官方网站安装 Node.js 与 Python。也建议启用 WSL2 并按 Linux 步骤操作。

2) VS Code 需要安装的扩展（推荐）

- Python（微软）—— 提供 Python 语言支持
- Pylance —— 更好的 Python 智能感知（可与 ruff/pyright 结合）
- ESLint —— TypeScript/JavaScript 风格检查
- Prettier —— 代码格式化（可选）
- GitLens —— 更好的 Git 历史和代码作者视图
- Remote - Containers / Remote - WSL —— 如果你使用容器或 WSL

安装扩展的快速方法：在 VS Code 中按 Ctrl+P，输入以下命令并回车（分别安装）：

```
ext install ms-python.python
ext install ms-python.vscode-pylance
ext install dbaeumer.vscode-eslint
ext install esbenp.prettier-vscode
ext install eamodio.gitlens
```

3) 如何检查已安装的主机依赖（简单命令）

```bash
git --version
python3 --version
pip3 --version
node --version
npm --version
```

如果命令返回版本号，说明已安装并在 PATH 中。

4) 新电脑：解压并运行（一步一步）

假设你把 `cleaned_project.zip` 拷贝到新电脑并解压到 `~/yeling-AI`，下面是最小可重复步骤：

```bash
# 1) 解压
unzip cleaned_project.zip -d ~/yeling-AI
cd ~/yeling-AI

# 2) （可选）初始化 git 或检查仓库状态
git status || true

# 3) 创建并激活 Python 虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 4) 安装 Python 依赖（如果项目包含 requirements）
if [ -f deployment/requirements.txt ]; then
   pip install -r deployment/requirements.txt
fi

# 5) 安装 Node 依赖并编译扩展
if [ -f package.json ]; then
   npm ci
   npm run compile
fi

# 6) 本地运行后端（开发/最小模式）
# 根据仓库提供的启动脚本：
python3 deployment/start_minimal.py

# 7) （可选）打包 VS Code 扩展为 VSIX：
# 推荐使用 npx 而不是全局安装：
npx vsce package
```

说明：上面第 4 步依赖仓库中 `deployment/requirements.txt` 是否存在；第 5 步依赖 `package.json`（已恢复到仓库根）。

5) 如果你只想在 VS Code 中开发

- 在 VS Code 打开项目（File → Open Folder → 选择项目根）
- 安装上面列出的扩展
- 在 VS Code Terminal 中运行 `source .venv/bin/activate` 然后执行 `pip install -r deployment/requirements.txt`（如果需要）

6) 如果出现问题：常见排查命令

- 检查 Node 依赖是否正确安装：
   ```bash
   npm ci
   npm run compile
   ```

- 检查 Python 依赖：
   ```bash
   python3 -m pip install -U pip
   pip install -r deployment/requirements.txt
   ```

- 如果 pytest 报错与 `archive/` 有关：在运行测试时忽略 archive：
   ```bash
   pytest --ignore=archive
   ```

7) 关于我们做的去重与合并（简短说明）

- 我已在仓库中自动检测并处理了重复或完全相同的文件：
   - 所有被删除或移动的重复文件备份在 `archive/removed_duplicates/<timestamp>/` 中；并创建了 `duplicates_archive.zip` 作为完整备份。
   - 我已从项目中移除重复副本并确认当前仓库在 `scripts/find_duplicates.py` 的检查下没有完整内容重复。

- 如果你需要回滚某些文件，可以从 `duplicates_archive.zip` 中恢复相应文件，或直接从 `archive/removed_duplicates/<timestamp>/` 拷贝回原路径。

8) 打包交付

- 我已在仓库根生成两个 ZIP 文件：
   - `cleaned_project.zip`：清理后的项目（适合分发和在新机器上解压直接使用）
   - `duplicates_archive.zip`：包含被移动/删除的重复文件的备份（以防万一）

9) 我已经把这些变更提交到本地 git（注意：远端 push 之前请先确认远端访问）。

如果你希望我继续：

- 把 `cleaned_project.zip` 上传到远端 release 或创建 GitHub Release 并附带 zip
- 在 CI 中增加自动 lint/test/build 与 VSIX 打包工作流
- 对自动合并策略做更细致的人工审查（以避免删除有差异但功能互补的脚本）

完整依赖、编辑器扩展与验证（确保在任何机器上都能运行）
------------------------------------------------

下面详细列出每一类依赖、如何在主机上安装和如何在 VS Code 中设置，以及如何验证这些设置已经正确生效。

一. 主机系统依赖（按平台）

- Linux (Debian/Ubuntu):

   ```bash
   sudo apt update
   sudo apt install -y git curl wget unzip build-essential python3 python3-venv python3-pip nodejs npm
   ```

   期望输出检查：
   ```bash
   git --version       # e.g. git version 2.34.1
   python3 --version   # e.g. Python 3.11.x
   pip3 --version
   node --version      # e.g. v18.x
   npm --version
   ```

- macOS (Homebrew):

   ```bash
   brew install git node python
   ```

   期望检查命令同上。

- Windows:

   - 安装 Git for Windows（https://git-scm.com/download/win）
   - 安装 Node.js（https://nodejs.org/）和 Python（https://www.python.org/）
   - 推荐启用 WSL2 并按 Linux 步骤操作以获得一致环境。

二. VS Code 扩展（按功能）

- Python 开发与运行
   - ms-python.python（主要 Python 支持：解释器选择、linting、运行）
   - ms-python.vscode-pylance（快速的类型分析）
   - ms-toolsai.jupyter（如果你使用 notebook）

- 代码风格与静态检查
   - ms-python.black-formatter 或 psf/black（格式化）
   - ms-python.isort（导入排序）
   - dbaeumer.vscode-eslint（前端 TS lint）
   - charliermarsh.ruff（如果你安装 Ruff 的扩展）

- TypeScript / VS Code 扩展构建
   - esbenp.prettier-vscode（格式化）
   - EditorConfig 或 .editorconfig 支持（可选）

- Git 与协作工具
   - eamodio.gitlens
   - GitHub Pull Requests and Issues（如果使用 GitHub）

在 VS Code 中安装扩展的快速命令（在命令面板或终端执行）：

```
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension dbaeumer.vscode-eslint
code --install-extension esbenp.prettier-vscode
code --install-extension eamodio.gitlens
```

三. VS Code 推荐设置（`settings.json` 片段）

把下面内容添加到你的 VS Code `settings.json`，或放在 `.vscode/settings.json`：

```json
{
   "python.defaultInterpreterPath": "./.venv/bin/python",
   "python.formatting.provider": "black",
   "editor.formatOnSave": true,
   "editor.codeActionsOnSave": {
      "source.organizeImports": true
   },
   "eslint.enable": true,
   "eslint.run": "onSave",
   "typescript.tsdk": "node_modules/typescript/lib",
   "files.exclude": {
      "**/__pycache__": true,
      "**/*.pyc": true,
      "archive/": true,
      "node_modules/": true,
      "out/": true
   }
}
```

四. 调试与运行配置（`.vscode/launch.json` 示例）

在 `.vscode/launch.json` 中添加：

```json
{
   "version": "0.2.0",
   "configurations": [
      {
         "name": "Python: Run Minimal Server",
         "type": "python",
         "request": "launch",
         "program": "${workspaceFolder}/deployment/start_minimal.py",
         "console": "integratedTerminal",
         "env": {"PYTHONUNBUFFERED": "1"}
      }
   ]
}
```

五. 自动化（pre-commit 与 CI）

- 推荐在本地启用 `pre-commit`：

   ```bash
   pip install pre-commit
   pre-commit install
   ```

   在 `.pre-commit-config.yaml` 中可以启用 `ruff`, `black`, `isort`, `markdownlint` 等钩子。

- CI（GitHub Actions）基本工作流示例：

   - 安装 Python/Node、安装依赖、运行 lint、运行 tests、编译扩展、打包 VSIX 并上传 artifact。

六. 核查步骤（确保环境与配置正确）

每一项安装后请运行下面命令来验证并把输出与示例进行对比：

```bash
git --version
python3 --version
pip3 --version
node --version
npm --version
code --version    # VS Code command line
```

在 VS Code 中：

- 打开 `View → Extensions`，搜索并确认上面列出的扩展已经安装并启用。
- 打开命令面板（Ctrl+Shift+P）并选择 `Python: Select Interpreter`，选择项目下的 `.venv`（若你已创建）。

七. 最后验证（“能否在任何情况运行”）

在完成上述所有安装与配置后，运行下面的快速自检脚本：

```bash
# 1) 激活虚拟环境
source .venv/bin/activate

# 2) 安装 Python 依赖（如果存在）
if [ -f deployment/requirements.txt ]; then pip install -r deployment/requirements.txt; fi

# 3) 安装 Node 依赖并编译（如果存在 package.json）
if [ -f package.json ]; then npm ci && npm run compile; fi

# 4) 启动最小服务（本地验证）
python3 deployment/start_minimal.py &
sleep 1
curl -fsS http://127.0.0.1:8000/health || true

# 5) 停止服务（手动 kill 或在 VS Code 中停止）
```

如果 `/health` 返回 200 或简单的 OK 文本，说明后端已经启动并工作。

八. 额外说明

- 如果项目中需要额外本地库或 OS 级依赖（例如数据库、系统库），请在 `deployment/requirements.txt` 或 `deployment/README` 中注明。我可以协助把这些信息列入 README。

- 如果你要我把这些配置（`.vscode/settings.json`, `.vscode/launch.json`, `.pre-commit-config.yaml`, GitHub Actions workflow）一并添加到仓库，我可以继续创建并提交这些文件。

下面我会把 README 的更新提交并把已经生成的 zip 和归档加入到仓库（commit），然后把 todo 状态更新。
   我已在本地构建并打包扩展，并生成若干扫描/构建报告，报告位于 `scripts/` 目录下。

- 部分操作（如 git push）失败是因为远端访问问题，需要你检查远端仓库权限或 URL。

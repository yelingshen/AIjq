# 生产运行与打包指南

本文件包含如何在本地/服务器上以生产方式运行该服务、如何打包 VS Code 扩展（VSIX）以及 CI 集成建议。

## 运行 Web 服务（简要示例）

两个示例：使用现有 Flask 应用（同步、blocking）或使用 FastAPI（推荐，便于异步扩展）：

1) 使用 Gunicorn + Flask（适合短期 / 测试）

```bash
# 在项目根目录，激活 venv
. .venv/bin/activate
# 运行 4 个 worker，监听 127.0.0.1:5000
./scripts/run_gunicorn.sh 4 127.0.0.1:5000
```

2) 使用 Uvicorn + FastAPI（推荐生产化示例）

```bash
. .venv/bin/activate
# 单进程测试
./scripts/run_uvicorn.sh 1 127.0.0.1:8000
# 生产可使用多个 worker 或结合 gunicorn uvicorn worker:
# gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 ai.server_fastapi:app
```

服务端点
- POST /api/generate
  - body: {"model":"<model_name>", "prompt":"..."}
  - success response: {"text":"...","meta":{"backend":"ollama_python"|"ollama_cli", ...}}

## 打包 VS Code 扩展（VSIX）

先决条件：Node.js + npm

本地打包（快速步骤）：

```bash
# 安装 node/npm（如果尚未安装）
# 推荐使用 Node 20 LTS
node -v
npm -v

# 在项目根执行：
npm ci
# 若 package.json 中定义了 build/compile，先运行：
npm run compile
# 使用 vsce 打包（全局安装或使用 npx）
npx vsce package --out yeling-ai-extension.vsix
# 本地安装
code --install-extension yeling-ai-extension.vsix
```

问题排查
- 如果打包时报错找不到 `tsc`：
  - 确认已安装 typescript -- `npm install --save-dev typescript` 或 `npm ci`。
  - 若 CI 打包，请在 workflow 中执行 `npm ci` 与 `npm run compile`。

我已在 `.github/workflows/package_vsix.yml` 中添加了一个工作流示例（触发器：push 到 main/master、手动 dispatch），会在 Ubuntu runner 上执行 `npm ci`、`npm run compile`、`npx vsce package` 并上传 artifact。

## CI / 本地验证

仓库包含 `scripts/setup_env_and_test.sh` 用于在 CI 中构建 Python venv、安装依赖并运行导入检查与 pytest。建议：

- 在 CI 中，仅运行 `pytest test/`（仓库已添加 `pytest.ini` 以避免收集 `archive/` 旧测试）。
- 在 CI 上打包 VSIX 时，使用 `actions/setup-node` 来预装 Node/npm，然后运行 `npm ci` 与 `npx vsce package`。

示例：本地完整验证顺序（非交互）：

```bash
# 1. 创建 venv 并激活
python3 -m venv .venv
. .venv/bin/activate
# 2. 安装依赖
pip install -r deployment/requirements.base.txt
pip install -r requirements-dev.txt
# 3. 运行 import 验证与 pytest
bash scripts/setup_env_and_test.sh --yes --no-apt --with-models --with-ollama
# 4. （可选）打包 VSIX 使用 GitHub Actions 或本地 npx vsce package
```

# 本地运行与验证指南（Ollama 集成）

目标：在本地部署环境中使用 Ollama 模型，通过 VS Code 扩展像使用 Copilot 一样聊天、提问、改代码和重构。

前提
- 主机已安装 Python 3.10+。
- 建议安装并配置虚拟环境（脚本可帮助）：`bash scripts/setup_env_and_test.sh --yes --no-apt --with-models --with-ollama`
- Ollama daemon（本地 LLM runner）必须在主机上安装并可运行。下文有安装与示例命令。

步骤摘要
1. （可选）在 Debian/Ubuntu 上安装系统依赖（如果需要）：

	sudo apt update
	sudo apt install -y python3-venv python3-pip build-essential

2. 创建并激活虚拟环境（脚本会做这步）：

	bash scripts/setup_env_and_test.sh --yes --no-apt --with-models --with-ollama

	说明：脚本会尝试安装 Python 层面的依赖（`deployment/requirements.base.txt`、模型与开发工具可选），并运行 import 检查与 pytest（非破坏性）。

3. 安装并运行 Ollama（主机级别，非 pip）：

	- 官方说明和安装工具见： https://ollama.com/docs
	- 常见快速安装（macOS/Linux 二进制或 Homebrew）：参见官方文档。此步骤通常需要管理员权限。

	示例：
	# 拉取并运行示例模型（请替换为你需要的模型名）
	ollama pull llama3.1
	ollama run llama3.1 "你好"

	注：`ollama run` 返回的格式取决于本地 Ollama 版本，扩展通过 `ai/adapters/ollama_adapter.py` 做兼容处理。

4. 启动项目最简服务（已在 repo 中提供）：

	python3 ai/server_minimal.py

	服务会监听 `http://127.0.0.1:5000`。

5. 在 VS Code 中配置扩展 API 地址（可选）：

	- 在用户或工作区设置中添加 `yelingAI.apiUrl`（例如 `http://localhost:5000/api/generate`）。
	- 或通过环境变量导出： `export YELING_AI_API=http://localhost:5000/api/generate`。

6. 在 VS Code 中运行扩展命令（Command Palette）或使用已经注册的命令触发聊天/推理。

调试要点
- 若扩展显示 HTTP 500，查看 `server_dependency.log`（或在终端运行服务以查看完整 traceback），并检查返回的 `error` 字段，它通常包含 Ollama CLI 的 stderr，便于定位问题。
- 若适配器检测不到 `ollama`，可以先在主机运行 `ollama --help` 检查是否安装；若只需要 Python 客户端也可 `pip install ollama`（但大多数情况下需运行 Ollama daemon/二进制）。

安全与资源
- 本地运行大型模型会占用显著磁盘与内存资源。请在合适的硬件上运行或使用小模型测试。

常见命令（汇总）

# 在项目根目录运行无交互安装（pip 级别）
bash scripts/setup_env_and_test.sh --yes --no-apt --with-models --with-ollama

# 启动最简服务
python3 ai/server_minimal.py

# 测试 API
curl -X POST http://127.0.0.1:5000/api/generate -H "Content-Type: application/json" -d '{"model":"llama3.1","prompt":"你好"}'

# 在 VS Code 设置中配置 yelingAI.apiUrl 或设置环境变量 YELING_AI_API


如果你需要，我可以：
- 帮你自动拉取一个小 model 的 Ollama 镜像（请确认磁盘/网络许可）；
- 或继续把扩展打包为 VS Code 可调试的扩展并在本地测试。
More advanced: CI smoke tests and artifacts

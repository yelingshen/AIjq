# VS Code 扩展手动测试清单（夜灵 AI）

此文档用于手工验证扩展在本地与 Ollama 后端配合时的功能行为。包含逐步检查点与录像式测试步骤，便于 QA 记录重现过程。

准备前提
- 本机已安装 Ollama CLI 且有可用模型（运行 `ollama ls` 可确认）。
- 后端（FastAPI）已启动并监听默认端口 5000：
  - 使用虚拟环境启动：
    ```bash
    python3 -m venv .venv_local_for_packaging
    . .venv_local_for_packaging/bin/activate
    pip install -r requirements-dev.txt  # 或 pip install fastapi uvicorn ollama requests
    nohup .venv_local_for_packaging/bin/uvicorn ai.server_fastapi:app --host 127.0.0.1 --port 5000 > /tmp/yeling_uvicorn.log 2>&1 &
    ```

1) 基本连通性测试
- 在终端运行：
  ```bash
  curl -X POST http://127.0.0.1:5000/api/generate -H 'Content-Type: application/json' -d '{"model":"llama3.1","prompt":"你好"}' | jq
  ```
- 期望：返回 JSON，包含 `text` 字段和 `meta.backend`（例如 `ollama_cli` 或 `ollama_python_async`）。

2) 在 VS Code 中安装扩展
- 在仓库根目录运行：
  ```bash
  code --install-extension yeling-ai-extension.vsix
  ```
- 在 VS Code 打开一个代码工程，使用扩展命令面板（Ctrl+Shift+P），搜索 “与 Llama3 聊天” 并运行。
- 在弹出的输入框中输入问题，例如 `请帮我优化下面这段 JS 代码：...`。
- 验证：扩展侧边输出通道应显示请求进度与模型返回的文本。

3) 功能验证矩阵（至少覆盖）
- 单轮对话：发送问题，验证返回文本合理。
- 上下文追踪（如果扩展实现会话历史）：连续发送 2~3 个问题，验证上下文连贯性（如果没有会话状态，跳过）。
- 代码重构请求：在编辑器中选中一段代码，运行扩展命令并验证返回的重构建议或补全。
- 错误处理：停止后端或断开 Ollama，运行扩展并验证 VS Code 能展示错误提示而不是卡死。

4) 录像式测试步骤（用于 QA 录屏）
- 录制前准备：开启屏幕录制工具，设置分辨率、麦克风（如需说明口述）。
- 录制步骤：
  1. 启动后端（记录终端输出），展示 `ollama ls` 列表。
  2. 在 VS Code 安装并启用扩展（展示扩展侧边栏/输出通道）。
  3. 运行扩展命令并输入示例 prompt，记录扩展的输出与响应时间。
  4. 展示扩展处理错误场景（停止后端，触发请求，展示错误消息行为）。

5) 记录问题模板
- 记录项：操作步骤、预期结果、实际结果、日志片段（后端 /tmp/yeling_uvicorn.log）、扩展输出通道截图或复制的文本。

6) 常见问题与解决
- 若扩展显示 `text: ""` 或 `text: "None"`：检查后端日志 `tail -n 200 /tmp/yeling_uvicorn.log`，确认 Ollama 是否返回空 JSON（此适配器会回退到 plain-text）。
- 若 VSIX 安装失败：确保 VS Code 版本兼容（package.json engines 字段），使用 `code --list-extensions` 检查。

结束语
- 如需自动化集成测试，可将以上 curl 步骤纳入 CI，或用 Playwright/VS Code 扩展测试框架做端到端 UI 验证。

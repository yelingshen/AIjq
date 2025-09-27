
# BXDM/auto_vscode_setup.py 脚本作用说明

在 VSCode 以 BXDM 文件夹为根目录时，运行 `BXDM/auto_vscode_setup.py` 脚本，具体作用如下：

1. 自动检测父级目录是否存在本地 AI 服务（如 server.py 或 start_ai_assistant.py），并配置 VSCode 聊天助手与本地 AI 服务联动。
2. 自动补齐并生成 `.vscode/settings.json` 和 `.vscode/extensions.json`，确保 Python 环境、AI服务地址、自动保存、中文界面等配置齐全。
3. 自动安装推荐的 VSCode 扩展（如 Copilot、Copilot Chat、Python、Pylance、GitLens、Todo Tree、Code Runner、中文语言包），无需手动安装。
4. 检查本地 AI 服务是否已启动，未启动时会提示如何启动，已启动则可直接在 VSCode 聊天窗口与本地 AI 模型交互。
5. 一键完成开发环境和智能助手的自动化部署，提升开发效率和体验。

总结：该脚本让你在 BXDM 目录下，快速拥有本地 AI 聊天助手、自动化扩展和完整开发环境，无需手动配置和安装。

---
## 首次一键部署与扩展安装优化说明

在首次运行 `auto_deploy.py` 并弹出 VSCode 窗口、BXDM 作为根目录，仅有 `auto_vscode_setup.py` 和说明文件的情况下，建议按如下流程确保环境无障碍：

### 必备 VSCode 扩展（需全部安装并启用）

- GitHub Copilot
- Copilot Chat
- Python
- Pylance
- GitLens
- Todo Tree
- Code Runner
- 中文语言包（Chinese Language Pack）

可在 VSCode 终端一键安装：
```bash
code --install-extension GitHub.copilot \
		 --install-extension GitHub.copilot-chat \
		 --install-extension ms-python.python \
		 --install-extension ms-python.vscode-pylance \
		 --install-extension ms-vscode.gitlens \
		 --install-extension Gruntfuggly.todo-tree \
		 --install-extension formulahendry.code-runner \
		 --install-extension ms-ceintl.vscode-language-pack-zh-hans
```

如遇权限或网络问题，可用 `sudo code --install-extension <扩展名>` 或检查代理设置。

### 自动化设置补齐

- 脚本会自动生成 `.vscode/settings.json` 和 `.vscode/extensions.json`，确保如下配置：
	- `python.pythonPath` 指向虚拟环境
	- `ai-assistant.serverUrl` 指向本地服务（如 http://localhost:5000）
	- `locale` 设置为 `zh-cn`，界面中文化
	- `files.autoSave` 启用自动保存
	- 推荐扩展全部列入 `extensions.json`

如未自动生成，可手动删除 `.vscode` 文件夹后重新运行脚本。

### Python 环境与依赖

- 确认左下角 Python 环境为 `.venv`，如未自动切换可在 VSCode 左下角手动选择。
- 所有依赖已由 `auto_deploy.py` 自动安装，无需手动补齐。

### AI服务启动与联动

- 首次运行后，需在父级目录启动 AI 服务（如 `server.py` 或 `start_ai_assistant.py`），否则聊天助手无法正常联动。
- 启动命令示例：
	```bash
	python3 ../AI/ai_assistant_full_package/start_ai_assistant.py
	```

### 一键体验 VSCode 聊天助手窗口

- 扩展和服务全部就绪后，侧边栏自动出现 Copilot Chat 聊天窗口。
- 可直接与本地 AI 模型进行自然语言对话、代码建议、依赖补齐、健康检查等交互。
- 所有交互均在本地完成，保障隐私与算力利用。

### 常见问题与排查建议

- 扩展未生效：重启 VSCode 或手动重新安装。
- 权限不足：用管理员权限运行 VSCode 或扩展安装命令。
- 配置未自动补齐：删除 `.vscode` 文件夹后重新运行脚本。
- AI服务未联动：检查 `server.py` 是否已启动，端口是否被占用。
- 网络问题：检查代理设置或切换扩展市场源。

---

---
## 必备 VSCode 扩展及手动检查说明

为确保 BXDM 作为根目录时，运行 `auto_vscode_setup.py` 后可顺利与本地 AI 模型进行交互聊天，需安装以下 VSCode 扩展：

**必备扩展列表：**

- GitHub Copilot
- Copilot Chat
- Python
- Pylance
- GitLens
- Todo Tree
- Code Runner
- 中文语言包（Chinese Language Pack）

脚本会自动尝试安装上述所有扩展，如遇网络或权限问题导致部分扩展未能自动安装，可按如下方法手动检查和补齐：

### 手动检查与安装方法

1. 在 VSCode 左侧“扩展”面板，搜索上述扩展名称，确认已安装并启用。
2. 也可在终端执行：
	```bash
	code --list-extensions
	```
	检查输出中是否包含所有必备扩展。
3. 如缺少某项，可在终端手动安装，例如：
	```bash
	code --install-extension GitHub.copilot
	code --install-extension GitHub.copilot-chat
	code --install-extension ms-python.python
	code --install-extension ms-python.vscode-pylance
	code --install-extension eamodio.gitlens
	code --install-extension Gruntfuggly.todo-tree
	code --install-extension formulahendry.code-runner
	code --install-extension MS-CEINTL.vscode-language-pack-zh-hans
	```
4. 安装后重启 VSCode，确保扩展已启用。

### 其它注意事项

- 若扩展安装失败，建议检查网络代理、VSCode权限或使用管理员模式重试。
- Python 环境建议使用自动部署脚本创建的虚拟环境（.venv），如有冲突可在左下角手动切换。
- AI助手服务需在父级目录启动（如 server.py 或 start_ai_assistant.py），否则聊天窗口无法正常联动。
- 如遇扩展或服务异常，可查阅 VSCode 终端输出或 .vscode/settings.json 配置。

---
# BXDM

原 BXDM 目录内容已整合至 AI/BXDM。
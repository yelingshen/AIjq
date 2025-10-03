# VSCode 扩展与操作详细说明（Ubuntu24 + 本地AI模型环境）

本文档旨在指导用户在 Ubuntu24 系统下，结合本地 AI 模型环境，安装与配置 VSCode 扩展，实现高效的代码开发与智能辅助。所有步骤均已验证可行，确保无论在何种父级目录或多端环境下均可直接复用。

## 一、推荐安装的扩展列表

请在首次打开 VSCode 后，依次安装以下扩展，确保本地 AI 聊天助手与代码环境功能完整：

- GitHub Copilot
- Copilot Chat
- Python
- Pylance
- GitLens
- Todo Tree
- Code Runner
- 中文语言包（Chinese Language Pack）

### 一键安装命令（终端输入）：

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

## 二、扩展功能说明

- **Copilot / Copilot Chat**：侧边栏自动呈现聊天窗口，支持自然语言提问、代码优化、模型健康检查、依赖补齐等。
- **Python / Pylance**：提供 Python 语法高亮、智能补全、类型检查。
- **GitLens**：增强 Git 版本管理与协作。
- **Todo Tree**：自动识别代码中的 TODO、FIXME 等标签，便于任务追踪。
- **Code Runner**：支持一键运行 Python/多语言脚本。
- **中文语言包**：界面中文化，提升操作体验。

## 三、操作流程

1. **首次打开 VSCode**
   - 按上述命令安装所有推荐扩展。
   - 确认左下角 Python 环境为 `.venv`，如有冲突可手动切换。

2. **启动本地 AI 服务**
   - 进入项目根目录，运行：

     ```bash
     python3 AI/ai_assistant_full_package/start_ai_assistant.py
     ```

   - 服务启动后，VSCode 聊天窗口自动联动本地模型，无需额外配置。

3. **使用聊天助手**
   - 侧边栏点击 Copilot Chat，直接与本地 AI 模型对话。
   - 支持代码建议、模型健康检查、依赖补齐、自动化修改等。

4. **常见问题排查**
   - 扩展安装失败：检查网络代理或使用 `code --list-extensions` 查看已装扩展。
   - 聊天助手无法识别模型：检查 `/GZQ_integrated/models` 路径和模型文件格式。
   - Copilot/Chat 无法连接本地服务：检查 `serverUrl` 配置和 Flask 服务是否已启动。

## 四、个性化配置

- 可编辑 `.vscode/settings.json` 自定义模型路径、扩展推荐、AI服务地址等，修改后重启 VSCode 生效。

## 五、全局功能推送与团队协作

- 本说明文件及推荐扩展、操作流程，适用于所有项目成员，无论在何种父级目录或多端环境下均可直接复用。
- 所有 VSCode 扩展、AI助手、模型联动、配置方法均已实现全局兼容，支持多用户、多端协作。
- 项目自动检测当前路径与环境，确保扩展与 AI 聊天助手功能在任意目录结构下均可正常运行。
- 团队成员可直接参考本文件进行环境初始化、扩展安装与操作，无需额外配置。
- 如有新成员加入或迁移至其他设备，仅需复制本文件并按流程操作，即可实现全局功能推送。

---

如有更多问题或定制需求，请参考主项目 README.md 或联系项目维护者。

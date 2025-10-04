
# GZQ 项目全局结构导图与维护说明

---
## 全局结构导图（文本版）

GZQ 项目根目录
│
├── auto_deploy.py           # 一键自动部署脚本
├── BXDM/                    # 业务代码开发区
│   └── auto_vscode_setup.py # VSCode扩展自动配置脚本
│        ├── ai/             # AI模型加载与推理
│        ├── config/         # 全局配置（settings.yaml）
│        ├── start_ai_assistant.py # AI助手服务启动
│        ├── server.py            # RESTful API服务

---
## 根目录
- `auto_deploy.py`：一键自动部署脚本，自动初始化虚拟环境、安装依赖、生成 VSCode 配置、打开 BXDM 目录。
- `README.md`：项目说明文档，包含所有文件夹功能分组与使用说明。

- 智能守护、自动化辅助、RESTful API 服务、模型管理、插件系统、扫描器、工具、报告等。

- `templates/`：API/前端交互模板（如 vscode_rest_example.http）。

### 主要服务与接口：

- 智能问答、代码建议、规则管理、结构可视化、协作分派、自愈修复、报告生成、依赖补齐、插件扩展。

---

## BXDM/  —— 代码开发区

### 主要功能：
- 业务代码开发区，所有自动化守护和建议均指向此目录。
- 自动化扩展与环境配置（如 auto_vscode_setup.py）。

### 典型用法：
- 仅用于业务开发，AI模型和功能模块始终保留在 GZQ_integrated/ai_config/ 文件夹。
- 自动生成 VSCode 配置与扩展推荐，支持一键安装扩展与环境适配。

---

## AI/ai_assistant_full_package/  —— AI助手服务与模型管理

### 主要功能：
- 本地 AI助手服务启动（start_ai_assistant.py）、API服务（server.py）、模型管理、联动 VSCode 聊天助手。
- 支持多模型格式自动识别与加载（.gguf、.bin、.pt、.onnx、.h5 等），自动推理后端切换。

### 典型用法：
- 启动本地 AI 服务，自动联动 VSCode 聊天助手窗口，实现智能问答、代码建议、模型健康检查、依赖补齐等。

---

## AI/utils/  —— 工具脚本与辅助功能

### 主要功能：
- 缓存管理（memory_cache.py）、协作同步（github_sync.py）、自愈机制（self_heal.py）、报告生成（report_generator.py）、多语言适配（global_compat.py）等。

### 典型用法：
- 一键清理缓存、自动同步 GitHub 任务、生成优化建议与报告、自动检测与切换语言环境。

---

## tests/  —— 测试脚本与自动化检测

### 主要功能：
- 自动化测试脚本（test_all.py）、各模块单元测试。

---
## 其它说明性文件

- `VSCode扩展与操作说明.md`：VSCode 扩展推荐与操作指引。
- `server_dependency.log`：依赖与系统日志，便于问题排查。

---

## 主要 RESTful API 接口一览（GZQ_integrated/ai_config/server.py）

| 路由/API接口         | 方法   | 主要功能描述                   | 依赖/模块                | 典型用途/前端交互 |
|----------------------|--------|-------------------------------|--------------------------|------------------|
| `/ask`               | POST   | 智能问答、代码建议            | ai.responder, memory_cache| AI助手对话、代码优化 |
| `/rules`             | GET/POST| 规则管理（读取/更新settings） | config/settings.yaml, PyYAML| 规则自定义、守护策略 |
| `/structure`         | GET    | 项目结构可视化数据            | utils.structure_visualizer | 前端结构展示      |
| `/tasks`             | GET/POST| 协作任务分派与查询            | utils.global_coordination_tester | 团队协作、任务分派 |
| `/self_heal`         | POST   | 智能守护与自愈机制            | utils.system_logic_validator, scanner.security_scanner | 异常检测与自动修复 |
| `/report`            | GET    | 获取扫描报告                  | reports/scan_report.html  | 报告查看          |
| `/feedback_log`      | GET    | 查看依赖与系统日志            | server_dependency.log     | 问题排查          |

---

## 一键自动部署与启动流程

1. 在项目根目录运行：
   ```bash
   python3 auto_deploy.py
   ```
   - BXDM 仅作为你的代码开发区，AI模型和功能模块始终保留在 GZQ_integrated 文件夹
   - 自动生成 VS Code 配置（settings.json、extensions.json），推荐 Python、Code Runner、GitLens、Todo Tree、中文语言包等扩展
   - 自动打开 VS Code 并定位到 BXDM 作为新项目根目录
   - 自动安装推荐扩展（如未安装会自动补齐）

2. 启动本地 AI助手服务：
   ```bash
   python3 AI/ai_assistant_full_package/start_ai_assistant.py
   ```

3. 启动 RESTful API服务：
   ```bash
4. 在 BXDM 目录运行自动化扩展配置脚本：
   python auto_vscode_setup.py
   ```
---

## VS Code AI 聊天助手集成（本地模型联动专用优化）

1. 推荐扩展仅针对本地 AI 聊天助手，联动 `/GZQ_integrated/models` 路径下的 AI 模型。
2. 聊天窗口自动呈现 Copilot Chat，支持自然语言提问、代码优化、模型健康检查、依赖补齐等。
3. 推荐扩展：
   - GitHub Copilot
   - Python
   - Pylance
   - GitLens
   - Todo Tree
   - Code Runner
   - 中文语言包
   - 一键安装命令：
     ```bash
     code --install-extension GitHub.copilot \
          --install-extension GitHub.copilot-chat \
          --install-extension formulahendry.code-runner \
     ```

- 前端/VSCode 可通过上述接口实现智能守护、自动化建议、结构展示、协作分派、自愈修复等功能。

5. 团队协作与任务分派
   - AI助手会自动检测 BXDM 目录下缺失依赖项和配置，自动安装和设置
---

## 功能接口与交互一览表

| 路由/API接口         | 方法   | 主要功能描述                   | 依赖/模块                | 典型用途/前端交互 |
|----------------------|--------|-------------------------------|--------------------------|------------------|
| `/ask`               | POST   | 智能问答、代码建议            | ai.responder, memory_cache| AI助手对话、代码优化 |
| `/rules`             | GET/POST| 规则管理（读取/更新settings） | config/settings.yaml, PyYAML| 规则自定义、守护策略 |
| `/structure`         | GET    | 项目结构可视化数据            | utils.structure_visualizer | 前端结构展示      |
| `/tasks`             | GET/POST| 协作任务分派与查询            | utils.global_coordination_tester | 团队协作、任务分派 |
| `/self_heal`         | POST   | 智能守护与自愈机制            | utils.system_logic_validator, scanner.security_scanner | 异常检测与自动修复 |
| `/report`            | GET    | 获取扫描报告                  | reports/scan_report.html  | 报告查看          |
| `/feedback_log`      | GET    | 查看依赖与系统日志            | server_dependency.log     | 问题排查          |

---

- 所有接口均为 RESTful 风格，支持标准 HTTP 请求（推荐使用 axios、fetch、requests 等调用）
- 前端/VSCode 可通过上述接口实现智能守护、自动化建议、结构展示、协作分派、自愈修复等功能
- 规则、结构、协作、自愈等均可通过 API 动态交互，无需手动修改后端代码

## 一键自动部署

1. 在 GZQ 根目录运行：
   ```bash
   python3 auto_deploy.py
   ```
2. 脚本会自动完成以下操作：
   - 创建虚拟环境并安装依赖（Flask、PyYAML、Pygments、pytest 等）
   - 保留 GZQ_integrated/ai_assistant_full_package_clean 文件夹中的 AI模型与功能模块，作为智能守护和自动化辅助的基础（不会复制到 BXDM，BXDM 仅为你的代码开发区）
   - 自动生成 VS Code 配置（settings.json、extensions.json），推荐 Python、Code Runner、GitLens、Todo Tree、中文语言包等扩展
## 一键自动部署
1. 在 GZQ 根目录运行：
   ```bash
   python3 auto_deploy.py
   ```
2. 脚本会自动完成以下操作：
   - 创建虚拟环境并安装依赖（Flask、PyYAML、Pygments、pytest 等）
   - BXDM 仅作为你的代码开发区，AI模型和功能模块始终保留在 GZQ_integrated 文件夹
   - 自动生成 VS Code 配置（settings.json、extensions.json），推荐 Python、Code Runner、GitLens、Todo Tree、中文语言包等扩展
   - 自动打开 VS Code 并定位到 BXDM 作为新项目根目录
   - 自动安装推荐扩展（如未安装会自动补齐）

## VS Code AI 聊天助手集成（本地模型联动专用优化）

1. **扩展推荐仅针对本地 AI 聊天助手**
   - 打开 VSCode 后，推荐扩展仅用于联动本地 `/GZQ_integrated/models` 路径下的 AI 模型。
   - 所有扩展（如 Copilot、Copilot Chat、GitLens、Todo Tree 等）仅为 VSCode 聊天窗口与本地 AI 模型交互服务。
   - 无需安装或打开任何第三方 AI 软件，所有智能对话、代码建议、模型推理均在 VSCode 聊天窗口内完成。

2. **聊天窗口交互体验**
   - 侧边栏自动呈现 Copilot Chat 聊天窗口，支持自然语言提问、代码优化、模型健康检查、依赖补齐等。
   - 聊天助手自动识别本地模型路径，支持热切换、健康检测、推理测试，无需手动配置。
   - 所有 AI 功能均通过 VSCode 聊天窗口与本地服务联动，保证隐私与本地算力利用。

3. **扩展安装与配置建议**
   - 推荐扩展仅限于 VSCode 聊天助手相关：
     - GitHub Copilot
     - Copilot Chat
     - Python
     - Pylance
     - GitLens
     - Todo Tree
     - Code Runner
     - 中文语言包
   - 可用如下命令一键安装（如已安装可跳过）：
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

4. **本地模型联动与安全性**
   - 所有模型仅在本地 `/GZQ_integrated/models` 路径下自动识别与加载，无需联网下载或外部调用。
   - 聊天助手与本地 RESTful 服务（如 `server.py`）自动联动，保障数据安全与隐私。
   - 若需自定义模型路径或扩展配置，可编辑 `.vscode/settings.json`，修改后重启 VSCode 生效。

5. **常见问题与排查建议**
   - 若扩展安装失败，可检查网络代理或使用 `code --list-extensions` 查看已装扩展。
   - 若 AI助手无法识别模型，优先检查 `/GZQ_integrated/models` 路径和模型文件格式。
   - 若 Copilot/Chat 无法连接本地服务，检查 `serverUrl` 配置和 Flask 服务是否已启动。
   - 所有自动化检测、模型加载、API调用均在虚拟环境下运行，避免系统依赖冲突。


## BXDM 文件夹
- BXDM 为后续所有代码、脚本开发的根目录
- AI守护和自动化辅助逻辑由 GZQ_integrated/ai_assistant_full_package_clean 文件夹内的功能模块驱动，BXDM 仅作为你的代码开发区

- 所有 AI 守护、自动化待办、代码规则等均已自动指向 BXDM
## VS Code 推荐扩展
- Python
- Pylance
- Code Runner
- GitLens
- Todo Tree
- 中文语言包
- GitHub Copilot
- Copilot Chat

- Todo Tree
## 自动化依赖与配置补齐
- 脚本会自动检测 BXDM 目录下缺失依赖项和配置，自动安装和设置
- 支持一键补齐 Python、Shell、AI 相关运行环境
- AI助手会根据 GZQ_integrated/ai_assistant_full_package_clean 内的功能模块规则，自动补齐和优化 BXDM 代码区的依赖与配置

## 注意事项
- 如需自定义 AI 服务地址、扩展推荐或自动化规则，可修改 `.vscode/settings.json`
## 如何运行
1. 进入 GZQ 根目录，运行：
   ```bash
   python3 auto_deploy.py
   ```
2. 等待自动部署完成，VS Code 会自动打开 BXDM 目录
3. 按照侧边栏提示，安装/启用推荐扩展
4. 在 BXDM 目录下编写代码，AI 助手可自动扫描、建议、修改和补齐依赖

- 其它历史项目内容已整合至 GZQ_integrated 文件夹

## 问题反馈
如遇自动化部署或开发环境问题，请联系维护者或在 BXDM 目录下新建 issue。

---

### 更新记录

- 2025-09-16：
  - settings.yaml 已扩展为多级规则体系，支持安全、性能、协作、自愈分组，优先级、条件触发、动态更新，前端可启用/禁用和调整规则。
  - 规则与策略模块自动化完成，后续将自动推进推理与任务联动等待办事项。

## VSCode 打开后的详细操作步骤

1. **扩展安装与环境确认**
   - 按照侧边栏提示，安装推荐扩展（如 Python、Pylance、Code Runner、GitLens、Todo Tree、GitHub Copilot、Copilot Chat、中文语言包等）。
   - 确认左下角 Python 环境为自动部署脚本创建的虚拟环境（.venv），如有冲突可在设置中手动切换。
   - 检查 `.vscode/settings.json` 是否已自动配置 AI 服务地址、代码运行环境等。

2. **AI助手联动与智能守护**
   - 在侧边栏或命令面板中打开 Copilot Chat，与 AI助手进行代码问答、自动化建议、依赖补齐等交互。
   - 可直接在 BXDM 目录下编写/修改代码，AI助手会自动扫描、分析并给出优化建议。
   - 支持一键修复、自动补齐依赖、生成测试用例、重构代码等智能操作。

3. **API接口调用与前端联动**
   - 通过 RESTful API（server.py）实现规则管理、结构可视化、协作分派、自愈机制等功能。
   - 推荐使用 Postman、curl、requests、axios 等工具测试 API，或通过 VSCode 插件（如 REST Client）直接调用。
   - 典型接口如 `/ask`（智能问答）、`/rules`（规则管理）、`/structure`（结构可视化）、`/tasks`（协作分派）、`/self_heal`（自愈机制）。

4. **协作分派与团队开发**
   - 通过 `/tasks` 路由分派和查询协作任务，支持多人协作开发。
   - 可在 BXDM 目录下新建 issue 或使用团队协作工具（如 GitHub Projects、Trello）同步任务进度。
   - 任务分派、进度跟踪、自动化待办均可与 AI助手联动。

5. **自动化检测与优化流程**
   - 代码保存后，AI助手会自动触发静态/动态分析、安全/兼容性检测、依赖补齐、性能优化等流程。
   - 检测结果和优化建议会在侧边栏、终端或 Copilot Chat 中展示。
   - 支持一键生成风险报告、修复建议、自动化脚本。

6. **自定义配置与扩展**
   - 可在 `.vscode/settings.json` 中自定义 AI服务地址、扩展推荐、自动化规则等。
   - 支持自定义扫描规则、重构策略、守护策略（编辑 ai_config/config/settings.yaml 或通过 `/rules` 路由动态调整）。
   - 如需扩展新功能模块，可在 GZQ_integrated/ai_config/ 下新增脚本并注册到 dispatcher.py。

7. **常见问题与排查**
   - 如遇依赖安装失败、环境冲突、API不可用等问题，优先查看 `server_dependency.log` 和 VSCode 终端输出。
   - 可通过 `/feedback_log` 路由或直接查阅日志文件定位问题。
   - 如需人工协助，可在 BXDM 目录下新建 issue 或联系维护者。

### 自动部署后的 VSCode 配置检查与优化

- 自动部署脚本会在 `.vscode/settings.json` 中完成如下配置：
  - `python.pythonPath`：已自动指向虚拟环境 `/home/xiedaima/桌面/GZQ/.venv/bin/python`，确保所有 Python 代码运行在隔离环境，避免系统依赖冲突。
  - `ai-assistant.serverUrl`：自动配置为 `http://localhost:5000`，确保 AI助手与本地 RESTful 服务联动。
  - `code-runner.executorMap`：Python 代码运行器已自动指向虚拟环境，支持一键运行脚本。
  - `locale`：设置为 `zh-cn`，界面中文化，便于本地团队协作。
  - `files.autoSave`：自动保存，减少因未保存导致的代码丢失。
  - `extensions.ignoreRecommendations`：关闭扩展忽略，确保推荐扩展自动弹出。

- 检查要点：
  1. 打开 VSCode 后，进入“设置”->“工作区设置”，确认上述配置已生效。
  2. 若 Python 环境未自动切换，可在左下角选择 `.venv` 环境，或在设置中手动指定。
  3. AI助手侧边栏应能正常连接本地服务（如 Copilot Chat），如无法连接请检查 `serverUrl` 是否为本地地址。
  4. 推荐扩展（如 Python、Copilot、GitLens、Todo Tree 等）应自动弹出安装提示，未安装时可手动点击安装。
  5. 代码运行、调试、API调用均应在虚拟环境下进行，避免污染系统环境。
  6. 如需自定义 AI 服务地址、扩展推荐、自动化规则，可直接编辑 `.vscode/settings.json`，修改后重启 VSCode 生效。

- 自动部署保障：
  - 每次运行 `python3 auto_deploy.py`，都会自动覆盖并更新 `.vscode/settings.json`，确保环境、服务、扩展配置始终最新。
  - 若有自定义需求，可在部署后手动调整，后续自动部署会保留关键配置并补齐缺失项。

## 全局兼容与智能守护说明

- 所有自动化部署、路径识别、依赖补齐、模型管理、API服务、协作分派等功能均已推向全局：
  - 项目可在任意父级文件夹下运行，所有路径均自动基于当前脚本目录拼接，无需关心上层目录名称。
  - 自动化检测、智能守护、协作分派、结构可视化、风险报告等功能支持多端联动（VSCode、Web IDE、前端、CLI），无论在哪个入口均可统一调用。
  - 规则体系、模型管理、API接口、团队协作、日志联动等均为全局可用，支持多项目、多团队协同扩展。
  - 支持自定义扩展、自动化规则、AI服务地址，所有配置均可在 `.vscode/settings.json` 或 API 动态调整。
  - 自动化脚本和智能助手会自动检测当前项目结构，补齐缺失依赖、优化环境配置，保障开发区与守护区分离。
  - 所有检测、优化、协作分派、风险报告等流程均可一键触发，支持自动闭环和持续集成。

- 推荐在团队协作、项目迁移、环境重构等场景下优先使用本项目的全局自动化能力，确保开发效率和系统稳定性。

## 功能模板：缓存管理与扩展性优化

### 缓存管理优化

- 提供统一的缓存清理命令或API（如 `python3 utils/memory_cache.py --clear`），支持一键清理所有模块缓存。
- 定期自动检测无效缓存，结合AI自检机制，自动清理冗余数据。
- 支持多端缓存同步，防止协作时缓存冲突。

### 扩展性功能建议

- 插件系统支持热插拔，允许动态加载/卸载AI模型与功能模块，无需重启服务。
- 配置文件（如 settings.yaml）支持分组、优先级和动态更新，便于团队协作和个性化扩展。
- API接口支持自定义扩展，允许用户按需注册新路由或功能。
- 日志与监控模块联动，自动记录扩展行为与异常，便于回溯与优化。
- 提供结构可视化工具，自动展示当前扩展模块与依赖关系，便于维护和扩展。
- 支持多语言和多平台适配，提升跨端兼容性。

## 本地AI部署功能优化说明

- 本项目所有AI模型与服务均默认本地部署，所有推理、健康检查、插件扩展均在本地环境完成。
- 支持多种主流模型格式（如 .gguf、.bin、.pt、.onnx、.h5），自动识别与加载，无需外部云连接。
- 所有API接口、插件系统、结构可视化、缓存管理等功能均为本地优先，保障数据隐私与算力利用。
- 配置文件（settings.yaml）支持本地分组、优先级与动态更新，团队成员可个性化扩展本地功能。
- 日志与监控模块自动记录本地扩展行为与异常，便于回溯与优化。
- 结构可视化工具自动扫描本地项目结构与依赖，支持本地前端展示。

### 容器与云平台功能预留（可选扩展）

- 项目预留 Dockerfile、Kubernetes 配置入口，支持后续容器化部署（默认不开启）。
- 云平台相关功能（如自动化云部署、云监控、云存储）仅作为可选扩展，默认不启用。
- 如需启用容器或云平台功能，可在 config/settings.yaml 中设置 `enable_container: true` 或 `enable_cloud: true`，并补充相关配置。
- 所有云端扩展均需用户主动配置并授权，默认不连接任何外部AI或云服务。

---

## AI 文件夹内容与功能说明

### AI/ai_assistant_full_package/
- config/settings.yaml：AI助手全局配置文件，支持模型分组、优先级、插件动态更新、API路由分组等，便于多模型、多插件、多服务场景灵活扩展。

### AI/utils/
- github_sync.py：GitHub 协作同步工具，支持自动同步 issue、PR、任务分派与消息推送，可用于团队协作自动化。
- memory_cache.py：智能缓存管理工具，支持缓存清理、自检、异常文件检测与自动修复，保障系统稳定运行。
- self_heal.py：智能建议与自愈机制工具，自动生成代码优化建议、一键修复常见问题（如 print 替换为日志）、自动回滚，提升代码质量与安全性。

---

## BXDM 文件夹独立说明与自动化配置

BXDM 文件夹为你的专属代码开发区，所有业务逻辑、项目脚本、功能模块均可在此自由创建和管理，AI守护区不会自动修改此目录结构。

- `/home/xiedaima/桌面/GZQ/BXDM/auto_vscode_setup.py`：一键自动配置 VSCode 扩展与 AI 交互环境，运行后会自动生成 `.vscode/settings.json` 和 `.vscode/extensions.json`，推荐扩展包括 Code Runner、Python、GitLens、Todo Tree、中文语言包等，AI助手服务地址自动写入，支持自动保存、中文界面、Python环境自动适配。
- `/home/xiedaima/桌面/GZQ/BXDM/README.md`：开发区专属说明文档，建议补充你的项目说明、使用方法、接口文档、开发建议等，便于团队协作和维护。

使用流程：
1. 运行 `/home/xiedaima/桌面/GZQ/auto_deploy.py` 完成环境初始化和依赖安装。
2. 在 VSCode 中打开 BXDM 文件夹，运行 `python auto_vscode_setup.py`，自动完成扩展推荐和 AI 交互窗口配置。
3. 按需创建主脚本、功能模块、数据文件、测试脚本等，所有开发内容均可在 BXDM 内自由扩展。
4. 推荐在 BXDM/README.md 内补充项目说明和接口文档。

BXDM 文件夹可自由命名和扩展，建议保持结构清晰，支持多语言界面和文档，国际化与本地化自动适配。

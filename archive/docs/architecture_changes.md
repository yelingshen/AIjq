# Architecture changes & functional suggestions (draft)

目标：给出逐步、安全的改进建议以把当前代理/包装器策略演进为更长期、可维护的结构。

1) 恢复或重构 `ai/model_loader.py`（高优先级）
   - 现在已用 stub 覆盖以通过静态检查。建议：在受控 venv 中运行完整测试后，将经过验证的原始实现或更模块化版本恢复到 `ai/model_loader.py`，并编写单元测试覆盖关键加载/推理路径。

2) 逐步替换运行时 runpy 代理为直接模块导入（中优先级）
   - 当前 `utils/*`、`scanners/*`、`services/*` 多处使用 runpy 或 importlib 做运行时代理，优点是低风险迁移；缺点是可维护性较差、调试不便。
   - 建议：对常用模块（report_generator、structure_visualizer、memory_cache 等）改为正常包/模块结构并直接 import。为此需要统一项目根路径和 package 名称（例如将 `ai` 设为 package 并添加 `pyproject.toml`/`setup.cfg` 以支持可编辑安装）。

3) 统一配置管理（中优先级）
   - 创建 `config/` 或 `ai/config.py` 统一读取环境变量与 YAML/JSON 配置文件，避免代码中散落的路径常量。

4) 增加 CI 的 import-only 检查（低风险、立即可做）
   - 我已准备好将 `scripts/verify_imports.py` 在 GitHub Actions 中运行，以在 PR 时早期发现破坏性改动。

5) 模型后端适配策略（长期）
   - 明确支持列表（torch/transformers, onnxruntime, pygpt4all, diffusers 等），并为每一种后端写一个适配器类（Factory pattern），以减小模型后端切换成本。

6) 文档和示例（立刻执行）
   - 把 `scripts/RUN_VALIDATION.md`、deployment README 中的运行时验证示例保持最新，提供端点测试脚本和 sample model files 位置（如果无法分发模型，提供下载或转换脚本）。

风险与回滚：

- 如果要替换代理实现，建议分小步进行并在 CI 中增加回滚检测（merge 前跑导入检查 + 简单端点 smoke-test）。

下一步动作建议：

- 我可以把 `scripts/verify_imports.py` 加入到 GitHub Actions 工作流草案（`.github/workflows/import_check.yml`），如果你同意我会继续创建该文件草案。

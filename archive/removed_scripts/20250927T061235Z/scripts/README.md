# scripts/

此目录用于存放已迁移的根级脚本（原先位于仓库根的脚本已迁移到此处），目的是把脚本组织到更清晰的子目录以便部署与 CI。

已迁移：
- `auto_deploy.py` -> `scripts/auto_deploy.py`（主部署脚本，包含 dry-run、venv 创建、依赖安装与打包步骤）

快速入门（静态检查）：

1. 在项目根运行导入烟雾测试（不安装第三方依赖）：

```bash
python3 scripts/verify_imports.py
```

2. 查看生成的报告： `scripts/import_report.json`（记录哪些模块在当前环境可被导入，哪些依赖缺失需要运行时安装）。

示例：如果 `ai.server` 报错 "No module named 'flask'"，请在 venv 中安装 Flask 并重试。

运行时验证（参见 scripts/RUN_VALIDATION.md）包含启动 minimal/full 服务器和端点 smoke-tests 的流程。

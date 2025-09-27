README — 部署指南 (Deployment)
=================================

快速概览
---------

- 应用类型：Python FastAPI 服务（生产使用 Gunicorn + Uvicorn workers）。

- 额外组件：可选 Docker、nginx 反向代理、systemd 服务文件已在 `deployment/`。

- VS Code 扩展（如果需要）可用 `scripts/package_vsix.sh` 打包为 VSIX。

Systemd + Gunicorn (推荐生产)
------------------------------

1. 在目标服务器上创建部署目录，例如 `/opt/yeling-ai`，并将代码放入其中。

2. 创建并激活虚拟环境：

   python3 -m venv /opt/yeling-ai/venv

   source /opt/yeling-ai/venv/bin/activate

3. 安装依赖：

   pip install -r deployment/requirements.txt

4. systemd 单元：`deployment/gunicorn.service`（示例已包含）。启用并启动：

   sudo cp deployment/gunicorn.service /etc/systemd/system/yeling-ai.service

   sudo systemctl daemon-reload

   sudo systemctl enable --now yeling-ai.service

Uvicorn (开发/轻量生产)
-----------------------

使用 `scripts/run_uvicorn.sh` 启动（或直接运行 `uvicorn ai.server_fastapi:app --host 0.0.0.0 --port 8000`）。

Docker
------

- 参见 `Dockerfile` 与 `docker-compose.yml`。在容器中运行时，确保把 host 的端口映射到容器的 8000/5000（取决于配置）。

CI / Tests
----------

- GitHub Actions 工作流文件位于 `.github/workflows/`，主要包含 CI、Docker Build、VSIX 打包与发布等。

- 在本地运行测试：

  python -m pytest -q

Linting
-------

- 项目使用 `ruff`（配置在 `.trunk/configs/ruff.toml`），也可使用 `black`/`isort` 进行格式化。

回滚策略
--------

- 对仓库更改：可以通过 `git revert <commit>` 回滚单次 commit。

- 若需要彻底从历史中移除大文件，请使用 `git-filter-repo` 或 BFG（注意：会重写历史并需要强制推送）。

变更与归档记录
----------------

- 重复文件已被移动到 `archive/removed_scripts/`，以便审计和恢复。

疑难排查
--------

- 如果 systemd 启动失败，检查 `sudo journalctl -u yeling-ai.service -b`。

- 如果依赖安装失败，确认 Python 版本和 `pip` 的目标虚拟环境路径。

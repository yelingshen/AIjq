Yeling-AI — 一键上手说明（中文）
=================================

本文件为项目的最终中文说明。将本仓库解压到任意目录后，请先阅读 "快速开始" 部分，按步骤操作即可在本地构建并运行后端与 VS Code 扩展。

快速开始（最短路径）
--------------------
1. 解压包并进入目录：

   unzip final_package.zip -d yeling-ai && cd yeling-ai

2. Python 环境与依赖：

   python3 -m venv .venv
   =================================

   本文件为项目的最终中文说明。将本仓库解压到任意目录后，请先阅读 "快速开始" 部分，按步骤操作即可在本地构建并运行后端与 VS Code 扩展。

   快速开始（最短路径）
   --------------------

   1. 解压包并进入目录：

      unzip final_package.zip -d yeling-ai && cd yeling-ai

   2. Python 环境与依赖：

      python3 -m venv .venv
      source .venv/bin/activate
      pip install -r deployment/requirements.txt

   3. 构建并安装 VS Code 扩展（可选，若只需后端则跳过）：

      npm ci
      npm run compile

      ```bash
      # 本地打包为 .vsix（可直接在 VS Code 中安装）
      npx vsce package
      ```

   4. 运行后端（快速本地方式）：

      ```bash
      # 最小化本地启动脚本（项目包含 start_minimal.py）
      python3 deployment/start_minimal.py
      ```

      如果需要使用 Uvicorn（开发模式）：

      uvicorn ai.server:app --reload --host 0.0.0.0 --port 8000

   部署到生产（建议）
   -------------------

    - 使用系统级虚拟环境或容器。

      仓库中包含以下示例/模板文件：

      - `deployment/gunicorn.service`
      - `Dockerfile`
      - `docker-compose.yml`

    - 推荐使用 Gunicorn + Uvicorn workers，在 systemd 中运行类似命令：

       ```bash
       gunicorn -k uvicorn.workers.UvicornWorker 'ai.server:app' -w 4 -b 0.0.0.0:8000
       ```

   如何还原 archive 中被移除的文件
   -------------------------------

   项目把重复或历史文件移动到了 `archive/` 目录以避免与当前代码冲突。如果你需要恢复某些文件：

   1. 查看归档目录：

      ls -la archive/removed_duplicates

   2. 手动还原（示例）：

      mkdir -p restored_backup
      cp -r archive/removed_duplicates/20251002T102855Z/restored_filename restored_backup/

   3. 如果需要把某些文件重新纳入项目，请在恢复后运行 `git add` 并提交。

   包中包含的文件（重要项）
   -------------------------

   - `ai/`：后端源码（若存在）。

   - `deployment/`：部署脚本与 systemd 单元、requirements 文件。

   - `src/`, `out/`：VS Code 扩展源码与编译产物（如存在）。

   - `scripts/`：维护脚本（扫描、去重、合并候选等）。

   - `deleted_files_full_archive.zip`：本次清理中被移除/归档的全部文件备份，放在仓库根，可用于回滚或审计。

   如何立即验证（快速 smoke-test）
   -------------------------------

   1. 启动后端（见上），打开浏览器访问 http://localhost:8000/docs 查看 API 文档（如果使用 FastAPI）。

   2. 在 VS Code 中安装本地生成的 `*.vsix`，激活扩展并在扩展面板中查看可用命令（如果打包成功）。

   恢复与回滚注意事项
   -------------------

    - 我们已在仓库根生成 `full_backup_before_prune.zip`（完整备份），以及 `deleted_files_full_archive.zip`（仅归档内容）。在执行任何破坏性清理前请保留这些备份。

    - 若你希望我现在把仓库裁剪为只保留 `final_package.zip`，请明确回复“继续裁剪”。

       我会先生成 `final_package.zip` 并创建 SHA256 校验，然后执行裁剪。

       注意：裁剪是不可逆的操作，请确保 `full_backup_before_prune.zip` 已安全保存。

   联系方式与后续建议
   --------------------

   - 推荐添加一个 GitHub Actions CI 工作流来自动运行 lint 与测试，并在合并时生成 VSIX 与 release zip。

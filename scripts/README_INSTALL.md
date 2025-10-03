Yeling-AI 可移动安装包说明

内容：
- `final_package.zip`：项目主包，包含 `README_FINAL.md`、`scripts/`、`deployment/`、`src/`、`ai/` 等
- `scripts/checksums_SHA256.txt`：SHA256 校验，便于在目标机器核对包完整性
- `scripts/pack_and_verify_log.txt`：打包时的文件列单预览，便于审计
- `scripts/install_package.sh`：交互式安装脚本，支持创建 venv、安装 `deployment/requirements.txt`，并可选择创建 systemd 服务

安装流程（目标机器）：
1. 将 `yeling-ai-installer.tar.gz` 复制到目标机器并解压：

   tar -xzf yeling-ai-installer.tar.gz

2. 可选：校验 SHA256（建议）：

   sha256sum -c scripts/checksums_SHA256.txt

3. 运行安装脚本（需要 sudo 或 root）：

   sudo ./scripts/install_package.sh /opt/yeling-ai --enable-service

4. 安装完成后：查看 `/opt/yeling-ai/install_done.txt` 获取安装摘要。

注意事项：
- 目标机器需安装 Python 3.10+；若需构建 VS Code 扩展，还需安装 Node.js 与 npm。
- systemd 启用步骤需要 root 权限。
- 本包包含归档的历史文件以便回滚；若不需要可在安装后删除 `archive/`。

### 新增功能说明

#### 系统依赖检查

安装脚本会自动检查以下依赖：

- Python 3.10+（必需）
- Node.js 和 npm（可选，用于构建 VS Code 扩展）
- Docker（可选，用于容器化部署）
- systemd（可选，用于服务管理）

若缺少必需依赖，脚本会提示并终止安装。

#### 健康检查

安装完成后，脚本会运行健康检查脚本 `health_check.sh`，验证服务是否正常运行。

- 默认检查地址：`http://localhost:8000`
- 若服务未正常运行，脚本会提示警告。

#### 示例命令

- 干运行模式（不做实际修改）：

  ```bash
  sudo ./scripts/install_package.sh --dry-run
  ```

- 指定目标目录和端口：

  ```bash
  sudo ./scripts/install_package.sh --target /custom/path --port 8080
  ```

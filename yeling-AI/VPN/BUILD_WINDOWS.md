Windows 打包说明 (PyInstaller)

目标：把项目打包成单个 exe 文件，便于在没有 Python 环境的 Windows 机器上分发。

准备
- 在 Windows 上或者在 Windows 虚拟机/容器中执行下列步骤（建议使用与目标机器相同的 Windows 版本）。
- 安装 Python 3.10/3.11（与开发时一致），并确保 `python` 在 PATH 中。
- 创建并激活虚拟环境：

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

- 安装依赖（只需运行时依赖）：

```powershell
python -m pip install -r multi_tool\requirements.txt
python -m pip install pyinstaller
```

打包命令（单文件）
- 在仓库根（含 `launcher.py`）运行：

```powershell
pyinstaller --onefile --name multi_tool.exe launcher.py
```

产出
- 可执行文件位于 `dist\multi_tool.exe`。

常见注意事项
- GUI/Tkinter：如果使用 GUI（`file-helper` 或 `vpn-router` GUI），确保目标系统安装有适当的 GUI 运行时（Windows 自带 Tk 支持，但某些精简系统可能缺失）。
- 本地文件/模板：若代码使用模板或静态文件（例如 HTML_TEMPLATE），PyInstaller 通常会自动包含被 import 的模块内的字符串，但如果存在外部模板文件，需通过 `--add-data` 明确包含。
- 可执行打包时会丢失对系统外部命令（如 `sudo`, `piactl`, `xvpn_linux_amd64`）的能力；这些功能在 Windows 上需替换为等价的 Windows 命令或在运行文档中说明。
- 临时目录：ORchestrator 的锁路径已被改为使用临时目录，保证 Windows 上也能工作。

调试
- 运行时出现缺少模块错误时，可使用 `--hidden-import <module>` 来强制包含。
- 若 exe 启动失败，使用 `pyinstaller --onedir launcher.py` 先生成可展开的目录版，便于排查哪些文件缺失。

分发
- 若需安装程序体验，可将 `dist\multi_tool.exe` 打包到安装器（例如 Inno Setup）或只单独分发 exe。

安全
- 请不要将私钥/机密等写死进可执行文件中。构建过程应从安全位置读取运行时所需的密钥/配置（例如通过用户提供的 license 文件）。

#!/usr/bin/env python3
import os
import subprocess
import threading
import tempfile
import shutil
import atexit
import webbrowser

from .modules import dependencies, file_detect, sandbox_run, logger


HTML_TEMPLATE = """
<html>
<head><meta charset="utf-8"><title>单文件助手 CLI 操作</title></head>
<body>
<h1>可执行文件操作</h1>
<ul>
{% for exe in executables %}
<li>{{ exe }} <button onclick="fetch('/run?cmd={{ exe|urlencode }}').then(r=>r.text()).then(alert)">执行</button></li>
{% endfor %}
</ul>
</body>
</html>
"""


def run_server(port=5000):
    # import Flask lazily to avoid hard requirement at package import time
    from flask import Flask, render_template_string, request
    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template_string(HTML_TEMPLATE, executables=globals().get('EXECUTABLES', []))

    @app.route("/run")
    def run_cmd():
        cmd = request.args.get("cmd")
        use_wine = cmd.endswith((".exe", ".bat", ".cmd"))
        try:
            if use_wine:
                subprocess.Popen(["wine64", cmd])
            else:
                subprocess.Popen([cmd])
            return f"{cmd} 已执行"
        except Exception as e:
            return f"执行失败: {e}"

    app.run(port=port, debug=False)


def rollback(tmp_dir, installed_deps):
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir, ignore_errors=True)
        logger.log("回退: 清理临时目录")
    if installed_deps:
        try:
            subprocess.run(["sudo", "apt", "remove", "--purge", "-y"] + installed_deps)
            logger.log(f"回退: 卸载依赖 {installed_deps}")
        except Exception:
            logger.log("回退: 卸载依赖时出错")


def open_settings_window():
    import tkinter as _tk
    from tkinter import ttk
    from .. import settings as _settings
    win = _tk.Toplevel()
    win.title('设置')
    win.geometry('400x300')
    frm = ttk.Frame(win, padding=10)
    frm.pack(fill='both', expand=True)

    cfg = _settings.load_settings()

    ttk.Label(frm, text='通用设置（占位）').pack(anchor='w')
    var_enable_vdev = _tk.BooleanVar(value=cfg.get('enable_virtual_device', False))
    ttk.Checkbutton(frm, text='启用虚拟设备管理', variable=var_enable_vdev).pack(anchor='w')

    def _save():
        cfg['enable_virtual_device'] = bool(var_enable_vdev.get())
        _settings.save_settings(cfg)
        ttk.Button(frm, text='已保存').pack()
        win.destroy()

    ttk.Button(frm, text='保存', command=_save).pack(side='right', pady=10)


def run_gui():
    """Interactive entrypoint for the File Helper GUI.

    This function will run the GUI flow (file selection, dependency checks, and start the local report server).
    """
    # prepare environment
    tmp_dir = tempfile.mkdtemp()
    installed_deps = []

    # register rollback on exit
    atexit.register(rollback, tmp_dir, installed_deps)

    dependencies.check_minimal()

    import tkinter as _tk
    from tkinter import filedialog as _fd, messagebox as _mb, ttk as _tt
    _root = _tk.Tk()
    _root.title('文件助手')
    _root.geometry('600x120')

    # Main menu frame
    main_frame = _tt.Frame(_root, padding=10)
    main_frame.pack(fill='both', expand=True)

    _tt.Label(main_frame, text='单文件助手').grid(row=0, column=0, sticky='w')
    _tt.Button(main_frame, text='选择文件并启动服务器', command=lambda: _start_file_flow(_root)).grid(row=1, column=0, pady=8)
    _tt.Button(main_frame, text='打开设置', command=open_settings_window).grid(row=1, column=1, pady=8)
    _tt.Button(main_frame, text='运行子功能', command=lambda: _open_actions_dialog(_root)).grid(row=1, column=2, pady=8)

    _root.mainloop()


def _start_file_flow(_root):
    # File selection and server start flow extracted for button callback
    import tkinter as _tk
    from tkinter import filedialog as _fd, messagebox as _mb
    target = _fd.askopenfilename(title="选择要处理的文件")
    if not target:
        _mb.showerror("错误", "未选择文件")
        return
    ext = file_detect.detect_ext(target)
    is_exec = os.access(target, os.X_OK)
    if ext in ["exe", "bat", "cmd"]:
        pkgs = ["wine64", "winetricks"]
    elif is_exec or ext in ["run", "sh", "bin", "elf"]:
        pkgs = ["bash", "coreutils"]
    else:
        pkgs = dependencies.get_packages_for_ext(ext)

    try:
        dependencies.install_if_missing(pkgs)
    except Exception:
        _mb.showerror("错误", "依赖安装失败")
        return

    # expose executables to the web UI
    globals()['EXECUTABLES'] = [target]

    # Start the simple local report server
    threading.Thread(target=run_server, daemon=True).start()
    webbrowser.open("http://127.0.0.1:5000")


def _open_actions_dialog(root):
    import tkinter as _tk
    from tkinter import ttk as _tt, messagebox as _mb
    from .. import actions as _actions

    win = _tk.Toplevel(root)
    win.title('运行子功能')
    win.geometry('420x320')
    frm = _tt.Frame(win, padding=8)
    frm.pack(fill='both', expand=True)

    actions = _actions.list_actions()
    vars = {}

    for i, (name, (_, desc)) in enumerate(actions.items()):
        var = _tk.BooleanVar(value=False)
        vars[name] = var
        _tt.Checkbutton(frm, text=f"{name} - {desc}", variable=var).pack(anchor='w')

    def _run_selected():
        selected = [n for n, v in vars.items() if v.get()]
        if not selected:
            _mb.showwarning('提示', '未选择任何子功能')
            return
        for n in selected:
            try:
                _actions.run_action(n)
            except Exception as e:
                _mb.showerror('错误', f'运行 {n} 失败: {e}')
        _mb.showinfo('完成', '所选操作已执行（详见控制台）')

    _tt.Button(frm, text='运行所选', command=_run_selected).pack(pady=10)


if __name__ == '__main__':
    run_gui()

try:
    from ..actions import action as _action_decorator

    @_action_decorator('file_helper.start', description='启动文件助手 GUI', admin_only=False, supports_dry_run=False)
    def _file_helper_start(dry_run=False, params=None):
        if dry_run:
            print('[Dry-Run] file_helper.start')
            return
        return run_gui()
except Exception:
    pass

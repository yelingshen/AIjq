import subprocess
from . import logger
import os

def maybe_sandbox_run(file_path, use_wine=False):
    if not use_wine and os.path.isfile(file_path):
        try:
            os.chmod(file_path, 0o755)
        except Exception as e:
            logger.log(f"权限设置失败: {file_path} => {e}")

    # delay GUI import until needed
    try:
        import tkinter as tk
        from tkinter import messagebox
    except Exception:
        # if tkinter not available, just run without confirmation
        try:
            if use_wine:
                subprocess.Popen(["wine64", file_path])
            else:
                subprocess.Popen([file_path])
            logger.log(f"执行文件 (no-GUI): {file_path}")
        except Exception as e:
            logger.log(f"执行失败: {file_path} => {e}")
        return

    root = tk.Tk()
    root.withdraw()
    if messagebox.askyesno("确认", f"是否执行 {file_path}?"):
        try:
            if use_wine:
                subprocess.Popen(["wine64", file_path])
            else:
                subprocess.Popen([file_path])
            logger.log(f"执行文件: {file_path}")
        except Exception as e:
            logger.log(f"执行失败: {file_path} => {e}")
            messagebox.showerror("执行失败", f"{file_path} 执行失败: {e}")

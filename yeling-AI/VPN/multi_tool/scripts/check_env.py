#!/usr/bin/env python3
"""环境检查脚本：跨平台基本依赖检测和建议修复步骤

- 检查 Python 版本
- 检查 pip, git
- 检查可选工具（docker, node）并报告

退出码：0 = OK, 非0 = 有问题
"""
import sys
import subprocess
import shutil

REQ_TOOLS = ["python3", "pip3", "git"]
OPTIONAL_TOOLS = ["docker", "node"]


def check_tool(cmd):
    path = shutil.which(cmd)
    if path:
        try:
            subprocess.run([cmd, "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
    return path is not None


def main():
    ok = True
    # python version
    if sys.version_info < (3, 8):
        print("ERROR: Python 3.8+ is required")
        ok = False
    else:
        print(f"Python OK: {sys.version}")

    for t in REQ_TOOLS:
        if not check_tool(t):
            print(f"MISSING: {t}")
            ok = False
        else:
            print(f"Found: {t}")

    for t in OPTIONAL_TOOLS:
        if not check_tool(t):
            print(f"Optional missing: {t} (recommended)")
        else:
            print(f"Found optional: {t}")

    if not ok:
        print("One or more required tools missing. See messages above.")
        sys.exit(2)
    print("Environment looks OK for basic operations.")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
GZQ CLI 工具：支持一键自检、规则查询、结构导出等命令，自动联动 RESTful API。
"""
import sys, requests, json
import os
import sys
from pathlib import Path

# 获取当前脚本所在目录
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
API_BASE = "http://127.0.0.1:5000"

def print_json(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))

def main():
    if len(sys.argv) < 2:
        print("用法: cli.py [self_check|rules|structure|tasks|report|model_check] [参数]")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "self_check":
        r = requests.post(f"{API_BASE}/self_heal", json={})
        print_json(r.json())
    elif cmd == "rules":
        r = requests.get(f"{API_BASE}/rules")
        print_json(r.json())
    elif cmd == "structure":
        r = requests.get(f"{API_BASE}/structure")
        print_json(r.json())
    elif cmd == "tasks":
        r = requests.get(f"{API_BASE}/tasks")
        print_json(r.json())
    elif cmd == "report":
        r = requests.get(f"{API_BASE}/report")
        if r.status_code == 200:
            print(r.text)
        else:
            print_json(r.json())
    elif cmd == "model_check":
        r = requests.get(f"{API_BASE}/model_check")
        print_json(r.json())
    else:
        print(f"未知命令: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()

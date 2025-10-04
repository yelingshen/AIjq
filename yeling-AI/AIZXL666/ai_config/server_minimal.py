import os
import sys
from pathlib import Path

# 获取当前脚本所在目录
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return 'Flask Minimal Server Running!'

if __name__ == '__main__':
    print('[DEBUG] 启动最简 Flask 服务')
    app.run(port=5000)

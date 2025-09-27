
import os
import sys
import subprocess
import json

# 获取当前BXDM目录和父级目录
BXDM_PATH = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BXDM_PATH, '..'))

# 检查父级目录AI服务
def find_ai_service():
	ai_paths = [
		os.path.join(PROJECT_ROOT, 'GZQ_integrated', 'ai_config', 'server.py'),
		os.path.join(PROJECT_ROOT, 'AI', 'ai_assistant_full_package', 'server.py'),
	]
	for path in ai_paths:
		if os.path.exists(path):
			return path
	return None

ai_service_path = find_ai_service()
if ai_service_path:
	print(f'[INFO] 检测到本地AI服务: {ai_service_path}')
	ai_server_url = 'http://localhost:5000'
else:
	print('[WARN] 未检测到本地AI服务，部分功能可能不可用')
	ai_server_url = ''

# 补齐 .vscode/settings.json
vscode_dir = os.path.join(BXDM_PATH, '.vscode')
os.makedirs(vscode_dir, exist_ok=True)
settings_path = os.path.join(vscode_dir, 'settings.json')
settings = {
	"python.pythonPath": sys.executable,
	"ai-assistant.serverUrl": ai_server_url,
	"code-runner.executorMap": {"python": sys.executable},
	"locale": "zh-cn",
	"files.autoSave": "afterDelay",
	"extensions.ignoreRecommendations": False
}
if os.path.exists(settings_path):
	with open(settings_path, 'r', encoding='utf-8') as f:
		try:
			old = json.load(f)
		except Exception:
			old = {}
	old.update(settings)
	settings = old
with open(settings_path, 'w', encoding='utf-8') as f:
	json.dump(settings, f, ensure_ascii=False, indent=2)
print('[INFO] VSCode settings.json 已补齐')

# 补齐 .vscode/extensions.json
extensions_path = os.path.join(vscode_dir, 'extensions.json')
recommend = [
	"formulahendry.code-runner",
	"ms-ceintl.vscode-language-pack-zh-hans",
	"ms-python.python",
	"ms-vscode.gitlens",
	"Gruntfuggly.todo-tree",
	"GitHub.copilot",
	"GitHub.copilot-chat",
	"ms-python.vscode-pylance"
]
exts = {"recommendations": recommend}
if os.path.exists(extensions_path):
	try:
		with open(extensions_path, 'r', encoding='utf-8') as f:
			old_exts = json.load(f)
		if 'recommendations' in old_exts:
			for ext in recommend:
				if ext not in old_exts['recommendations']:
					old_exts['recommendations'].append(ext)
			exts = old_exts
	except Exception:
		pass
with open(extensions_path, 'w', encoding='utf-8') as f:
	json.dump(exts, f, ensure_ascii=False, indent=2)
print('[INFO] VSCode extensions.json 已补齐')

# 自动安装推荐扩展
for ext in recommend:
	print(f'[INFO] 安装扩展: {ext}')
	subprocess.run(['code', '--install-extension', ext])

# 检查AI服务是否已启动
import socket
def check_server(port=5000):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		s.connect(('127.0.0.1', port))
		s.close()
		return True
	except Exception:
		return False

if ai_server_url and not check_server(5000):
	print('[WARN] 本地AI服务未启动，请在父级目录运行 server.py 或 start_ai_assistant.py')
else:
	print('[INFO] 本地AI服务已启动，可在 VSCode 聊天窗口直接交互')

print('[SUCCESS] BXDM 自动化配置与扩展部署完成，可直接体验本地AI聊天助手！')

import sys
import locale
import platform
from flask import Flask, jsonify, request

app = Flask(__name__)

def get_system_info():
    info = {
        'os': platform.system(),
        'os_version': platform.version(),
        'python_version': platform.python_version(),
        'locale': locale.getdefaultlocale()[0],
        'encoding': locale.getpreferredencoding(),
        'arch': platform.machine()
    }
    return info

def is_supported_language(lang_list):
    sys_lang = locale.getdefaultlocale()[0]
    return sys_lang in lang_list

def is_supported_platform(platform_list):
    sys_platform = platform.system()
    return sys_platform in platform_list

@app.route('/system_info', methods=['GET'])
def get_system_info_api():
    info = get_system_info()
    return jsonify(info)

@app.route('/supported_languages', methods=['GET'])
def get_supported_languages():
    langs = ['zh_CN', 'en_US', 'ja_JP', 'fr_FR']
    return jsonify({'supported_languages': langs, 'current': locale.getdefaultlocale()[0]})

@app.route('/switch_language', methods=['POST'])
def switch_language():
    data = request.get_json()
    lang = data.get('lang')
    # 实际切换逻辑需结合前端或配置文件
    return jsonify({'message': f'已切换到语言: {lang}'})

if __name__ == '__main__':
    info = get_system_info()
    print('系统信息:', info)
    print('支持中文:', is_supported_language(['zh_CN', 'zh_TW']))
    print('支持Linux:', is_supported_platform(['Linux']))

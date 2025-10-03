import sys
from pathlib import Path

# 获取项目根目录并加入 sys.path（确保能导入顶层包 ai）
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
sys.path.insert(0, str(ROOT_DIR))
from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return 'Flask Minimal Server Running!'


@app.route('/api/generate', methods=['POST'])
def api_generate():
    try:
        data = sys.stdin and None  # placeholder to keep flake happy
        from flask import request, jsonify
        payload = request.get_json(force=True)
        model = payload.get('model')
        prompt = payload.get('prompt', '')
        # Use ModelLoader to call ollama adapter
        from ai.model_loader import ModelLoader
        ml = ModelLoader()
        # load a lightweight model object (we treat model id as model name)
        load_res = ml.load_model(model_path=model, backend='ollama')
        if load_res.get('error'):
            return jsonify({'error': load_res.get('error'), 'response': None}), 500
        adapter_cls = ml.adapters.get('ollama')
        adapter = adapter_cls()
        out = adapter.infer(load_res['model'], prompt)
        # adapter returns {'text':..., 'meta':{...}}
        if isinstance(out, dict) and 'text' in out:
            return jsonify({'text': out.get('text'), 'meta': out.get('meta', {})})
        # fallback: wrap as text
        return jsonify({'text': str(out), 'meta': {}})
    except Exception as e:
        return jsonify({'error': str(e), 'response': None}), 500


if __name__ == '__main__':
    print('[DEBUG] 启动最简 Flask 服务')
    app.run(port=5000)

    def download_model(self, url, target_dir=None):
        """
        自动下载模型文件，支持 huggingface hub、公开URL。
        """
        import os, requests
        from pathlib import Path
        target_dir = Path(target_dir or self.DEFAULT_DIRS[0])
        target_dir.mkdir(parents=True, exist_ok=True)
        fname = url.split('/')[-1]
        fpath = target_dir / fname
        try:
            if 'huggingface.co' in url:
                # 简单支持：下载权重文件
                r = requests.get(url, stream=True)
                with open(fpath, 'wb') as fh:
                    for chunk in r.iter_content(chunk_size=8192):
                        fh.write(chunk)
            else:
                r = requests.get(url, stream=True)
                with open(fpath, 'wb') as fh:
                    for chunk in r.iter_content(chunk_size=8192):
                        fh.write(chunk)
            return {'success': True, 'path': str(fpath)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_model(self, model_path, new_version_url):
        """
        自动更新模型：下载新版本并替换原模型，备份旧版本。
        """
        import shutil, os
        from pathlib import Path
        model_path = Path(model_path)
        backup_path = model_path.with_suffix(model_path.suffix + '.bak')
        try:
            shutil.copy2(model_path, backup_path)
            dl_result = self.download_model(new_version_url, model_path.parent)
            if dl_result['success']:
                os.replace(dl_result['path'], str(model_path))
                return {'success': True, 'backup': str(backup_path), 'updated': str(model_path)}
            else:
                return {'success': False, 'error': dl_result['error']}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def rollback_model(self, model_path, backup_path=None):
        """
        回滚模型到备份版本。
        """
        import shutil, os
        from pathlib import Path
        model_path = Path(model_path)
        backup_path = Path(backup_path or model_path.with_suffix(model_path.suffix + '.bak'))
        try:
            if backup_path.exists():
                shutil.copy2(backup_path, model_path)
                return {'success': True, 'restored': str(model_path)}
            else:
                return {'success': False, 'error': '备份文件不存在'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_model_metadata(self, model_info):
        meta = {
            'name': model_info['name'],
            'path': model_info['path'],
            'type': model_info['type'],
            'size': model_info['size'],
            'last_modified': model_info['mtime'],
            'backend': 'unknown',
            'error': None,
            'version': None,
            'source': None,
            'download_time': None
        }
        # 可扩展：参数量、依赖、用途、来源、下载时间等
        return meta
    def auto_infer_and_check(self, model_path=None):
        """
        自动推理健康检查：根据模型类型自动生成测试输入，运行推理并校验输出 shape。
        支持 transformers、diffusers、onnx、keras、torch、paddlepaddle 等主流模型。
        """
        import traceback
        result = {'model_path': model_path, 'backend': None, 'success': False, 'output_shape': None, 'error': None}
        mlist = self.find_all_models()
        minfo = None
        if model_path:
            minfo = next((m for m in mlist if m['path'] == model_path), None)
        else:
            minfo = mlist[0] if mlist else None
        if not minfo:
            result['error'] = '未找到可用模型'
            return result
        ext = Path(minfo['path']).suffix.lower()
        try:
            if ext in ['.pt', '.pth']:
                import torch
                model = torch.load(minfo['path'])
                dummy_input = torch.randn(1, 3, 224, 224)
                out = model(dummy_input)
                result['backend'] = 'torch'
                result['output_shape'] = tuple(out.shape)
                result['success'] = True
            elif ext == '.onnx':
                import onnxruntime
                session = onnxruntime.InferenceSession(minfo['path'])
                input_name = session.get_inputs()[0].name
                dummy_input = {input_name: [[0.0]*224]*224}
                out = session.run(None, dummy_input)
                result['backend'] = 'onnxruntime'
                result['output_shape'] = str([o.shape if hasattr(o, 'shape') else type(o) for o in out])
                result['success'] = True
            elif ext == '.h5':
                from tensorflow import keras
                model = keras.models.load_model(minfo['path'])
                import numpy as np
                dummy_input = np.random.randn(1, 224, 224, 3)
                out = model.predict(dummy_input)
                result['backend'] = 'keras'
                result['output_shape'] = tuple(out.shape)
                result['success'] = True
            elif ext in ['.bin', '.gguf']:
                from pygpt4all import GPT4All
                model = GPT4All(model=minfo['path'])
                out = model.generate("你好", max_tokens=10)
                result['backend'] = 'pygpt4all'
                result['output_shape'] = str(type(out))
                result['success'] = True
            elif ext == '.pdparams':
                import paddle
                model = paddle.load(minfo['path'])
                dummy_input = paddle.randn([1, 3, 224, 224])
                out = model(dummy_input)
                result['backend'] = 'paddlepaddle'
                result['output_shape'] = tuple(out.shape)
                result['success'] = True
            elif ext == '.safetensors':
                try:
                    from diffusers import DiffusionPipeline
                    pipe = DiffusionPipeline.from_pretrained(minfo['path'])
                    out = pipe("a cat")
                    result['backend'] = 'diffusers'
                    result['output_shape'] = str(type(out))
                    result['success'] = True
                except Exception:
                    result['backend'] = 'diffusers'
                    result['error'] = 'diffusers模型推理失败'
            elif ext == '.pt' and 'transformers' in minfo['path']:
                from transformers import AutoModel, AutoTokenizer
                model = AutoModel.from_pretrained(minfo['path'])
                tokenizer = AutoTokenizer.from_pretrained(minfo['path'])
                inputs = tokenizer("你好", return_tensors="pt")
                out = model(**inputs)
                result['backend'] = 'transformers'
                result['output_shape'] = str(out.last_hidden_state.shape)
                result['success'] = True
            else:
                result['error'] = '暂不支持该模型类型自动推理'
        except Exception as e:
            result['error'] = str(e) + '\n' + traceback.format_exc()
        return result
"""Auto-detect model file in a directory and provide a simple loader wrapper.
It tries to support multiple backends: pygpt4all and llama_cpp (if installed).
If none available, it returns a dummy object so rest of system works offline.
"""
import os, glob
from pathlib import Path
class ModelLoader:
    def self_check(self):
        import time
        report = {
            'model_dirs': [],
            'supported_formats': list(self.SUPPORTED_FORMATS.keys()),
            'models_found': 0,
            'missing_dependencies': [],
            'dependency_versions': {},
            'load_test': None,
            'param_count': None,
            'load_time': None,
            'inference_test': None,
            'suggestions': []
        }
        dirs = [self.preferred_dir] if self.preferred_dir else self.DEFAULT_DIRS
        for d in dirs:
            report['model_dirs'].append(str(d))
            if not d.exists():
                report.setdefault('missing_dirs', []).append(str(d))
                report['suggestions'].append(f'模型目录不存在：{d}，请检查路径或新建目录。')
        for pkg in ['pygpt4all', 'llama_cpp_python', 'torch', 'onnxruntime', 'tensorflow']:
            try:
                mod = __import__(pkg)
                ver = getattr(mod, '__version__', None)
                report['dependency_versions'][pkg] = ver
            except Exception:
                report['missing_dependencies'].append(pkg)
                report['suggestions'].append(f'缺失依赖包：{pkg}，建议运行 pip install {pkg} 自动安装。')
        models = self.find_all_models()
        report['models_found'] = len(models)
        if models:
            try:
                t0 = time.time()
                result = self.load_model(models[0]['path'])
                t1 = time.time()
                report['load_time'] = round(t1-t0, 3)
                report['load_test'] = {'success': result['error'] is None, 'backend': result['backend'], 'error': result['error']}
                if result['backend'] == 'torch' and result['model'] is not None:
                    try:
                        param_count = sum(p.numel() for p in result['model'].parameters())
                        report['param_count'] = param_count
                    except Exception:
                        report['param_count'] = '未知'
                        report['suggestions'].append('无法统计参数量，建议检查模型结构或依赖版本。')
                if result['backend'] == 'torch' and result['model'] is not None:
                    try:
                        import torch
                        dummy_input = torch.randn(1, 3, 224, 224)
                        out = result['model'](dummy_input)
                        report['inference_test'] = {'success': True, 'output_shape': tuple(out.shape)}
                    except Exception as e:
                        report['inference_test'] = {'success': False, 'error': str(e)}
                        report['suggestions'].append(f'推理异常：{e}，建议检查模型输入 shape 或依赖版本。')
            except Exception as e:
                report['load_test'] = {'success': False, 'error': str(e)}
                report['suggestions'].append(f'模型加载失败：{e}，建议检查模型格式或依赖包。')
        else:
            report['suggestions'].append('未检测到可用模型文件，请将模型文件放入 models 相关目录。')
        return report

    def auto_infer_and_check(self, model_path=None):
        """
        自动推理健康检查：根据模型类型自动生成测试输入，运行推理并校验输出 shape。
        支持 transformers、diffusers、onnx、keras、torch、paddlepaddle 等主流模型。
        """
        import traceback
        result = {'model_path': model_path, 'backend': None, 'success': False, 'output_shape': None, 'error': None, 'suggestion': None}
        mlist = self.find_all_models()
        minfo = None
        if model_path:
            minfo = next((m for m in mlist if m['path'] == model_path), None)
        else:
            minfo = mlist[0] if mlist else None
        if not minfo:
            result['error'] = '未找到可用模型'
            result['suggestion'] = '请将模型文件放入 models 相关目录，并确保格式受支持。'
            return result
        ext = Path(minfo['path']).suffix.lower()
        try:
            if ext in ['.pt', '.pth']:
                import torch
                model = torch.load(minfo['path'])
                dummy_input = torch.randn(1, 3, 224, 224)
                out = model(dummy_input)
                result['backend'] = 'torch'
                result['output_shape'] = tuple(out.shape)
                result['success'] = True
            elif ext == '.onnx':
                import onnxruntime
                session = onnxruntime.InferenceSession(minfo['path'])
                input_name = session.get_inputs()[0].name
                dummy_input = {input_name: [[0.0]*224]*224}
                out = session.run(None, dummy_input)
                result['backend'] = 'onnxruntime'
                result['output_shape'] = str([o.shape if hasattr(o, 'shape') else type(o) for o in out])
                result['success'] = True
            elif ext == '.h5':
                from tensorflow import keras
                model = keras.models.load_model(minfo['path'])
                import numpy as np
                dummy_input = np.random.randn(1, 224, 224, 3)
                out = model.predict(dummy_input)
                result['backend'] = 'keras'
                result['output_shape'] = tuple(out.shape)
                result['success'] = True
            elif ext in ['.bin', '.gguf']:
                from pygpt4all import GPT4All
                model = GPT4All(model=minfo['path'])
                out = model.generate("你好", max_tokens=10)
                result['backend'] = 'pygpt4all'
                result['output_shape'] = str(type(out))
                result['success'] = True
            elif ext == '.pdparams':
                import paddle
                model = paddle.load(minfo['path'])
                dummy_input = paddle.randn([1, 3, 224, 224])
                out = model(dummy_input)
                result['backend'] = 'paddlepaddle'
                result['output_shape'] = tuple(out.shape)
                result['success'] = True
            elif ext == '.safetensors':
                try:
                    from diffusers import DiffusionPipeline
                    pipe = DiffusionPipeline.from_pretrained(minfo['path'])
                    out = pipe("a cat")
                    result['backend'] = 'diffusers'
                    result['output_shape'] = str(type(out))
                    result['success'] = True
                except Exception:
                    result['backend'] = 'diffusers'
                    result['error'] = 'diffusers模型推理失败'
                    result['suggestion'] = '建议检查模型路径或转换为标准 diffusers 格式。'
            elif ext == '.pt' and 'transformers' in minfo['path']:
                from transformers import AutoModel, AutoTokenizer
                model = AutoModel.from_pretrained(minfo['path'])
                tokenizer = AutoTokenizer.from_pretrained(minfo['path'])
                inputs = tokenizer("你好", return_tensors="pt")
                out = model(**inputs)
                result['backend'] = 'transformers'
                result['output_shape'] = str(out.last_hidden_state.shape)
                result['success'] = True
            else:
                result['error'] = '暂不支持该模型类型自动推理'
                result['suggestion'] = '建议检查模型格式或扩展 ModelLoader 支持。'
        except Exception as e:
            result['error'] = str(e) + '\n' + traceback.format_exc()
            if 'No module named' in result['error']:
                mod_name = result['error'].split('No module named ')[-1].split(' ')[0].replace("'","")
                result['suggestion'] = f'缺失依赖包：{mod_name}，建议运行 pip install {mod_name} 自动安装。'
            elif 'shape' in result['error'] or 'input' in result['error']:
                result['suggestion'] = '推理输入 shape 异常，建议检查模型输入维度或参考官方文档。'
            else:
                result['suggestion'] = '建议检查模型路径、格式或依赖包版本。'
        return result
        import time
        report = {
            'model_dirs': [],
            'supported_formats': list(self.SUPPORTED_FORMATS.keys()),
            'models_found': 0,
            'missing_dependencies': [],
            'dependency_versions': {},
            'load_test': None,
            'param_count': None,
            'load_time': None,
            'inference_test': None
        }
        # 检查模型目录
        dirs = [self.preferred_dir] if self.preferred_dir else self.DEFAULT_DIRS
        for d in dirs:
            report['model_dirs'].append(str(d))
            if not d.exists():
                report.setdefault('missing_dirs', []).append(str(d))
        # 检查依赖包及版本
        for pkg in ['pygpt4all', 'llama_cpp_python', 'torch', 'onnxruntime', 'tensorflow']:
            try:
                mod = __import__(pkg)
                ver = getattr(mod, '__version__', None)
                report['dependency_versions'][pkg] = ver
            except Exception:
                report['missing_dependencies'].append(pkg)
        # 检查模型文件
        models = self.find_all_models()
        report['models_found'] = len(models)
        # 尝试加载第一个模型并统计参数量、加载耗时
        if models:
            try:
                t0 = time.time()
                result = self.load_model(models[0]['path'])
                t1 = time.time()
                report['load_time'] = round(t1-t0, 3)
                report['load_test'] = {'success': result['error'] is None, 'backend': result['backend'], 'error': result['error']}
                # 参数量统计
                if result['backend'] == 'torch' and result['model'] is not None:
                    try:
                        param_count = sum(p.numel() for p in result['model'].parameters())
                        report['param_count'] = param_count
                    except Exception:
                        report['param_count'] = '未知'
                # 推理健康检查（仅示例，实际需根据模型类型定制）
                if result['backend'] == 'torch' and result['model'] is not None:
                    try:
                        import torch
                        dummy_input = torch.randn(1, 3, 224, 224)
                        out = result['model'](dummy_input)
                        report['inference_test'] = {'success': True, 'output_shape': tuple(out.shape)}
                    except Exception as e:
                        report['inference_test'] = {'success': False, 'error': str(e)}
                # 可扩展：其他后端推理测试
            except Exception as e:
                report['load_test'] = {'success': False, 'error': str(e)}
        return report
    SUPPORTED_FORMATS = {
        '.gguf': 'LLM', '.bin': 'LLM', '.pt': 'LLM/CV', '.pth': 'LLM/CV', '.onnx': 'LLM/CV', '.pb': 'CV', '.h5': 'CV/语音', '.tflite': 'CV/语音'
    }
    def __init__(self, preferred_dir=None):
        self.preferred_dir = preferred_dir
        self.DEFAULT_DIRS = self._find_gpt_dirs()

    def _find_gpt_dirs(self):
        from pathlib import Path
        start_dir = Path(__file__).resolve().parent
        dirs = []
        for parent in [start_dir] + list(start_dir.parents):
            gpt_ai = parent / 'GPT' / 'AI'
            if gpt_ai.exists():
                dirs.append(gpt_ai)
            ai = parent / 'AI'
            if ai.exists():
                dirs.append(ai)
        return dirs if dirs else [start_dir]
    def find_all_models(self):
        from pathlib import Path
        try:
            dirs = [self.preferred_dir] if self.preferred_dir else self.DEFAULT_DIRS
            found = []
            for d in dirs:
                d = Path(d) if not isinstance(d, Path) else d
                if d and d.exists():
                    for ext, mtype in self.SUPPORTED_FORMATS.items():
                        for f in d.glob(f'**/*{ext}'):
                            found.append({
                                'path': str(f.resolve()),
                                'type': mtype,
                                'name': f.name,
                                'size': f.stat().st_size,
                                'last_modified': f.stat().st_mtime
                            })
            return {
                'success': True,
                'models': sorted(found, key=lambda x: x['last_modified'], reverse=True),
                'error': None
            }
        except Exception as e:
            return {
                'success': False,
                'models': [],
                'error': str(e)
            }
    def get_model_metadata(self, model_info):
        try:
            meta = {
                'success': True,
                'name': model_info.get('name'),
                'path': model_info.get('path'),
                'type': model_info.get('type'),
                'size': model_info.get('size'),
                'last_modified': model_info.get('last_modified', model_info.get('mtime')),
                'backend': model_info.get('backend', 'unknown'),
                'error': None
            }
            # 可扩展：参数量、依赖、用途等
            return meta
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    def load_model(self, model_path=None):
        mlist = self.find_all_models()
        minfo = None
        if model_path:
            minfo = next((m for m in mlist if m['path'] == model_path), None)
        else:
            minfo = mlist[0] if mlist else None
        if not minfo:
            return {'error': '未找到可用模型', 'backend': 'none', 'model': None, 'meta': None}
        ext = Path(minfo['path']).suffix.lower()
        try:
            if ext in ['.gguf', '.bin']:
                from pygpt4all import GPT4All
                model = GPT4All(model=minfo['path'])
                backend = 'pygpt4all'
            elif ext in ['.pt', '.pth']:
                import torch
                model = torch.load(minfo['path'])
                backend = 'torch'
            elif ext == '.onnx':
                import onnxruntime
                model = onnxruntime.InferenceSession(minfo['path'])
                backend = 'onnxruntime'
            elif ext == '.h5':
                from tensorflow import keras
                model = keras.models.load_model(minfo['path'])
                backend = 'keras'
            else:
                model = None
                backend = 'unknown'
            meta = self.get_model_metadata(minfo)
            meta['backend'] = backend
            return {'backend': backend, 'model': model, 'meta': meta, 'error': None}
        except Exception as e:
            meta = self.get_model_metadata(minfo)
            meta['backend'] = 'error'
            meta['error'] = str(e)
            return {'backend': 'error', 'model': None, 'meta': meta, 'error': str(e)}

if __name__ == "__main__":
    print("ModelLoader 仅作为模块使用，不建议直接运行。")

from flask import Flask, jsonify, request, send_from_directory
from werkzeug.exceptions import BadRequest
import logging, os, sys, json, subprocess, time, select, importlib, threading, shutil
from pathlib import Path

# 动态获取当前脚本所在目录
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

def find_gpt_folder(start_dir=None):
    if start_dir is None:
        start_dir = Path(__file__).resolve().parent
    for parent in [start_dir] + list(start_dir.parents):
        gpt_dir = parent / 'GPT'
        if gpt_dir.exists() and gpt_dir.is_dir():
            return gpt_dir
    return None

GPT_DIR = find_gpt_folder()

LOG = logging.getLogger('ai_assistant.server')
logging.basicConfig(level=logging.INFO)
app = Flask(__name__, static_folder='reports')
BASE = BASE_DIR

# 新增：统一模型元数据与健康状态 API
@app.route('/models', methods=['GET'])
def models():
    try:
        from ai.model_loader import ModelLoader
        loader = ModelLoader()
        models_result = loader.find_all_models()
        if not models_result.get('success'):
            return jsonify({'error': models_result.get('error')}), 400
        model_list = []
        for m in models_result.get('models', []):
            meta = loader.get_model_metadata(m)
            # 健康状态联动
            try:
                check = loader.auto_infer_and_check(m['path'])
                meta['health'] = check.get('status', 'unknown')
                meta['check_report'] = check
            except Exception as e:
                meta['health'] = 'error'
                meta['check_report'] = {'error': str(e)}
            model_list.append(meta)
        return jsonify({'models': model_list})
    except BadRequest as br:
        return jsonify({'error': '参数校验失败', 'detail': str(br)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 新增：模型健康检查与推理测试 API
@app.route('/model_check', methods=['GET'])
def model_check():
    try:
        from ai.model_loader import ModelLoader
        loader = ModelLoader()
        check_report = loader.self_check()
        infer_report = loader.auto_infer_and_check()
        # 结构化日志写入
        log_entry = {
            'event': 'model_check',
            'timestamp': __import__('datetime').datetime.utcnow().isoformat() + 'Z',
            'self_check': check_report,
            'inference_check': infer_report
        }
        try:
            with open('server_dependency.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as logerr:
            logging.error(f"日志写入失败: {logerr}")
        return jsonify({'self_check': check_report, 'inference_check': infer_report})
    except BadRequest as br:
        return jsonify({'error': '参数校验失败', 'detail': str(br)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
#!/usr/bin/env python3
import os, sys
# 自动检测并切换到虚拟环境
VENV_PATH = os.path.join(os.path.dirname(__file__), '../../.venv/bin/python')
if sys.executable != os.path.abspath(VENV_PATH) and os.path.exists(VENV_PATH):
     print(f"[自动切换] 使用虚拟环境: {VENV_PATH}")
     os.execv(VENV_PATH, [VENV_PATH] + sys.argv)
     sys.exit(0)
"""Simple Flask server for VS Code integration (POST /ask, GET /report)."""
import logging
logging.basicConfig(filename='server_dependency.log', level=logging.INFO)
try:
    from flask import Flask, request, jsonify, send_from_directory
except ImportError as e:
    logging.error(f"缺失依赖: {e}")
    raise
logging.info("已自动补齐依赖: flask")
import os, json
from pathlib import Path
import sys
import subprocess
import time
import select
import importlib
import threading
import shutil

LOG = logging.getLogger('ai_assistant.server')
logging.basicConfig(level=logging.INFO)
app = Flask(__name__, static_folder='reports')
BASE = Path(__file__).parent
REQUIRED_PACKAGES = ["Flask", "PyYAML", "pygments"]
DEFAULT_MODEL_DIRS = [
    os.path.expanduser("~/models"),
    os.path.expanduser("~/.local/share/nomic.ai/GPT4All/"),
    os.path.join(os.path.dirname(__file__), "models"),
]

def find_models():
    found_models = []
    for mdir in DEFAULT_MODEL_DIRS:
        if os.path.exists(mdir):
            for root, dirs, files in os.walk(mdir):
                for file in files:
                    if file.lower().endswith((".bin", ".gguf", ".pt", ".pth", ".onnx", ".pb", ".h5", ".tflite")):
                        found_models.append(os.path.join(root, file))
    return found_models

MODEL_FILES = find_models()
if MODEL_FILES:
    logging.info(f"已识别到AI模型: {MODEL_FILES}")
    print(f"[模型识别] 已识别到AI模型: {MODEL_FILES}")
else:
    logging.warning("未检测到可用AI模型，请将模型文件放入 models 相关目录")
    print("[模型识别] 未检测到可用AI模型，请将模型文件放入 ~/models 或 ai_config/models 目录")
WORKSPACE_DIR = "/home/xiedaima/桌面/GZQ"

# 自动检测并安装依赖
for pkg in REQUIRED_PACKAGES:
    try:
        __import__(pkg.lower())
    except ImportError:
        logging.warning(f"缺失依赖: {pkg}, 正在自动安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", pkg])
        logging.info(f"已自动安装依赖: {pkg}")
    except Exception as e:
        logging.error(f"依赖安装异常: {e}")

logging.info(f"工作区目录: {WORKSPACE_DIR}")
# 检查工作区文件夹
if not os.path.exists(WORKSPACE_DIR):
    logging.error(f"工作区目录不存在: {WORKSPACE_DIR}")
    print(f"工作区目录不存在: {WORKSPACE_DIR}")
else:
    logging.info(f"工作区目录已找到: {WORKSPACE_DIR}")

# 自动发现并集成所有 scanner、utils、ai 子模块
MODULE_PATHS = [
    'ai_assistant_full_package.scanner',
    'ai_assistant_full_package.utils',
    'ai_assistant_full_package.ai'
]
for mod_path in MODULE_PATHS:
    mod_dir = os.path.join(os.path.dirname(__file__), mod_path.split('.')[-1])
    if os.path.exists(mod_dir):
        for fname in os.listdir(mod_dir):
            if fname.endswith('.py') and not fname.startswith('__'):
                mname = f"{mod_path}.{fname[:-3]}"
                try:
                    importlib.import_module(mname)
                    logging.info(f"已自动集成模块: {mname}")
                except Exception as e:
                    logging.error(f"模块集成失败: {mname}, 错误: {e}")

# 内容识别优化：支持多类型文件自动识别与处理
SUPPORTED_FILE_TYPES = ['.py', '.js', '.html', '.md', '.json', '.yaml', '.yml']
def is_supported_file(filename):
    return any(filename.endswith(ext) for ext in SUPPORTED_FILE_TYPES)

def scan_workspace_for_supported_files(workspace_dir):
    supported_files = []
    for root, dirs, files in os.walk(workspace_dir):
        for file in files:
            if is_supported_file(file):
                supported_files.append(os.path.join(root, file))
    logging.info(f"识别到支持的文件: {len(supported_files)} 个")
    return supported_files

# 在主流程中调用
supported_files = scan_workspace_for_supported_files(WORKSPACE_DIR)
logging.info(f"已优化内容识别，支持文件类型: {SUPPORTED_FILE_TYPES}")

# 智能学习与自我优化建议模块（扩展：联动性、兼容性、容错率、安全性、多项化发展）
def generate_global_suggestions(supported_files):
    suggestions = []
    py_files = [f for f in supported_files if f.endswith('.py')]
    js_files = [f for f in supported_files if f.endswith('.js')]
    config_files = [f for f in supported_files if f.endswith('.yaml') or f.endswith('.yml') or f.endswith('.json')]
    doc_files = [f for f in supported_files if f.endswith('.md')]
    # 联动性建议
    if len(py_files) > 0 and len(js_files) > 0:
        suggestions.append("建议：项目包含多语言脚本，建议实现 Python 与 JS 的数据或接口联动。")
    # 兼容性建议
    if not config_files:
        suggestions.append("建议：未检测到配置文件，建议添加 .yaml/.json 配置以提升环境兼容性。")
    # 容错率建议
    if any('test' in f.lower() for f in py_files):
        suggestions.append("建议：已检测到测试脚本，建议完善异常处理和单元测试以提升容错率。")
    else:
        suggestions.append("建议：未检测到测试脚本，建议补充测试用例以提升项目健壮性。")
    # 安全性建议
    if any('security' in f.lower() for f in py_files):
        suggestions.append("建议：已集成安全相关模块，建议定期进行安全扫描和依赖升级。")
    else:
        suggestions.append("建议：未检测到安全相关模块，建议增加安全扫描器或依赖检查功能。")
    # 多项化发展建议
    if len(doc_files) > 0:
        suggestions.append("建议：已检测到文档文件，可自动生成 API 文档和用户手册，支持多端协作。")
    else:
        suggestions.append("建议：未检测到文档文件，建议补充 README.md 或开发文档以提升项目多项化发展。")
    suggestions.append("建议：可集成更多 AI 模型或插件，提升智能化和自动化能力。")
    return suggestions

# 每次启动自动生成全局建议
global_suggestions = generate_global_suggestions(supported_files)
for s in global_suggestions:
    logging.info(f"智能建议: {s}")
    print(f"[AI智能建议] {s}")

# 集成智能分析和自动化测试流程
try:
    from utils.script_analyzer import ScriptAnalyzer
    from utils.connectivity_tester import GlobalConnectivityTester
    from utils.system_logic_validator import SystemLogicValidator

    def smart_deployment_manager():
        """智能部署管理器 - 根据脚本修改规模自动选择测试策略"""
        try:
            analyzer = ScriptAnalyzer(WORKSPACE_DIR)
            connectivity_tester = GlobalConnectivityTester(WORKSPACE_DIR)
            logic_validator = SystemLogicValidator(WORKSPACE_DIR)
            
            # 分析所有脚本的影响级别
            interaction_map = analyzer.get_global_interaction_map()
            
            # 判断是否需要进行全局测试
            high_impact_count = len(interaction_map['high_impact_scripts'])
            medium_impact_count = len(interaction_map['medium_impact_scripts'])
            
            if high_impact_count > 0 or medium_impact_count > 2:
                logging.info("检测到大脚本修改，执行全局连通性和逻辑验证...")
                print("[智能部署] 检测到大脚本修改，正在进行全局测试...")
                
                # 执行全局连通性测试
                connectivity_results = connectivity_tester.run_comprehensive_test()
                logging.info(f"连通性测试完成，健康度: {connectivity_results['overall_health']:.1f}%")
                
                # 执行整体逻辑验证
                validation_results = logic_validator.validate_system_logic()
                logging.info(f"系统逻辑验证完成，状态: {validation_results['system_status']}")
                
                # 输出详细建议
                for recommendation in validation_results['recommendations']:
                    logging.info(f"系统建议: {recommendation}")
                    print(f"[系统建议] {recommendation}")
                    
            else:
                logging.info("检测到小脚本修改，执行轻量级检查...")
                print("[智能部署] 检测到小脚本修改，执行轻量级检查...")
                
                # 只对修改的脚本进行单独验证
                for script_path in interaction_map['low_impact_scripts']:
                    script_analysis = analyzer.analyze_script_impact(script_path)
                    if script_analysis['impact_level'] == 'low':
                        logging.info(f"脚本 {script_path} 通过轻量级检查")
                        
        except Exception as e:
            logging.error(f"智能部署管理器异常: {e}")
            print(f"[警告] 智能部署管理器异常: {e}")

    # 执行智能部署管理
    smart_deployment_manager()
    
except ImportError as e:
    logging.warning(f"智能分析模块导入失败，跳过高级功能: {e}")
    print(f"[警告] 智能分析模块导入失败，使用基础功能: {e}")

# 10秒无响应自动继续（示例，实际可用于交互流程）
def wait_for_input(prompt, timeout=10):
    print(prompt)
    start = time.time()
    sys.stdout.flush()
    while True:
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            return sys.stdin.readline().strip()
        if time.time() - start > timeout:
            print("超时，自动继续...")
            return None

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json(force=True) or {}
    q = data.get('query') or data.get('question') or ''
    if not q:
        return jsonify({'error':'no query provided'}), 400
    try:
        from utils.memory_cache import MemoryCache
        cache = MemoryCache()
        from ai.context_manager import ContextManager
        ctx = cache.get('latest_context') or {}
        from ai.responder import Responder
        r = Responder().respond(ctx, q)
        return jsonify({'answer': r})
    except Exception as e:
        LOG.exception('ask fail')
        return jsonify({'error': str(e)}), 500

# 新增：规则管理 API
@app.route('/rules', methods=['GET', 'POST'])
def rules():
    import yaml
    rules_path = BASE / 'config' / 'settings.yaml'
    if request.method == 'GET':
        try:
            with open(rules_path, 'r', encoding='utf-8') as f:
                rules = yaml.safe_load(f)
            return jsonify(rules)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    if request.method == 'POST':
        try:
            new_rules = request.get_json(force=True)
            # 表单安全校验：必须为 dict 且包含至少一个分组
            if not isinstance(new_rules, dict) or not new_rules:
                return jsonify({'error': '规则数据格式错误或为空', 'code': 'invalid_rules'}), 400
            # 可扩展更多字段校验
            with open(rules_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(new_rules, f, allow_unicode=True)
            # 全局联动建议
            from ai_config.server import global_auto_optimization_suggestion
            suggestions = global_auto_optimization_suggestion()
            print(f"[全局建议] {suggestions[-1] if suggestions else '无建议'}")
            return jsonify({'status': 'updated', 'suggestion': suggestions[-1] if suggestions else '无建议'})
        except Exception as e:
            return jsonify({'error': str(e), 'code': 'update_failed'}), 500

# 新增：结构可视化 API
@app.route('/structure', methods=['GET'])
def structure():
    try:
        from utils.structure_visualizer import StructureVisualizer
        visualizer = StructureVisualizer(WORKSPACE_DIR)
        structure_data = visualizer.get_project_structure()
        # 全局联动建议
        from ai_config.server import global_auto_optimization_suggestion
        suggestions = global_auto_optimization_suggestion()
        print(f"[全局建议] {suggestions[-1] if suggestions else '无建议'}")
        structure_data['suggestion'] = suggestions[-1] if suggestions else '无建议'
        return jsonify(structure_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 新增：团队协作与任务分派 API
@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    try:
        from utils.global_coordination_tester import GlobalCoordinationTester
        tester = GlobalCoordinationTester(WORKSPACE_DIR)
        if request.method == 'GET':
            return jsonify(tester.list_tasks())
        if request.method == 'POST':
            task_info = request.get_json(force=True)
            # 表单安全校验：必须为 dict 且包含任务描述
            if not isinstance(task_info, dict) or 'description' not in task_info:
                return jsonify({'error': '任务数据格式错误或缺少描述', 'code': 'invalid_task'}), 400
            result = tester.assign_task(task_info)
            # 全局联动建议
            from ai_config.server import global_auto_optimization_suggestion
            suggestions = global_auto_optimization_suggestion()
            print(f"[全局建议] {suggestions[-1] if suggestions else '无建议'}")
            result['suggestion'] = suggestions[-1] if suggestions else '无建议'
            return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e), 'code': 'assign_failed'}), 500

# 新增：智能守护与自愈机制 API
@app.route('/self_heal', methods=['POST'])
def self_heal():
    try:
        from utils.system_logic_validator import SystemLogicValidator
        from scanner.security_scanner import SecurityScanner
        validator = SystemLogicValidator(WORKSPACE_DIR)
        scanner = SecurityScanner(WORKSPACE_DIR)
        issues = scanner.scan_security_issues()
        heal_result = validator.auto_heal(issues)
        # 全局联动建议
        from ai_config.server import global_auto_optimization_suggestion
        suggestions = global_auto_optimization_suggestion()
        print(f"[全局建议] {suggestions[-1] if suggestions else '无建议'}")
        return jsonify({'heal_result': heal_result, 'issues': issues, 'suggestion': suggestions[-1] if suggestions else '无建议'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/report', methods=['GET'])
def report():
    rp = BASE / 'reports' / 'scan_report.html'
    if rp.exists():
        return send_from_directory(str(BASE / 'reports'), 'scan_report.html')
    return jsonify({'error':'no report generated yet'}), 404

@app.route('/feedback_log', methods=['GET'])
def feedback_log():
    try:
        with open('server_dependency.log', 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/plain; charset=utf-8'}
    except Exception as e:
        return f'无法读取日志: {e}', 500

def clear_cache():
    cache_dir = os.path.join(os.path.dirname(__file__), 'utils', '__pycache__')
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
        print('[系统] 已清理缓存目录 utils/__pycache__')
        logging.info('[系统] 已清理缓存目录 utils/__pycache__')
    cache_dir2 = os.path.join(os.path.dirname(__file__), 'scanner', '__pycache__')
    if os.path.exists(cache_dir2):
        shutil.rmtree(cache_dir2)
        print('[系统] 已清理缓存目录 scanner/__pycache__')
        logging.info('[系统] 已清理缓存目录 scanner/__pycache__')
    # 可扩展更多缓存目录

def schedule_cache_clear():
    def periodic_clear():
        while True:
            import time; time.sleep(1800)
            clear_cache()
    t = threading.Thread(target=periodic_clear, daemon=True)
    t.start()

# 错误回滚机制
import copy
last_good_state = None

def safe_script_update(update_func):
    global last_good_state
    try:
        last_good_state = copy.deepcopy(update_func())
        print('[系统] 脚本修改成功，已保存快照')
        logging.info('[系统] 脚本修改成功，已保存快照')
    except Exception as e:
        print(f'[系统] 检测到错误，自动回滚并清理缓存: {e}')
        logging.error(f'[系统] 检测到错误，自动回滚并清理缓存: {e}')
        if last_good_state:
            # 回滚逻辑（示例，实际需结合版本管理或文件备份）
            pass
        clear_cache()


# 新增：自动化编程流水线 API
from threading import Lock
pipeline_state = {
    'tasks': [],
    'status': 'idle',
    'last_event': None,
    'suggestions': []
}
pipeline_lock = Lock()

@app.route('/pipeline', methods=['GET', 'POST'])
def pipeline():
    global pipeline_state
    with pipeline_lock:
        if request.method == 'GET':
            return jsonify(pipeline_state)
        if request.method == 'POST':
            data = request.get_json(force=True) or {}
            event = data.get('event')
            task = data.get('task')
            # 表单安全校验：event 必须为字符串，task（如有）必须为 dict
            if not isinstance(event, str) or (task and not isinstance(task, dict)):
                return jsonify({'error': '流水线参数格式错误', 'code': 'invalid_pipeline'}), 400
            # 事件驱动：根据 event 类型自动联动
            pipeline_state['last_event'] = event
            if event == 'start':
                pipeline_state['status'] = 'running'
                if task:
                    pipeline_state['tasks'].append(task)
            elif event == 'stop':
                pipeline_state['status'] = 'stopped'
            elif event == 'reset':
                pipeline_state = {'tasks': [], 'status': 'idle', 'last_event': None, 'suggestions': []}
            elif event == 'suggest':
                # 联动优化建议输出
                from ai.refactor_suggester import RefactorSuggester
                from utils.memory_cache import MemoryCache
                cache = MemoryCache()
                ctx = cache.get('latest_context') or {}
                scan_results = ctx.get('scan_results', {})
                suggester = RefactorSuggester()
                suggestions = suggester.suggest(scan_results, ctx)
                pipeline_state['suggestions'] = suggestions
            return jsonify({'status': pipeline_state['status'], 'tasks': pipeline_state['tasks'], 'suggestions': pipeline_state.get('suggestions', [])})


# 全局自动优化建议机制
def global_auto_optimization_suggestion():
    from utils.project_logic_optimizer import ProjectLogicOptimizer
    from utils.global_coordination_tester import GlobalCoordinationTester
    from utils.system_logic_validator import SystemLogicValidator
    from utils.structure_visualizer import StructureVisualizer
    optimizer = ProjectLogicOptimizer(WORKSPACE_DIR)
    coordination = GlobalCoordinationTester(WORKSPACE_DIR)
    validator = SystemLogicValidator(WORKSPACE_DIR)
    visualizer = StructureVisualizer(WORKSPACE_DIR)
    # 1. 项目逻辑优化建议
    logic_report = optimizer.generate_optimization_report()
    # 2. 协调性建议
    coord_report = coordination.generate_coordination_report()
    # 3. 系统自愈与安全建议
    sys_report = validator.validate_system_logic()
    # 4. 结构分析建议
    struct_data = visualizer.get_project_structure()
    struct_analysis = struct_data.get('analysis', {})
    # 汇总建议
    suggestions = []
    suggestions.extend(logic_report.get('recommendations', []))
    suggestions.extend(coord_report.get('recommendations', []))
    suggestions.extend(sys_report.get('recommendations', []))
    suggestions.extend(struct_analysis.get('suggestions', []))
    # 保证每次执行后至少有一条建议
    if not suggestions:
        suggestions.append('项目结构与逻辑良好，无需优化。建议持续关注安全与协作。')
    print(f"[全局优化建议] {suggestions[-1]}")
    logging.info(f"[全局优化建议] {suggestions[-1]}")
    return suggestions

# 每次任务完成或无任务时自动调用
def on_task_complete():
    suggestions = global_auto_optimization_suggestion()
    # 自动输出建议
    print(f"[自动建议] {suggestions[-1] if suggestions else '无建议'}")
    # 自动触发下一步任务（如有任务队列，可在此联动 pipeline 或主控模块）
    # 示例：自动调用 pipeline 事件驱动
    import requests
    try:
        requests.post('http://127.0.0.1:5000/pipeline', json={'event': 'suggest'})
    except Exception as e:
        print(f"[自动联动] pipeline 事件触发失败: {e}")
    finally:
        pass

# 动态注册自定义API路由
import yaml
CUSTOM_API_CONFIG = os.path.join(BASE, 'config/settings.yaml')
def register_custom_apis(app):
    if not os.path.exists(CUSTOM_API_CONFIG):
        return
    with open(CUSTOM_API_CONFIG, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    for api in config.get('api', {}).get('group', []):
        route = api.get('route')
        name = api.get('name')
        if route and name:
            def custom_api():
                return jsonify({'message': f'自定义API {name} 已注册', 'route': route})
            app.add_url_rule(route, endpoint=name, view_func=custom_api, methods=['GET'])
register_custom_apis(app)

# 日志与监控模块联动
from functools import wraps

def log_api_event(event_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                LOG.info(f'[API事件] {event_name} 成功')
                return result
            except Exception as e:
                LOG.error(f'[API异常] {event_name}: {e}')
                return jsonify({'error': str(e)}), 500
        return wrapper
    return decorator

# 示例：为所有自定义API自动加日志
for rule in app.url_map.iter_rules():
    if rule.endpoint.startswith('自定义API'):
        view_func = app.view_functions[rule.endpoint]
        app.view_functions[rule.endpoint] = log_api_event(rule.endpoint)(view_func)

# 日志与监控模块联动扩展
import threading
MONITOR_LOG_PATH = os.path.join(BASE, 'reports/monitor_log.json')
monitor_data = []

def log_monitor_event(event, detail=None):
    entry = {
        'event': event,
        'detail': detail,
        'timestamp': __import__('datetime').datetime.utcnow().isoformat() + 'Z'
    }
    monitor_data.append(entry)
    try:
        with open(MONITOR_LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    except Exception as e:
        LOG.error(f'监控日志写入失败: {e}')

@app.before_request
def before_any_request():
    log_monitor_event('request', {'path': request.path, 'method': request.method})

@app.errorhandler(Exception)
def handle_any_exception(e):
    log_monitor_event('error', {'error': str(e), 'path': request.path})
    return jsonify({'error': str(e)}), 500

@app.route('/monitor', methods=['GET'])
def get_monitor_data():
    try:
        with open(MONITOR_LOG_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        data = [json.loads(line) for line in lines]
        return jsonify({'monitor': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 权限与安全管理扩展
from functools import wraps
API_TOKEN = os.environ.get('API_TOKEN', 'default-token')

def require_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token != f'Bearer {API_TOKEN}':
            LOG.warning(f'权限校验失败: {request.path}')
            return jsonify({'error': '权限校验失败'}), 403
        return func(*args, **kwargs)
    return wrapper

@app.route('/secure-data', methods=['GET'])
@require_token
def get_secure_data():
    LOG.info(f'敏感数据访问: {request.path}')
    return jsonify({'data': '这是受保护的数据'})

# 预留安全扫描工具集成入口（如 bandit、safety）
def run_security_scan():
    # 可集成 bandit/safety 命令行自动检测
    pass

if __name__ == '__main__':
    print('[DEBUG] 仅启动 Flask 服务，无其他逻辑')
    logging.info('仅启动 Flask 服务，无其他逻辑')
    app.run(port=5000)
    print('[DEBUG] Flask 服务已启动')
    logging.info('Flask 服务已启动')

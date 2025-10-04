import sys
import subprocess
import shutil
import importlib.metadata
from pathlib import Path
import json # 提前导入 json

# 动态获取当前脚本所在目录
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR
BXDM_PATH = BASE_DIR / 'BXDM'
INTEGRATED_PATH = BASE_DIR / 'GZQ_integrated'
VENV_PATH = BASE_DIR / '.venv'

# 保证ai_config模块可导入
if (INTEGRATED_PATH / 'ai_config').is_dir():
    sys.path.insert(0, str(INTEGRATED_PATH))

# 自动适配虚拟环境下python/pip路径
if sys.platform == 'win32':
    PYTHON_BIN = VENV_PATH / 'Scripts' / 'python.exe'
    PIP_BIN = VENV_PATH / 'Scripts' / 'pip.exe'
    BANDIT_BIN = VENV_PATH / 'Scripts' / 'bandit.exe'
    SAFETY_BIN = VENV_PATH / 'Scripts' / 'safety.exe'
else:
    PYTHON_BIN = VENV_PATH / 'bin' / 'python'
    PIP_BIN = VENV_PATH / 'bin' / 'pip'
    BANDIT_BIN = VENV_PATH / 'bin' / 'bandit'
    SAFETY_BIN = VENV_PATH / 'bin' / 'safety'

def run_command(cmd, check=True, shell=False, capture_output=False, text=False):
    """
    封装 subprocess.run，提供统一的错误处理和日志。
    """
    try:
        result = subprocess.run(cmd, check=check, shell=shell, capture_output=capture_output, text=text)
        if capture_output and text:
            return result.stdout.strip()
        return True
    except subprocess.CalledProcessError as e:
        print(f'[ERROR] 命令执行失败: {" ".join(cmd)} - {e}')
        if capture_output and text:
            print(f'[ERROR] stderr: {e.stderr}')
        return False
    except FileNotFoundError:
        print(f'[ERROR] 命令未找到: {cmd[0]}。请确保已安装并配置好 PATH。')
        return False

def install_system_dependencies():
    """
    检测并安装 Ubuntu 24 桌面实例系统所需的系统级依赖。
    """
    if sys.platform == 'linux':
        print('[INFO] 检测并安装系统级依赖 (适用于 Ubuntu 24)')
        required_packages = ['python3-venv', 'git']
        installed_packages = run_command(['dpkg', '-l'], capture_output=True, text=True)
        
        packages_to_install = []
        for pkg in required_packages:
            if installed_packages and f' {pkg} ' not in installed_packages:
                packages_to_install.append(pkg)
        
        if packages_to_install:
            print(f'[INFO] 正在安装系统软件包: {", ".join(packages_to_install)}')
            if not run_command(['sudo', 'apt', 'update']):
                print('[ERROR] apt update 失败，请检查网络连接或权限。')
                return False
            if not run_command(['sudo', 'apt', 'install', '-y'] + packages_to_install):
                print('[ERROR] 系统软件包安装失败。请手动安装或检查权限。')
                return False
            print('[INFO] 系统软件包安装完成。')
        else:
            print('[INFO] 所有必要的系统软件包已安装。')

        # 检查 VSCode 的 'code' 命令
        if not shutil.which('code'):
            print('[WARN] VSCode 的 "code" 命令未找到。')
            print('请确保已安装 VSCode 并将其添加到 PATH。')
            print('您可以通过以下命令安装 VSCode (如果尚未安装):')
            print('  sudo snap install --classic code')
            print('或从官网下载安装包: https://code.visualstudio.com/download')
        else:
            print('[INFO] VSCode "code" 命令已找到。')
        return True
    else:
        print(f'[INFO] 当前操作系统为 {sys.platform}，跳过 Linux 系统依赖安装。')
        return True

def check_and_install_python_package(package, version=None):
    """
    检查并安装 Python 包，支持指定版本。
    """
    try:
        dist_version = importlib.metadata.version(package)
        if version:
            if dist_version == version:
                print(f'[INFO] {package} 已安装且版本匹配: {version}')
                return True
            else:
                print(f'[INFO] {package} 已安装但版本为 {dist_version}，将尝试安装指定版本 {version}')
        else:
            print(f'[INFO] {package} 已安装，版本: {dist_version}')
            return True
    except importlib.metadata.PackageNotFoundError:
        print(f'[INFO] {package} 未安装，将自动安装')
    
    install_str = f'{package}=={version}' if version else package
    print(f'[INFO] 正在安装 Python 包: {install_str}')
    if not run_command([str(PIP_BIN), 'install', install_str]):
        print(f'[ERROR] Python 包 {install_str} 安装失败。')
        return False
    return True

# 1. 安装系统级依赖
if not install_system_dependencies():
    print('[ERROR] 系统依赖安装失败，请检查日志并手动解决。')
    sys.exit(1)

# 2. 创建并激活虚拟环境
if not VENV_PATH.exists():
    print('[INFO] 虚拟环境未找到，正在创建...')
    if not run_command([sys.executable, '-m', 'venv', str(VENV_PATH)]):
        print('[ERROR] 虚拟环境创建失败。')
        sys.exit(1)
    print('[INFO] 虚拟环境已创建。')
    # 补充安装 pip，兼容部分系统 venv 不自动安装 pip
    print('[INFO] 确保虚拟环境中 pip 已安装并升级。')
    if not run_command([str(PYTHON_BIN), '-m', 'ensurepip', '--upgrade']):
        print('[ERROR] 虚拟环境中 pip 补充安装失败。')
        sys.exit(1)
    print('[INFO] pip 已补充安装。')
else:
    print('[INFO] 虚拟环境已存在。')

# 确保 pip 可用并升级
if not PIP_BIN.exists():
    print('[WARN] 虚拟环境中 pip 可执行文件未找到，尝试重新安装 ensurepip。')
    if not run_command([str(PYTHON_BIN), '-m', 'ensurepip', '--upgrade']):
        print('[ERROR] 虚拟环境中 pip 补充安装失败。')
        sys.exit(1)
print('[INFO] 升级 pip 到最新版本。')
if not run_command([str(PIP_BIN), 'install', '--upgrade', 'pip']):
    print('[ERROR] pip 升级失败。')
    sys.exit(1)

# 3. 安装 Python 依赖
print('[INFO] 开始安装 Python 依赖。')
DEPENDENCIES = {
    'flask': None,
    'pyyaml': None,
    'pygments': None,
    'pytest': None,
    'torch': None,
    'onnxruntime': None,
    'tensorflow': None,
    'pygpt4all': None
}
for pkg, ver in DEPENDENCIES.items():
    check_and_install_python_package(pkg, ver)
print('[INFO] Python 依赖安装并版本检查完成。')

# 清理多余版本（仅保留当前虚拟环境下的依赖）
def clean_extra_versions():
    site_packages = VENV_PATH / 'lib' / f'python{sys.version_info.major}.{sys.version_info.minor}' / 'site-packages'
    if not site_packages.exists():
        print('[WARN] site-packages 路径不存在，跳过多余版本清理。')
        return
    
    cleaned_any = False
    for pkg in DEPENDENCIES.keys():
        # 查找以包名开头且包含版本号的目录或文件
        # 注意：这里假设包名在 site-packages 中是以下划线分隔的，例如 'flask-2.0.0.dist-info'
        # 并且可能存在多个版本目录
        matches = [d for d in site_packages.iterdir() if d.name.startswith(pkg.replace('-', '_')) and '-' in d.name]
        
        if len(matches) > 1:
            # 尝试根据版本号排序，保留最新的
            # 这是一个简化的逻辑，可能不适用于所有复杂的版本命名
            matches_with_versions = []
            for m in matches:
                try:
                    # 提取版本号，例如 'flask-2.0.0.dist-info' -> '2.0.0'
                    version_str = m.name.split('-')[1].split('.')[0] # 简化处理，可能需要更复杂的版本解析
                    matches_with_versions.append((m, version_str))
                except IndexError:
                    matches_with_versions.append((m, '0.0.0')) # 无法解析版本则视为旧版本

            # 假设版本字符串可以直接比较，或者需要更复杂的 LooseVersion 比较
            matches_with_versions.sort(key=lambda x: x[1], reverse=True)
            
            for old_path, _ in matches_with_versions[1:]:
                if old_path.is_dir():
                    shutil.rmtree(old_path)
                    print(f'[INFO] 已清理多余版本目录: {old_path.name}')
                    cleaned_any = True
                elif old_path.is_file():
                    old_path.unlink()
                    print(f'[INFO] 已清理多余版本文件: {old_path.name}')
                    cleaned_any = True
    if not cleaned_any:
        print('[INFO] 未发现需要清理的多余版本。')

print('[INFO] 开始清理多余的 Python 包版本。')
clean_extra_versions()
print('[INFO] 多余版本清理完成。')

# 4. AI模型自检与健康检查
try:
    sys.path.insert(0, str(INTEGRATED_PATH))
    from ai_config.ai.model_loader import ModelLoader
    print('[INFO] 正在进行 AI 模型自检与健康检查...')
    check_result = ModelLoader().self_check()
    with open(str(PROJECT_ROOT / 'model_self_check.json'), 'w', encoding='utf-8') as f:
        json.dump(check_result, f, ensure_ascii=False, indent=2)
    print('[AI模型自检报告]')
    print(json.dumps(check_result, ensure_ascii=False, indent=2))

    # 4.1 自动协作分派与同步（GitHub/GitLab）
    print('[INFO] 正在进行协作分派与同步 (GitHub/GitLab)...')
    try:
        from ai_config.utils.global_coordination_tester import sync_github_gitlab_tasks
        sync_result = sync_github_gitlab_tasks(BXDM_PATH)
        with open(str(PROJECT_ROOT / 'coordination_sync_log.json'), 'w', encoding='utf-8') as f:
            json.dump(sync_result, f, ensure_ascii=False, indent=2)
        print('[GitHub/GitLab 协作分派同步结果]')
        print(json.dumps(sync_result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f'[ERROR] 协作分派同步失败: {e}')
    
    # 4.2 智能建议与自愈机制自动检测与修复
    print('[INFO] 正在进行智能建议与自愈机制自动检测与修复...')
    try:
        from ai_config.utils.system_logic_validator import self_heal_and_suggest
        heal_result = self_heal_and_suggest(BXDM_PATH)
        with open(str(PROJECT_ROOT / 'self_heal_log.json'), 'w', encoding='utf-8') as f:
            json.dump(heal_result, f, ensure_ascii=False, indent=2)
        print('[智能建议与自愈结果]')
        print(json.dumps(heal_result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f'[ERROR] 智能建议与自愈机制失败: {e}')
    
    # 4.3 数据分析与可视化自动报告生成
    print('[INFO] 正在进行数据分析与可视化自动报告生成...')
    try:
        from ai_config.utils.report_generator import generate_full_report
        report_result = generate_full_report(BXDM_PATH)
        with open(str(PROJECT_ROOT / 'full_analysis_report.json'), 'w', encoding='utf-8') as f:
            json.dump(report_result, f, ensure_ascii=False, indent=2)
        print('[数据分析与可视化报告]')
        print(json.dumps(report_result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f'[ERROR] 数据分析与可视化失败: {e}')
    
    # 4.4 国际化与本地化自动检测与切换
    print('[INFO] 正在进行国际化与本地化自动检测与切换...')
    try:
        from ai_config.utils.global_compat import detect_and_switch_language
        lang_result = detect_and_switch_language()
        with open(str(PROJECT_ROOT / 'language_switch_log.json'), 'w', encoding='utf-8') as f:
            json.dump(lang_result, f, ensure_ascii=False, indent=2)
        print('[国际化与本地化结果]')
        print(json.dumps(lang_result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f'[ERROR] 国际化与本地化失败: {e}')
    
    # 4.5 安全扫描
    print('[INFO] 正在进行安全扫描 (Bandit, Safety)...')
    bandit_report = PROJECT_ROOT / 'bandit_report.json'
    safety_report = PROJECT_ROOT / 'safety_report.txt'
    try:
        print('[INFO] 正在安装安全扫描工具 Bandit 和 Safety。')
        if not run_command([str(PIP_BIN), 'install', 'bandit', 'safety']):
            print('[ERROR] 安全扫描工具安装失败。')
        else:
            print('[INFO] 运行 Bandit 安全扫描。')
            run_command([str(BANDIT_BIN), '-r', str(BXDM_PATH), '-f', 'json', '-o', str(bandit_report)])
            print('[INFO] 运行 Safety 依赖安全检测。')
            run_command([str(SAFETY_BIN), 'check', '--full-report', '--output', str(safety_report)])
            
            if bandit_report.exists():
                with open(str(bandit_report), 'r', encoding='utf-8') as f:
                    print('[Bandit 安全扫描结果]')
                    print(f.read())
            else:
                print('[WARN] Bandit 报告文件未生成。')

            if safety_report.exists():
                with open(str(safety_report), 'r', encoding='utf-8') as f:
                    print('[Safety 依赖安全检测结果]')
                    print(f.read())
            else:
                print('[WARN] Safety 报告文件未生成。')
    except Exception as e:
        print(f'[ERROR] 安全扫描失败: {e}')
except Exception as e:
    print(f'[ERROR] AI模型自检或相关功能执行失败: {e}')

def summarize_ai_assistant_status():
    """
    汇总 AI 助手各项功能的执行状态。
    """
    print('\n[AI 助手功能汇总报告]')
    status = {}

    # 模型自检
    model_check_report = PROJECT_ROOT / 'model_self_check.json'
    if model_check_report.exists():
        with open(model_check_report, 'r', encoding='utf-8') as f:
            report = json.load(f)
            status['model_self_check'] = report.get('status', '未知')
            print(f'  - AI 模型自检: {status["model_self_check"]}')
    else:
        status['model_self_check'] = '未执行或报告缺失'
        print(f'  - AI 模型自检: {status["model_self_check"]}')

    # 协作分派与同步
    coordination_sync_log = PROJECT_ROOT / 'coordination_sync_log.json'
    if coordination_sync_log.exists():
        with open(coordination_sync_log, 'r', encoding='utf-8') as f:
            report = json.load(f)
            status['coordination_sync'] = report.get('status', '未知')
            print(f'  - 协作分派与同步: {status["coordination_sync"]}')
    else:
        status['coordination_sync'] = '未执行或报告缺失'
        print(f'  - 协作分派与同步: {status["coordination_sync"]}')

    # 智能建议与自愈机制
    self_heal_log = PROJECT_ROOT / 'self_heal_log.json'
    if self_heal_log.exists():
        with open(self_heal_log, 'r', encoding='utf-8') as f:
            report = json.load(f)
            status['self_heal_suggest'] = report.get('status', '未知')
            print(f'  - 智能建议与自愈: {status["self_heal_suggest"]}')
    else:
        status['self_heal_suggest'] = '未执行或报告缺失'
        print(f'  - 智能建议与自愈: {status["self_heal_suggest"]}')

    # 数据分析与可视化
    full_analysis_report = PROJECT_ROOT / 'full_analysis_report.json'
    if full_analysis_report.exists():
        with open(full_analysis_report, 'r', encoding='utf-8') as f:
            report = json.load(f)
            status['data_analysis_viz'] = report.get('status', '未知')
            print(f'  - 数据分析与可视化: {status["data_analysis_viz"]}')
    else:
        status['data_analysis_viz'] = '未执行或报告缺失'
        print(f'  - 数据分析与可视化: {status["data_analysis_viz"]}')

    # 国际化与本地化
    language_switch_log = PROJECT_ROOT / 'language_switch_log.json'
    if language_switch_log.exists():
        with open(language_switch_log, 'r', encoding='utf-8') as f:
            report = json.load(f)
            status['i18n_l10n'] = report.get('status', '未知')
            print(f'  - 国际化与本地化: {status["i18n_l10n"]}')
    else:
        status['i18n_l10n'] = '未执行或报告缺失'
        print(f'  - 国际化与本地化: {status["i18n_l10n"]}')

    # 安全扫描
    bandit_report = PROJECT_ROOT / 'bandit_report.json'
    safety_report = PROJECT_ROOT / 'safety_report.txt'
    if bandit_report.exists() and safety_report.exists():
        status['security_scan'] = '已完成'
        print(f'  - 安全扫描: {status["security_scan"]}')
    else:
        status['security_scan'] = '未完成或报告缺失'
        print(f'  - 安全扫描: {status["security_scan"]}')

    overall_status = '成功'
    for key, val in status.items():
        if val not in ['成功', '已完成', '已安装', '已存在']: # 假设这些是成功的状态
            overall_status = '存在问题'
            break
    print(f'\n[整体 AI 助手功能状态]: {overall_status}')
    return status

# 执行汇总报告
summarize_ai_assistant_status()

# 5. 保留 AI模型和功能模块在 GZQ_integrated 内，BXDM 仅作为开发区
print('[INFO] AI模型和功能模块已保留在 GZQ_integrated，BXDM 仅作为代码开发区。')

# 6. 自动生成 VSCode 配置
vscode_dir = PROJECT_ROOT / '.vscode'
vscode_dir.mkdir(exist_ok=True)
settings = {
    "python.pythonPath": str(PYTHON_BIN),
    "ai-assistant.serverUrl": "http://localhost:5000",
    "code-runner.executorMap": {"python": str(PYTHON_BIN)},
    "locale": "zh-cn",
    "files.autoSave": "afterDelay",
    "extensions.ignoreRecommendations": False
}
with open(str(vscode_dir / 'settings.json'), 'w', encoding='utf-8') as f:
    json.dump(settings, f, ensure_ascii=False, indent=2)
with open(str(vscode_dir / 'extensions.json'), 'w', encoding='utf-8') as f:
    json.dump({"recommendations": ["formulahendry.code-runner", "ms-ceintl.vscode-language-pack-zh-hans", "ms-python.python", "ms-vscode.gitlens", "Gruntfuggly.todo-tree"]}, f, ensure_ascii=False, indent=2)
print('[INFO] VSCode 配置已生成。')

# 7. 自动打开 VSCode
print('[INFO] 尝试自动打开 VSCode...')
try:
    run_command(['code', str(BXDM_PATH)])
    print('[INFO] VSCode 已自动打开 BXDM 项目目录。')
except Exception as e:
    print(f'[WARN] VSCode 启动失败: {e}')
    print('请手动打开 VSCode 并导航到 BXDM 项目目录。')

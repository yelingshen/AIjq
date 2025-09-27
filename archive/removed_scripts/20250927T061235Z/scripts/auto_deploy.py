import sys
import subprocess
import shutil
import importlib.metadata
from pathlib import Path
import json # 提前导入 json

# 动态获取当前脚本所在目录
BASE_DIR = Path(__file__).resolve().parent.parent
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


def create_virtualenv(venv_path: Path):
    """创建并激活项目虚拟环境（如果不存在）。"""
    if venv_path.exists():
        print(f'[INFO] 虚拟环境已存在: {venv_path}')
        return True

    print(f'[INFO] 创建虚拟环境: {venv_path}')
    if not run_command([sys.executable, '-m', 'venv', str(venv_path)]):
        print('[ERROR] 创建虚拟环境失败。')
        return False

    print('[INFO] 虚拟环境创建完成。')
    return True


def pip_install(requirements_file: Path):
    """使用 venv 中的 pip 安装 requirements.txt 指定的依赖。"""
    if not requirements_file.exists():
        print(f'[WARN] 依赖文件不存在: {requirements_file}')
        return True

    # Prefer invoking the venv's python -m pip to avoid PATH surprises
    python_exec = str(PYTHON_BIN) if PYTHON_BIN.exists() else shutil.which('python3') or shutil.which('python')
    if not python_exec:
        print('[ERROR] Python 未找到，无法通过 -m pip 安装。')
        return False

    print(f'[INFO] 使用 {python_exec} -m pip 安装: {requirements_file}')
    if not run_command([python_exec, '-m', 'pip', 'install', '-r', str(requirements_file)]):
        print('[ERROR] pip install 失败。')
        return False
    print('[INFO] pip install 完成。')
    return True


def ensure_python_packages(packages: list):
    """确保指定的 Python 包已安装（尝试通过 import 检查）。"""
    missing = []
    # Some packages have different import names vs pip package names.
    import_name_map = {
        'pyyaml': 'yaml',
    }
    for pkg in packages:
        import_name = import_name_map.get(pkg, pkg)
        try:
            importlib.import_module(import_name)
        except Exception:
            missing.append(pkg)

    if not missing:
        print('[INFO] 所需 Python 包均已安装。')
        return True

    print(f'[INFO] 缺失的 Python 包: {missing}，将尝试通过 pip 安装。')
    pip_exec = str(PIP_BIN) if PIP_BIN.exists() else shutil.which('pip')
    if not pip_exec:
        print('[ERROR] pip 未找到，无法安装缺失包。')
        return False

    if not run_command([pip_exec, 'install'] + missing):
        print('[ERROR] 通过 pip 安装缺失包失败。')
        return False
    print('[INFO] 缺失包安装完成。')
    return True


def install_project_requirements():
    """根据仓库的推荐 requirements 列表安装依赖。
    优先使用 deployment/install_requirements.txt，如果不存在，尝试根目录 requirements.txt。
    """
    requirements_candidates = [PROJECT_ROOT / 'deployment' / 'install_requirements.txt', PROJECT_ROOT / 'requirements.txt']
    for req in requirements_candidates:
        if req.exists():
            return pip_install(req)

    print('[WARN] 未找到 requirements 文件，跳过安装。')
    return True


def run_safety_and_bandit_checks(code_path: Path):
    """可选的安全/静态检查（bandit/safety）"""
    print('[INFO] 运行安全扫描 (bandit/safety)')
    bandit_exec = str(BANDIT_BIN) if BANDIT_BIN.exists() else shutil.which('bandit')
    safety_exec = str(SAFETY_BIN) if SAFETY_BIN.exists() else shutil.which('safety')

    if bandit_exec:
        run_command([bandit_exec, '-r', str(code_path)])
    else:
        print('[WARN] bandit 未安装，跳过 bandit 检查。')

    if safety_exec:
        run_command([safety_exec, 'check', '--file', str(PROJECT_ROOT / 'requirements.txt')])
    else:
        print('[WARN] safety 未安装，跳过 safety 检查。')


def copy_vscode_settings():
    """把 BXDM 或项目内部的 VSCode 推荐设置拷贝到 .vscode/（如果存在）。"""
    src = BXDM_PATH / '.vscode'
    dst = PROJECT_ROOT / '.vscode'
    if src.exists() and src.is_dir():
        print(f'[INFO] 复制 VSCode 设置从 {src} 到 {dst}')
        dst.mkdir(exist_ok=True)
        for item in src.iterdir():
            target = dst / item.name
            if item.is_dir():
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(item, target)
            else:
                shutil.copy2(item, target)
        print('[INFO] VSCode 设置复制完成。')
    else:
        print('[INFO] 未检测到 BXDM/.vscode，跳过复制 VSCode 设置。')


def deploy_assets():
    """简化的部署动作：生成部署清单、创建 releases 目录并拷贝关键文件。"""
    releases = PROJECT_ROOT / 'releases'
    releases.mkdir(exist_ok=True)
    manifest = {
        'project': PROJECT_ROOT.name,
        'python': sys.version,
    }
    manifest_path = releases / 'manifest.json'
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    print(f'[INFO] 生成发布清单: {manifest_path}')

    # 拷贝关键文件: deployment, ai, scripts
    for name in ['deployment', 'ai', 'scripts']:
        src = PROJECT_ROOT / name
        if src.exists():
            dst = releases / name
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
    print('[INFO] 发布包准备完成，位于 releases/ 目录。')


def main():
    print('[INFO] 开始自动部署流程')
    # 1. 系统依赖
    if not install_system_dependencies():
        print('[ERROR] 系统依赖安装失败，终止。')
        return

    # 2. 创建虚拟环境
    if not create_virtualenv(VENV_PATH):
        print('[ERROR] 虚拟环境创建失败，终止。')
        return

    # 3. 安装项目依赖
    if not install_project_requirements():
        print('[ERROR] 项目依赖安装失败，终止。')
        return

    # 4. 确认部分关键包
    ensure_python_packages(['flask', 'pyyaml', 'requests'])

    # 5. 运行可选安全检查
    run_safety_and_bandit_checks(PROJECT_ROOT)

    # 6. 复制 VSCode 建议配置
    copy_vscode_settings()

    # 7. 生成部署包
    deploy_assets()

    print('[INFO] 自动部署流程完成。')


if __name__ == '__main__':
    main()


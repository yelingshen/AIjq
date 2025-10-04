import shutil, subprocess
from . import logger

installed_deps = []

MIN_DEPENDS = ["python3","python3-tk"]

def check_minimal():
    for cmd in MIN_DEPENDS:
        if shutil.which(cmd) is None:
            try:
                subprocess.run(["sudo","apt","update","-qq"], check=True)
                subprocess.run(["sudo","apt","install","-y",cmd], check=True)
                installed_deps.append(cmd)
                logger.log(f"安装最小依赖: {cmd}")
            except subprocess.CalledProcessError:
                logger.log(f"安装失败: {cmd}")
                raise

def install_if_missing(pkgs):
    missing = [p for p in pkgs if p and shutil.which(p) is None]
    for pkg in missing:
        try:
            subprocess.run(["sudo","apt","install","-y",pkg], check=True)
            installed_deps.append(pkg)
            logger.log(f"按需安装依赖: {pkg}")
        except subprocess.CalledProcessError:
            logger.log(f"依赖安装失败: {pkg}")
            raise

def get_packages_for_ext(ext):
    import configparser, os
    conf_file = os.path.expanduser("~/.file_helper.conf")
    if not os.path.exists(conf_file):
        return []
    config = configparser.ConfigParser()
    config.read(conf_file)
    return config['DEFAULT'].get(ext,"").split()

import yaml
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.yaml')


def load_settings(path=None):
    p = path or CONFIG_PATH
    if not os.path.exists(p):
        return {}
    with open(p, 'r') as f:
        return yaml.safe_load(f) or {}


def save_settings(data, path=None):
    p = path or CONFIG_PATH
    with open(p, 'w') as f:
        yaml.safe_dump(data, f)
    return p

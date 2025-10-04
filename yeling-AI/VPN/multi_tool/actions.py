"""集中注册并导出可运行子功能（name -> callable, description）

目的：让 CLI 和 GUI 能以统一的方式列出/运行子功能。
"""
from typing import Callable, Dict, Any
import os
import sys

# registry: name -> metadata dict {func, description, admin_only, supports_dry_run, params}
_REGISTRY: Dict[str, Dict[str, Any]] = {}


def is_admin() -> bool:
    """Basic admin check: POSIX uses euid==0; on Windows it falls back to env flag for tests."""
    if os.name == 'posix':
        try:
            return os.geteuid() == 0
        except AttributeError:
            return False
    # Windows: allow override via env for CI/testing
    return os.environ.get('MULTI_TOOL_IS_ADMIN', '0') in ('1', 'true', 'True')


def action(name: str, description: str = '', admin_only: bool = False, supports_dry_run: bool = False, params: Dict[str, str] = None, depends: list = None, priority: int = 0):
    """Decorator to register an action.

    params: optional dict mapping param name -> description
    """
    def _decorator(fn: Callable):
        # normalize params: allow dict of name->desc or name->{required:bool, desc:str}
        norm = {}
        if params:
            for k, v in (params.items() if isinstance(params, dict) else []):
                if isinstance(v, dict):
                    norm[k] = {'required': bool(v.get('required', False)), 'desc': v.get('desc', '')}
                else:
                    norm[k] = {'required': False, 'desc': str(v)}

        _REGISTRY[name] = {
            'func': fn,
            'description': description,
            'admin_only': bool(admin_only),
            'supports_dry_run': bool(supports_dry_run),
            'params': norm,
            'depends': depends or [],
            'priority': int(priority),
        }
        return fn

    return _decorator


def register(name: str, func: Callable, description: str = '', admin_only: bool = False, supports_dry_run: bool = False, params: Dict[str, str] = None, depends: list = None, priority: int = 0):
    """Backward-compatible register function."""
    norm = {}
    if params:
        for k, v in (params.items() if isinstance(params, dict) else []):
            if isinstance(v, dict):
                norm[k] = {'required': bool(v.get('required', False)), 'desc': v.get('desc', '')}
            else:
                norm[k] = {'required': False, 'desc': str(v)}
    _REGISTRY[name] = {
        'func': func,
        'description': description,
        'admin_only': bool(admin_only),
        'supports_dry_run': bool(supports_dry_run),
        'params': norm,
        'depends': depends or [],
        'priority': int(priority),
    }


def list_actions() -> Dict[str, Dict[str, Any]]:
    return _REGISTRY.copy()


def run_action(name: str, dry_run: bool = False, params: Dict[str, Any] = None, check_admin: bool = True):
    if name not in _REGISTRY:
        raise KeyError(name)
    meta = _REGISTRY[name]
    if meta.get('admin_only') and check_admin and not is_admin():
        raise PermissionError(f"Action '{name}' requires admin privileges")
    fn = meta['func']
    # If dry_run requested but action doesn't support it, raise
    if dry_run and not meta.get('supports_dry_run'):
        raise RuntimeError(f"Action '{name}' does not support dry-run")
    # Call function with standardized signature: fn(dry_run=False, params=None)
    return fn(dry_run=bool(dry_run), params=params or {})


# Example legacy placeholder
def _hello():
    print('hello from multi_tool')


@action('hello', description='示例: 打印 hello', admin_only=False, supports_dry_run=True)
def _hello_action(dry_run=False, params=None):
    if dry_run:
        print('[Dry-Run] hello')
        return
    return _hello()

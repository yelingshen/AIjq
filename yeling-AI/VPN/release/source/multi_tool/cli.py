"""Simple CLI to run components of multi_tool."""
import argparse
import os
from .file_helper import main as fh
from .vpn_router import main as vr
from .vpn_router.utils.shell_utils import check_license, generate_license, license_status

def main():
    parser = argparse.ArgumentParser(prog='multi_tool')
    sub = parser.add_subparsers(dest='cmd')
    sub.add_parser('file-helper')
    p = sub.add_parser('vpn-router')
    p.add_argument('--config', default='config.yaml')
    # interactive menu command
    m = sub.add_parser('menu')
    m.add_argument('which', choices=['file-helper', 'vpn-router'], nargs='?', default='file-helper')
    m.add_argument('--config', default='config.yaml')
    # license management
    l = sub.add_parser('license')
    l.add_argument('action', choices=['generate', 'check'])
    l.add_argument('--path')
    # action management
    a = sub.add_parser('action')
    a_sub = a.add_subparsers(dest='sub')
    a_sub.add_parser('list')
    ar = a_sub.add_parser('run')
    ar.add_argument('name')
    ar.add_argument('--dry-run', action='store_true', help='只做演练，不执行敏感操作')
    ar.add_argument('--param', action='append', help='传递参数，格式 key=value，可重复')
    ar.add_argument('--non-interactive', action='store_true', help='非交互模式，缺少必需参数时报错')
    ar.add_argument('--as-admin', action='store_true', help='以管理员身份模拟执行（仅用于测试/CI）')

    args = parser.parse_args()

    # allow license commands without prior check
    if args.cmd == 'license':
        if args.action == 'generate':
            p = generate_license(path=args.path)
            print(f'License generated at {p}')
        else:
            ok, msg = license_status(args.path)
            print(msg)
        return

    # Authorization check for other commands
    if not check_license():
        print("Authorization failed. Please contact support.")
        return

    if args.cmd == 'file-helper':
        # launch GUI
        from .file_helper import main as fhmod
        fhmod.run_gui()
    elif args.cmd == 'vpn-router':
        from .vpn_router import main as vrmod
        vrmod.main(args.config)
    elif args.cmd == 'menu':
        if args.which == 'file-helper':
            from .file_helper import main as fhmod
            fhmod.run_gui()
        else:
            from .vpn_router import main as vrmod
            vrmod.load_main_menu(args.config)
    else:
        parser.print_help()
    # handle actions
    if args.cmd == 'action':
        from . import actions as _actions
        if args.sub == 'list':
            for k, meta in _actions.list_actions().items():
                desc = meta.get('description', '')
                params = meta.get('params', {})
                param_str = ''
                if params:
                    param_str = ' | params: ' + ', '.join([f"{n}{' (required)' if p.get('required') else ''}: {p.get('desc','')}" for n, p in params.items()])
                print(f"{k}: {desc}{param_str}")
            return
        elif args.sub == 'run':
            params = {}
            if getattr(args, 'param', None):
                for p in args.param:
                    if '=' in p:
                        k, v = p.split('=', 1)
                        params[k] = v
            # interactive prompt for missing params if schema declares required ones
            meta = _actions.list_actions().get(args.name, {})
            schema = meta.get('params', {})
            # schema format: {name: {'required': bool, 'desc': str}} or legacy simple dict mapping to desc
            for key, val in schema.items():
                # normalize legacy schema where val may be a string description
                if isinstance(val, str):
                    req = False
                    desc = val
                else:
                    req = bool(val.get('required'))
                    desc = val.get('desc', '')
                if key not in params and req:
                    if getattr(args, 'non_interactive', False):
                        raise ValueError(f"Missing required param '{key}' for action {args.name} in non-interactive mode")
                    # prompt interactively
                    try:
                        user_val = input(f"Enter value for '{key}' ({desc}): ")
                    except EOFError:
                        raise ValueError(f"Missing required param '{key}' and cannot prompt for input")
                    params[key] = user_val
            try:
                from . import orchestrator as _orch

                res = _orch.run_actions([args.name], dry_run=getattr(args, 'dry_run', False), params=params, check_admin=not getattr(args, 'as_admin', False))
                print(res)
            except Exception as e:
                print(f"Action failed: {e}")
                raise

if __name__ == '__main__':
    main()

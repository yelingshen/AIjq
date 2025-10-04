import time
from .vpn.vpn_controller import setup_vpn, get_vpn_status
from .network.port_forwarder import start_forwarder
import threading
import yaml

def main(config_path='config.yaml'):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    setup_vpn(config['vpn']['email'], config['vpn']['password'], 
              vpn_type=config['vpn'].get('type'), location=config['vpn'].get('location'))
    
    vpn_status = get_vpn_status()
    if vpn_status == "Disconnected":
        print("VPN连接失败，请检查配置。")
        return

    print(f"[{vpn_status}] 已连接成功")

    for mapping in config.get('port_mappings', []):
        threading.Thread(target=start_forwarder, args=(
            mapping['local_port'],
            mapping['remote_host'],
            mapping['remote_port']
        ), daemon=True).start()

def load_main_menu(config_path='config.yaml'):
    """交互式主菜单，提供 VPN 操作、查看状态和进入设置。"""
    import tkinter as _tk
    from tkinter import ttk as _tt, messagebox as _mb
    import yaml as _yaml

    try:
        with open(config_path, 'r') as f:
            cfg = _yaml.safe_load(f)
    except Exception:
        cfg = {}

    root = _tk.Tk()
    root.title('VPN 路由器')
    root.geometry('480x160')

    frame = _tt.Frame(root, padding=10)
    frame.pack(fill='both', expand=True)

    _tt.Label(frame, text='VPN 路由器主菜单').grid(row=0, column=0, sticky='w')

    def _connect():
        try:
            main(config_path)
            _mb.showinfo('信息', '已尝试建立 VPN 连接，详见控制台')
        except Exception as e:
            _mb.showerror('错误', f'连接失败: {e}')

    def _show_status():
        try:
            status = get_vpn_status()
            _mb.showinfo('VPN 状态', status)
        except Exception as e:
            _mb.showerror('错误', f'无法获取状态: {e}')

    _tt.Button(frame, text='连接 VPN', command=_connect).grid(row=1, column=0, pady=8)
    _tt.Button(frame, text='查看状态', command=_show_status).grid(row=1, column=1, pady=8)
    _tt.Button(frame, text='设置', command=lambda: _open_vpn_settings(root, cfg)).grid(row=1, column=2, pady=8)
    # Virtual device manager
    try:
        from .vpn.ip_detector import manage_virtual_devices
        _tt.Button(frame, text='虚拟设备管理', command=lambda: manage_virtual_devices(root)).grid(row=2, column=0, pady=8)
    except Exception:
        pass
    # Run actions dialog
    def _open_actions():
        import tkinter as _tk
        from tkinter import ttk as _tt2, messagebox as _mb
        from .. import actions as _actions

        win = _tk.Toplevel(root)
        win.title('运行子功能')
        win.geometry('420x320')
        frm = _tt2.Frame(win, padding=8)
        frm.pack(fill='both', expand=True)

        actions = _actions.list_actions()
        vars = {}
        for i, (name, (_, desc)) in enumerate(actions.items()):
            var = _tk.BooleanVar(value=False)
            vars[name] = var
            _tt2.Checkbutton(frm, text=f"{name} - {desc}", variable=var).pack(anchor='w')

        def _run_selected():
            selected = [n for n, v in vars.items() if v.get()]
            if not selected:
                _mb.showwarning('提示', '未选择任何子功能')
                return
            for n in selected:
                try:
                    _actions.run_action(n)
                except Exception as e:
                    _mb.showerror('错误', f'运行 {n} 失败: {e}')
            _mb.showinfo('完成', '所选操作已执行（详见控制台）')

        _tt2.Button(frm, text='运行所选', command=_run_selected).pack(pady=10)

    _tt.Button(frame, text='运行子功能', command=_open_actions).grid(row=2, column=1, pady=8)

    root.mainloop()


def _open_vpn_settings(root, cfg):
    import tkinter as _tk
    from tkinter import ttk as _tt
    from .. import settings as _settings
    win = _tk.Toplevel(root)
    win.title('VPN 设置')
    win.geometry('420x260')

    frm = _tt.Frame(win, padding=10)
    frm.pack(fill='both', expand=True)

    current = _settings.load_settings()
    _tt.Label(frm, text='VPN 设置（占位）').pack(anchor='w')
    var_vpn_autoconnect = _tk.BooleanVar(value=current.get('vpn_autoconnect', False))
    _tt.Checkbutton(frm, text='启动时自动连接 VPN', variable=var_vpn_autoconnect).pack(anchor='w')

    def _save():
        current['vpn_autoconnect'] = bool(var_vpn_autoconnect.get())
        _settings.save_settings(current)
        _tt.Button(frm, text='已保存').pack()
        win.destroy()

    _tt.Button(frm, text='保存并关闭', command=_save).pack(side='right', pady=10)

if __name__ == '__main__':
    main()

try:
    from ..actions import action as _action_decorator

    @_action_decorator('vpn.connect', description='连接 VPN (使用 config)', admin_only=False, supports_dry_run=True,)
    def _vpn_connect(dry_run=False, params=None):
        cfg = (params or {}).get('config', 'config.yaml')
        if dry_run:
            print(f"[Dry-Run] vpn.connect -> config={cfg}")
            return
        return main(cfg)

    @_action_decorator('vpn.status', description='获取 VPN 状态', admin_only=False, supports_dry_run=True)
    def _vpn_status(dry_run=False, params=None):
        return get_vpn_status()
except Exception:
    pass

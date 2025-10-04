import socket
import requests
import subprocess
import os
import threading

# Prefer netifaces if available (more detailed), otherwise fall back to psutil
try:
    import netifaces
    _HAS_NETIFACES = True
except Exception:
    netifaces = None
    _HAS_NETIFACES = False

try:
    import psutil
    _HAS_PSUTIL = True
except Exception:
    psutil = None
    _HAS_PSUTIL = False

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def get_vpn_ip():
    try:
        return requests.get("https://api.ipify.org").text
    except Exception as e:
        return f"Error: {e}"

def get_interfaces():
    """Return a list of interface names.

    Try netifaces first, then psutil. Raise RuntimeError if neither is
    available.
    """
    if _HAS_NETIFACES:
        return netifaces.interfaces()
    if _HAS_PSUTIL:
        return list(psutil.net_if_addrs().keys())
    raise RuntimeError("Neither netifaces nor psutil is available; cannot enumerate interfaces")

def get_interface_details(interface):
    """Return interface address details in a consistent dict format.

    If netifaces is present, return its mapping. Otherwise use psutil to
    construct a similar mapping.
    """
    if _HAS_NETIFACES:
        return netifaces.ifaddresses(interface)
    if _HAS_PSUTIL:
        addrs = psutil.net_if_addrs().get(interface, [])
        out = {}
        for a in addrs:
            fam = a.family
            # Map common families to netifaces-like keys
            if hasattr(netifaces, 'AF_INET') and fam == getattr(netifaces, 'AF_INET', None):
                k = netifaces.AF_INET
            else:
                # fallback: use family numeric value
                k = fam
            out.setdefault(k, []).append({'addr': a.address, 'netmask': a.netmask, 'broadcast': getattr(a, 'broadcast', None)})
        return out
    raise RuntimeError("Neither netifaces nor psutil is available; cannot retrieve interface details")

def enable_virtual_device():
    """启用虚拟设备功能"""
    if os.name == "nt":  # Windows
        subprocess.run(["powershell", "Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All"], shell=True)
    else:  # Linux
        subprocess.run(["sudo", "modprobe", "kvm"], check=True)
    print("虚拟设备功能已启用")

def update_software():
    """更新软件"""
    if os.name == "nt":
        subprocess.run(["winget", "upgrade", "--all"], shell=True)
    else:
        subprocess.run(["sudo", "apt", "update"], check=True)
        subprocess.run(["sudo", "apt", "upgrade", "-y"], check=True)
    print("软件已更新")

def restore_dns():
    """检查并恢复 DNS"""
    if os.name == "nt":
        subprocess.run(["ipconfig", "/flushdns"], shell=True)
    else:
        subprocess.run(["sudo", "systemd-resolve", "--flush-caches"], check=True)
    print("DNS 已恢复")


try:
    from ...actions import action as _action_decorator
    # decorate wrappers

    @_action_decorator('vdev.enable', description='启用虚拟设备', admin_only=True, supports_dry_run=False)
    def _enable_wrapper(dry_run=False, params=None):
        return enable_virtual_device()

    @_action_decorator('vdev.update', description='更新软件', admin_only=True, supports_dry_run=False)
    def _update_wrapper(dry_run=False, params=None):
        return update_software()

    @_action_decorator('vdev.restore_dns', description='恢复 DNS', admin_only=False, supports_dry_run=True)
    def _restore_wrapper(dry_run=False, params=None):
        return restore_dns()
except Exception:
    pass

def manage_virtual_devices(parent=None):
    import tkinter as _tk
    from tkinter import ttk as _tt, messagebox as _mb

    win = _tk.Toplevel(parent) if parent else _tk.Tk()
    win.title('虚拟设备管理')
    win.geometry('420x220')

    frm = _tt.Frame(win, padding=10)
    frm.pack(fill='both', expand=True)

    _tt.Label(frm, text='虚拟设备工具').pack(anchor='w')

    def run_bg(fn):
        def wrapper():
            def _task():
                try:
                    fn()
                    _mb.showinfo('完成', '操作已完成')
                except Exception as e:
                    _mb.showerror('错误', f'操作失败: {e}')
            threading.Thread(target=_task, daemon=True).start()
        return wrapper

    _tt.Button(frm, text='启用虚拟设备', command=run_bg(enable_virtual_device)).pack(fill='x', pady=6)
    _tt.Button(frm, text='更新软件', command=run_bg(update_software)).pack(fill='x', pady=6)
    _tt.Button(frm, text='恢复 DNS', command=run_bg(restore_dns)).pack(fill='x', pady=6)

    if not parent:
        win.mainloop()

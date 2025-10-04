import subprocess

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"命令执行失败: {cmd}\n错误: {result.stderr}")
    return result.stdout.strip()

def setup_vpn(email, password, vpn_type=None, location=None):
    if vpn_type == 'PIA':
        print('[PIA VPN] 连接...')
        run_cmd('piactl connect')
    else:
        print('[X-VPN] 登录并连接...')
        run_cmd(f'./xvpn_linux_amd64 login {email} {password}')
        if location:
            run_cmd(f'./xvpn_linux_amd64 location set "{location}"')
        run_cmd('./xvpn_linux_amd64 connect')

def get_vpn_status():
    try:
        output = run_cmd('./xvpn_linux_amd64 account')
        if 'Status: Connected' in output:
            return 'X-VPN'
    except Exception:
        pass
    try:
        output = subprocess.run('piactl status', shell=True, capture_output=True, text=True).stdout
        if 'Connected' in output:
            return 'PIA VPN'
    except Exception:
        pass
    return 'Disconnected'

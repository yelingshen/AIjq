import os
import sys
import platform
import subprocess

ROOT = os.path.abspath(os.path.dirname(__file__))

def choose_system():
    # If env var preset, honor it
    env = os.environ.get('MULTI_TOOL_TARGET') or os.environ.get('MULTI_TOOL_SYSTEM')
    if env:
        return env
    # Otherwise ask via simple console prompt (works cross-platform)
    print('Select target system for this run:')
    print('1) windows')
    print('2) ubuntu')
    choice = input('Choose (1/2) [auto-detect]: ').strip()
    if choice == '1':
        return 'windows'
    if choice == '2':
        return 'ubuntu'
    # default detect
    if os.name == 'nt' or platform.system().lower().startswith('win'):
        return 'windows'
    return 'ubuntu'


def main():
    tgt = choose_system()
    print(f'Chosen target: {tgt}')
    # Export env for installer
    os.environ['MULTI_TOOL_TARGET'] = tgt
    # Prefer packaged exe if present
    exe = os.path.join(ROOT, 'multi_tool.exe')
    if os.path.exists(exe):
        print('Running bundled executable...')
        subprocess.call([exe])
        return
    # Otherwise run installer_app.py via python
    py = sys.executable
    installer = os.path.join(ROOT, 'installer_app.py')
    if os.path.exists(installer):
        print('Launching installer UI via Python...')
        subprocess.call([py, installer])
        return
    # Fallback: run module
    print('Running package entrypoint via -m multi_tool.cli')
    subprocess.call([py, '-m', 'multi_tool.cli'])

if __name__ == '__main__':
    main()

"""Simple GUI installer/repair tool for multi_tool.

Features:
- System checks (Python version, venv, multi_tool.exe presence)
- Create virtualenv
- Install runtime dependencies (skipping netifaces on Windows)
- Generate license
- Run multi_tool subcommands (file-helper, vpn-router, actions)

This script is intended to be packaged with PyInstaller into a single exe
and distributed to end users as an interactive installer/repair utility.
"""

import os
import sys
import subprocess
import threading
import queue
import time
import tempfile
import shutil
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog

ROOT = os.path.abspath(os.path.dirname(__file__))
MULTI_TOOL_EXE = os.path.join(ROOT, 'dist', 'multi_tool.exe')

# --- i18n simple dictionary (zh/en) ---
LANG = 'zh'
STRINGS = {
    'zh': {
        'title': 'multi_tool 安装/修复',
        'select_actions': '选择操作：',
        'system_check': '系统检查',
        'create_venv': '创建虚拟环境 (.venv)',
        'install_deps': '安装运行时依赖',
        'generate_license': '生成授权文件',
        'start_file_helper': '启动 File Helper GUI',
        'vpn_connect': 'VPN: 连接（演练）',
        'run_selected': '执行所选',
        'templates': '模板：',
        'template_dev': '开发（Dev）',
        'template_min': '精简（Minimal）',
        'template_full': '完整（Full）',
        'recommend_install': '推荐安装所选工具',
        'check_completed': '检查完成',
    },
    'en': {
        'title': 'multi_tool Installer / Repair',
        'select_actions': 'Select actions:',
        'system_check': 'System check',
        'create_venv': 'Create virtualenv (.venv)',
        'install_deps': 'Install runtime dependencies',
        'generate_license': 'Generate license file',
        'start_file_helper': 'Start File Helper GUI',
        'vpn_connect': 'VPN: connect (dry-run)',
        'run_selected': 'Run selected',
        'templates': 'Templates:',
        'template_dev': 'Dev (recommended)',
        'template_min': 'Minimal',
        'template_full': 'Full',
        'recommend_install': 'Recommend/install selected tools',
        'check_completed': 'Check complete',
    }
}

def t(k):
    return STRINGS.get(LANG, STRINGS['en']).get(k, k)

# --- target system selection (windows / ubuntu) ---
# default: detect platform but allow user override
if os.name == 'nt':
    TARGET_SYSTEM = 'windows'
else:
    TARGET_SYSTEM = 'ubuntu'

# allow external override via environment variable (runner)
env_tgt = os.environ.get('MULTI_TOOL_TARGET') or os.environ.get('MULTI_TOOL_SYSTEM')
if env_tgt:
    TARGET_SYSTEM = env_tgt

def set_target_system(v):
    global TARGET_SYSTEM
    TARGET_SYSTEM = v
    append_output(f"Target system set to: {v}\n")

# --- Development tool checks and suggestions ---
DEV_TOOLS = [
    # (key, friendly name, winget id, download url)
    ('git', 'Git', 'Git.Git', 'https://git-scm.com/download/win'),
    ('node', 'Node.js', 'OpenJS.NodeJS', 'https://nodejs.org/'),
    ('npm', 'npm', None, 'https://www.npmjs.com/get-npm'),
    ('code', 'VS Code', 'Microsoft.VisualStudioCode', 'https://code.visualstudio.com/'),
    ('docker', 'Docker Desktop', 'Docker.DockerDesktop', 'https://www.docker.com/get-started'),
    ('winget', 'Windows Package Manager (winget)', None, 'https://learn.microsoft.com/windows/package-manager/winget/'),
    ('cl.exe', 'MSVC (cl.exe)', 'Microsoft.VisualStudio.2022.BuildTools', 'https://visualstudio.microsoft.com/visual-cpp-build-tools/'),
]

def check_tool_exists(cmd):
    try:
        # Use where.exe on Windows to locate commands
        rc, out = run_cmd(['where', cmd])
        return rc == 0
    except Exception:
        return False

def check_dev_tools():
    append_output('== Dev tool check start ==\n')
    results = {}
    for key, friendly, wid, url in DEV_TOOLS:
        ok = check_tool_exists(key)
        results[key] = ok
        append_output(f'{friendly} ({key}): {ok}\n')
    append_output('== Dev tool check end ==\n')
    return results

def recommend_install_selected(selected):
    # If winget present, use it; otherwise open browser to download pages
    winget_ok = check_tool_exists('winget')
    for name in selected:
        info = next(((n, friendly, wid, u) for n, friendly, wid, u in DEV_TOOLS if n == name), None)
        url = info[3] if info else None
        append_output(f'Recommend/install: {name}\n')
        if winget_ok:
            append_output(f'Installing {name} via winget...\n')
            wid = info[2] if info else None
            if wid:
                rc, out = run_cmd(['winget', 'install', '--id', wid, '--accept-source-agreements', '--accept-package-agreements'])
            else:
                append_output(f'No winget id for {name}; opening download page instead\n')
                import webbrowser
                if url:
                    webbrowser.open(url)
                rc = 1
            append_output(f'rc={rc}\n')
        else:
            if url:
                import webbrowser
                webbrowser.open(url)
                append_output(f'Opened browser to {url}\n')
            else:
                append_output(f'No URL for {name}\n')

# --- Menu placeholders for extension modules (from external folders) ---
EXT_MODULES = {
    'ubuntu_file_helper_gui': {
        'title': 'Ubuntu File Helper GUI',
        'desc': 'Linux-oriented file helper GUI (import scripts from ubuntu_file_helper_gui folder).',
        'actions': [
            {'key': 'analyze', 'title': 'Analyze files', 'desc': 'Detect file type and propose install steps', 'compat': ['ubuntu'], 'deps': [], 'run_type': 'dry-run'},
            {'key': 'start_server', 'title': 'Start report server', 'desc': 'Start bundled Flask report server (main.py)', 'compat': ['ubuntu','windows'], 'deps': ['python3','flask'], 'run_type': 'background-py'},
            {'key': 'install_deps_for_file', 'title': 'Install missing deps for file', 'desc': 'Run dependency installer mapping for selected file', 'compat': ['ubuntu'], 'deps': ['sudo','apt'], 'run_type': 'confirm-run'},
            {'key': 'detect_deps', 'title': 'Detect file -> deps mapping', 'desc': 'Show mapping between extension and system packages', 'compat': ['ubuntu'], 'deps': [], 'run_type': 'dry-run'},
            {'key': 'sandbox_run', 'title': 'Sandbox run', 'desc': 'Attempt to run selected file in sandbox (dry-run)', 'compat': ['ubuntu'], 'deps': ['firejail'], 'run_type': 'confirm-run'},
        ]
    },
    'yeling_super_helper_tui': {
        'title': 'Yeling Super Helper (TUI)',
        'desc': 'Terminal-based helper with workflow scripts (import from yeling_super_helper_tui).',
        'actions': [
            {'key': 'tui_main', 'title': 'Run TUI', 'desc': 'Launch yeling_super_helper_tui.sh (whiptail TUI)', 'compat': ['ubuntu'], 'deps': ['bash','whiptail'], 'run_type': 'background-shell'},
            {'key': 'auto_install', 'title': 'Auto-install package/URL', 'desc': 'Run auto_install module (one-click installer helper)', 'compat': ['ubuntu'], 'deps': ['wget','curl','apt','pip3'], 'run_type': 'confirm-run'},
            {'key': 'sysinfo', 'title': 'Show system info', 'desc': 'Run sysinfo.sh and display summary', 'compat': ['ubuntu'], 'deps': [], 'run_type': 'dry-run'},
            {'key': 'update_clean', 'title': 'System update & clean', 'desc': 'Run update_clean.sh (apt update + autoremove)', 'compat': ['ubuntu'], 'deps': ['apt'], 'run_type': 'confirm-run'},
            {'key': 'firewall', 'title': 'Firewall manager (UFW)', 'desc': 'Launch UFW helper', 'compat': ['ubuntu'], 'deps': ['ufw'], 'run_type': 'confirm-run'},
            {'key': 'resource_monitor', 'title': 'Resource monitor', 'desc': 'Show resource usage (htop/top)', 'compat': ['ubuntu'], 'deps': ['htop'], 'run_type': 'dry-run'},
            {'key': 'ssh_batch', 'title': 'SSH batch runner', 'desc': 'Run ssh_batch for bulk remote commands', 'compat': ['ubuntu'], 'deps': ['ssh'], 'run_type': 'confirm-run'},
        ]
    },
    'yl': {
        'title': 'YL utilities',
        'desc': 'Misc tools and templates.',
        'actions': [
            {'key': 'template_mgr', 'title': 'Template manager', 'desc': 'Manage and apply templates', 'compat': ['ubuntu','windows'], 'deps': [], 'run_type': 'dry-run'},
            {'key': 'cloud_vm', 'title': 'Cloud VM builder', 'desc': 'Prepare cloud VM images or scripts', 'compat': ['ubuntu'], 'deps': [], 'run_type': 'dry-run'},
            {'key': 'deploy_desktop_cleanup', 'title': 'Desktop cleanup helper', 'desc': 'Remove duplicate .desktop entries', 'compat': ['ubuntu'], 'deps': [], 'run_type': 'dry-run'},
        ]
    }
}

def build_menu_from_modules():
    # kept for compatibility; actual module list is created in build_ui
    try:
        if module_frame:
            for w in module_frame.winfo_children():
                w.destroy()
    except NameError:
        pass

def show_module_menu(key):
    meta = EXT_MODULES.get(key)
    if not meta:
        return
    append_output(f"== Module: {meta['title']} ==\n")
    append_output(meta['desc'] + '\n')
    # update info panel
    try:
        info_text.configure(state='normal')
        info_text.delete('1.0', 'end')
        info_text.insert('end', meta['title'] + '\n\n' + meta.get('desc','') + '\n\nActions:\n')
        for a in meta['actions']:
            info_text.insert('end', f" - {a['title']}: {a.get('desc','')}\n")
        info_text.configure(state='disabled')
    except NameError:
        pass

    # show actions as buttons in the actions area
    try:
        for w in actions_frame.winfo_children():
            w.destroy()
    except NameError:
        actions_frame = ttk.Frame(right, padding=6)
        actions_frame.pack(fill='x', pady=4)
    for a in meta['actions']:
        append_output(f" - {a['title']}: {a.get('desc','')}\n")
        compatible = TARGET_SYSTEM in a.get('compat', [])

        # prefer named wrapper ext_{key} if exists
        named = globals().get('ext_' + a['key'])
        if named:
            fn = named
        else:
            # choose wrapper based on run_type
            run_type = a.get('run_type')
            if run_type == 'dry-run':
                fn = lambda act=a: append_output(f"Dry-run: {act['title']}\n")
            elif run_type == 'background-py':
                def make_bg_py(act):
                    def _fn():
                        folder = os.path.join(ROOT, 'ubuntu_file_helper_gui')
                        main_py = os.path.join(folder, 'main.py')
                        if not os.path.exists(main_py):
                            append_output('main.py not found for background-py\n')
                            return
                        append_output(f"Starting Python server for {act['title']}...\n")
                        subprocess.Popen([sys.executable, main_py], cwd=folder)
                        append_output('Started (background).\n')
                    return _fn
                fn = make_bg_py(a)
            elif run_type == 'background-shell':
                def make_bg_sh(act, key=key):
                    def _fn():
                        path = os.path.join(ROOT, key, act['key'] + '.sh')
                        # fallback to named script
                        script = os.path.join(ROOT, key, os.path.basename(path))
                        if not os.path.exists(script):
                            # try main script names
                            if key == 'yeling_super_helper_tui':
                                script = os.path.join(ROOT, key, 'yeling_super_helper_tui.sh')
                        if not os.path.exists(script):
                            append_output(f"Script not found: {script}\n")
                            return
                        if shutil.which('bash') is None:
                            append_output('bash not found; cannot run shell script.\n')
                            return
                        append_output(f"Launching {script} (background)\n")
                        subprocess.Popen(['bash', script], cwd=os.path.dirname(script))
                    return _fn
                fn = make_bg_sh(a)
            elif run_type == 'confirm-run':
                def make_confirm(act, key=key):
                    def _fn():
                        if messagebox.askyesno('Confirm', f"Run '{act['title']}'? This may perform installs."):
                            append_output(f"Running: {act['title']} (may require sudo)\n")
                            # For safety, just print planned command (dry-run default)
                            append_output('Planned: run the module script with elevated privileges if available.\n')
                    return _fn
                fn = make_confirm(a)
            else:
                fn = lambda act=a: append_output(f"Action: {act['title']} (no-op)\n")
        

        # create button and disable if incompatible
        def make_click(fn, act):
            def _click():
                # check dependencies first
                missing = []
                for dep in act.get('deps', []):
                    if dep and shutil.which(dep) is None:
                        missing.append(dep)

                # build confirmation message
                msg = act.get('desc','') + '\n\n'
                if missing:
                    msg += 'Missing dependencies: ' + ', '.join(missing) + '\n\n'
                    msg += 'You can install them before proceeding. Proceed anyway?'
                else:
                    msg += 'Proceed?'

                # show description in a modal and require confirmation
                if messagebox.askyesno(act['title'], msg):
                    append_output(f'Confirmed: {act["title"]}\n')
                    # prepare tmpdir
                    tmpdir = tempfile.mkdtemp(prefix='multi_tool_run_')
                    tr = TaskRunner(title=act['title'])
                    # run wrapper via TaskRunner.run_with_progress
                    def target(cancel_event=None):
                        try:
                            # if the wrapper expects cancel_event param, call accordingly
                            try:
                                return fn(cancel_event=cancel_event)
                            except TypeError:
                                return fn()
                        finally:
                            # ensure cleanup of temp on normal finish
                            tr.cleanup_temp(tmpdir)

                    tr.run_with_progress(target, tmpdir=tmpdir)
                else:
                    append_output(f'Cancelled by user: {act["title"]}\n')
            return _click

        btn = ttk.Button(actions_frame, text=a['title'], command=make_click(fn, a))
        if not compatible:
            btn.state(['disabled'])
            tooltip = f"Not compatible with target system: {TARGET_SYSTEM}"
            append_output(tooltip + '\n')
        btn.pack(anchor='w', pady=2)


def on_module_select(event):
    # Listbox selection handler
    try:
        idx = modules_listbox.curselection()
        if not idx:
            return
        key = module_keys[idx[0]]
        show_module_menu(key)
    except Exception as e:
        append_output(f'on_module_select error: {e}\n')

    # small helper: check dev tools button
    ttk.Button(left, text=t('check_dev_tools'), command=lambda: thread_fn(check_dev_tools)()).pack(pady=(4,8))


def selected_dev_tools():
    tmpl = template_var.get()
    if tmpl == 'dev':
        return [n for n, _, _, _ in DEV_TOOLS]
    if tmpl == 'min':
        return ['git', 'node', 'code']
    if tmpl == 'full':
        return [n for n, _, _, _ in DEV_TOOLS] + ['npm']
    return []



def run_cmd(cmd, env=None):
    """Run a command and stream output (returns (returncode, output))."""
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env, shell=False)
    except Exception as e:
        return 1, str(e)
    out_lines = []
    for line in proc.stdout:
        out_lines.append(line)
        append_output(line)
    proc.wait()
    return proc.returncode, ''.join(out_lines)


def append_output(text):
    text_widget.configure(state='normal')
    text_widget.insert('end', text)
    text_widget.see('end')
    text_widget.configure(state='disabled')


# --- Extension module wrappers (safe/dry-run or guarded execution) ---
EXT_ROOT = ROOT

def ext_ubuntu_analyze(cancel_event=None):
    # Dry-run analyze: let user pick a file, then show planned steps
    append_output('ubuntu: Analyze files (dry-run)\n')
    f = filedialog.askopenfilename(title='Select file to analyze')
    if not f:
        append_output('No file selected.\n')
        return
    append_output(f'Would analyze: {f}\n')
    append_output('Planned steps:\n - detect extension\n - map to tools\n - propose install commands\n')

def ext_detect_deps(cancel_event=None):
    append_output('ubuntu: Detect extension -> deps mapping (dry-run)\n')
    messagebox.showinfo('Detect deps', 'This will show mapping between file extensions and packages (dry-run).')
    # read file_helper.conf if present
    conf = os.path.join(ROOT, 'ubuntu_file_helper_gui', 'file_helper.conf')
    if os.path.exists(conf):
        with open(conf, 'r', encoding='utf-8') as f:
            append_output(f.read()[:2000] + '\n')
    else:
        append_output('No file_helper.conf found.\n')

def ext_sandbox_run(cancel_event=None):
    append_output('ubuntu: Sandbox run (confirm)\n')
    if messagebox.askyesno('Sandbox run', 'Run selected file in sandbox (dry-run)?'):
        append_output('Would run file in firejail (dry-run).\n')
    else:
        append_output('Sandbox run cancelled.\n')

def ext_ubuntu_start_server(cancel_event=None):
    # Start the bundled Flask report server (if present)
    folder = os.path.join(ROOT, 'ubuntu_file_helper_gui')
    main_py = os.path.join(folder, 'main.py')
    if not os.path.exists(main_py):
        append_output('ubuntu: main.py not found, cannot start server.\n')
        return
    append_output(f'Starting ubuntu_file_helper server from {folder}\n')
    try:
        subprocess.Popen([sys.executable, main_py], cwd=folder)
        append_output('Server started (background). Open http://127.0.0.1:5000 if available.\n')
    except Exception as e:
        append_output(f'Failed to start server: {e}\n')

def ext_yeling_run_tui(cancel_event=None):
    script = os.path.join(ROOT, 'yeling_super_helper_tui', 'yeling_super_helper_tui.sh')
    if not os.path.exists(script):
        append_output('yeling: script not found\n')
        return
    if shutil.which('bash') is None:
        append_output('bash not found on system; cannot run TUI.\n')
        return
    append_output('Launching yeling TUI (in console)\n')
    try:
        subprocess.Popen(['bash', script], cwd=os.path.join(ROOT, 'yeling_super_helper_tui'))
        append_output('yeling TUI started (background).\n')
    except Exception as e:
        append_output(f'Failed to launch yeling TUI: {e}\n')

def ext_auto_install(cancel_event=None):
    messagebox.showinfo('Auto-install', 'This will guide auto-install (dry-run).')
    append_output('yeling: auto-install (dry-run).\n')

def ext_sysinfo(cancel_event=None):
    messagebox.showinfo('Sysinfo', 'Display system info (dry-run).')
    append_output('yeling: sysinfo (dry-run).\n')

def ext_update_clean(cancel_event=None):
    if messagebox.askyesno('Update & Clean', 'Run system update & clean? (dry-run)'):
        append_output('Planned: apt update && apt upgrade && autoremove (dry-run).\n')
    else:
        append_output('Update & clean cancelled.\n')

def ext_firewall(cancel_event=None):
    if messagebox.askyesno('Firewall', 'Open firewall manager? (dry-run)'):
        append_output('Planned: manage UFW rules (dry-run).\n')
    else:
        append_output('Firewall action cancelled.\n')

def ext_resource_monitor(cancel_event=None):
    messagebox.showinfo('Resource monitor', 'This will open resource monitor tools (dry-run).')
    append_output('Planned: run htop/top (dry-run).\n')

def ext_ssh_batch(cancel_event=None):
    if messagebox.askyesno('SSH Batch', 'Run SSH batch? This may execute remote commands. Continue as dry-run?'):
        append_output('Planned: run ssh_batch with provided hosts (dry-run).\n')
    else:
        append_output('SSH batch cancelled.\n')

def ext_yeling_auto_install():
    append_output('yeling: Deploy template (dry-run)\n')
    append_output('Planned: run auto_install with user-provided package or URL.\n')

def ext_yl_template_manager():
    append_output('yl: Template manager (dry-run)\n')

def ext_yl_cloud_vm_builder():
    append_output('yl: Cloud VM builder (dry-run)\n')



def thread_fn(fn):
    def wrapper():
        try:
            fn()
        except Exception as e:
            append_output(f"Error: {e}\n")
    threading.Thread(target=wrapper, daemon=True).start()


# --- Task runner with cancellation and progress UI ---
class TaskRunner:
    def __init__(self, title='Task'):
        self.cancel_event = threading.Event()
        self.proc = None
        self.title = title
        self._progress_root = None

    def _make_progress_window(self):
        self._progress_root = tk.Toplevel()
        self._progress_root.title(self.title)
        self._progress_root.geometry('400x120')
        ttk.Label(self._progress_root, text=self.title).pack(pady=(8,4))
        pb = ttk.Progressbar(self._progress_root, mode='indeterminate')
        pb.pack(fill='x', padx=12, pady=6)
        pb.start(10)
        btn = ttk.Button(self._progress_root, text='Cancel', command=self.cancel)
        btn.pack(pady=(4,8))
        # make modal-ish
        self._progress_root.transient(root)
        self._progress_root.grab_set()
        self._progress_root.protocol('WM_DELETE_WINDOW', self.cancel)

    def cancel(self):
        append_output('Cancel requested\n')
        self.cancel_event.set()
        try:
            if self.proc and self.proc.poll() is None:
                self.proc.terminate()
                time.sleep(0.2)
                if self.proc.poll() is None:
                    self.proc.kill()
        except Exception as e:
            append_output(f'Error killing process: {e}\n')

    def cleanup_temp(self, tmpdir):
        try:
            if os.path.exists(tmpdir):
                shutil.rmtree(tmpdir, ignore_errors=True)
                append_output(f'Cleaned temp dir: {tmpdir}\n')
        except Exception as e:
            append_output(f'Error cleaning temp dir {tmpdir}: {e}\n')

    def run_subprocess(self, cmd, cwd=None):
        # Run subprocess, update append_output, support cancellation
        try:
            self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=cwd)
        except Exception as e:
            append_output(f'Failed to start process: {e}\n')
            return 1
        for line in self.proc.stdout:
            append_output(line)
            if self.cancel_event.is_set():
                append_output('Cancellation detected, terminating process\n')
                try:
                    self.proc.terminate()
                except Exception:
                    pass
                break
        self.proc.wait()
        return self.proc.returncode

    def run_with_progress(self, target_fn, args=(), kwargs=None, tmpdir=None):
        if kwargs is None:
            kwargs = {}
        # create progress UI in main thread
        def start_progress():
            try:
                self._make_progress_window()
            except Exception as e:
                append_output(f'Could not create progress window: {e}\n')

        root.after(10, start_progress)

        # run the target in background
        def runner():
            try:
                ret = target_fn(*args, cancel_event=self.cancel_event, **kwargs)
                append_output(f'Task finished with: {ret}\n')
            except Exception as e:
                append_output(f'Task error: {e}\n')
            finally:
                # cleanup UI
                try:
                    if self._progress_root:
                        self._progress_root.destroy()
                except Exception:
                    pass
                # cleanup temp
                if tmpdir:
                    self.cleanup_temp(tmpdir)

        t = threading.Thread(target=runner, daemon=True)
        t.start()
        return t



def check_system():
    append_output('== System check start ==\n')
    # Python version
    append_output(f'Python: {sys.version}\n')
    # venv
    has_venv = os.path.isdir(os.path.join(ROOT, '.venv'))
    append_output(f"Virtualenv (.venv) present: {has_venv}\n")
    # multi_tool exe
    append_output(f"multi_tool.exe present: {os.path.exists(MULTI_TOOL_EXE)} ({MULTI_TOOL_EXE})\n")
    # netifaces availability
    try:
        import importlib
        spec = importlib.util.find_spec('netifaces')
        append_output(f"netifaces installed: {spec is not None}\n")
    except Exception:
        append_output("netifaces installed: unknown\n")
    append_output('== System check end ==\n')


def create_venv():
    append_output('Creating virtualenv .venv...\n')
    rc, out = run_cmd([sys.executable, '-m', 'venv', '.venv'])
    if rc == 0:
        append_output('Virtualenv created.\n')
    else:
        append_output(f'Failed to create virtualenv: {out}\n')


def install_deps():
    append_output('Installing runtime dependencies (skipping netifaces on Windows)...\n')
    # Use pip to install requirements but skip netifaces
    req_path = os.path.join(ROOT, 'multi_tool', 'requirements.txt')
    if not os.path.exists(req_path):
        append_output('requirements.txt not found in multi_tool.\n')
        return
    with open(req_path, 'r', encoding='utf-8') as f:
        reqs = [l.strip() for l in f if l.strip() and not l.strip().startswith('#')]
    reqs = [r for r in reqs if 'netifaces' not in r]
    # write temporary file
    tmp = os.path.join(ROOT, 'build', 'requirements_no_netifaces.txt')
    os.makedirs(os.path.dirname(tmp), exist_ok=True)
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write('\n'.join(reqs))
    # activate env if present
    py = sys.executable
    if os.path.isdir(os.path.join(ROOT, '.venv')):
        py = os.path.join(ROOT, '.venv', 'Scripts', 'python.exe')
    rc, out = run_cmd([py, '-m', 'pip', 'install', '--upgrade', 'pip'])
    rc, out = run_cmd([py, '-m', 'pip', 'install', '-r', tmp])
    if rc == 0:
        append_output('Dependencies installed.\n')
    else:
        append_output(f'Failed to install deps: {out}\n')


def generate_license():
    append_output('Generating license...\n')
    # Prefer built exe if available
    if os.path.exists(MULTI_TOOL_EXE):
        cmd = [MULTI_TOOL_EXE, 'license', 'generate']
    else:
        cmd = [sys.executable, '-m', 'multi_tool.cli', 'license', 'generate']
    rc, out = run_cmd(cmd)
    append_output(f'rc={rc}\n')


def run_file_helper():
    append_output('Starting file-helper GUI...\n')
    if os.path.exists(MULTI_TOOL_EXE):
        cmd = [MULTI_TOOL_EXE, 'file-helper']
    else:
        cmd = [sys.executable, '-m', 'multi_tool.cli', 'file-helper']
    rc, out = run_cmd(cmd)
    append_output(f'file-helper exited with rc={rc}\n')


def run_vpn_connect():
    append_output('Attempting vpn.connect (dry-run)...\n')
    if os.path.exists(MULTI_TOOL_EXE):
        cmd = [MULTI_TOOL_EXE, 'action', 'run', 'vpn.connect', '--dry-run']
    else:
        cmd = [sys.executable, '-m', 'multi_tool.cli', 'action', 'run', 'vpn.connect', '--dry-run']
    rc, out = run_cmd(cmd)
    append_output(f'vpn.connect rc={rc}\n')


def on_run_selected():
    selections = []
    if var_check.get():
        selections.append(('System check', check_system))
    if var_venv.get():
        selections.append(('Create virtualenv', create_venv))
    if var_deps.get():
        selections.append(('Install dependencies', install_deps))
    if var_license.get():
        selections.append(('Generate license', generate_license))
    if var_file_helper.get():
        selections.append(('Run file-helper', run_file_helper))
    if var_vpn.get():
        selections.append(('VPN connect (dry-run)', run_vpn_connect))

    if not selections:
        messagebox.showinfo('提示', '请先选择要执行的功能')
        return

    append_output('=== Running selected tasks ===\n')
    for name, fn in selections:
        append_output(f'--- {name} ---\n')
        try:
            fn()
        except Exception as e:
            append_output(f'Error running {name}: {e}\n')
    append_output('=== Finished ===\n')


# NOTE: tk.Variable instances must be created after root exists; they'll be
# created inside build_ui().


# --- UI build / language switch ---
def set_lang(lang):
    global LANG
    LANG = lang
    root.title(t('title'))
    # clear top-level children and rebuild
    for w in root.winfo_children():
        w.destroy()
    build_ui()


def build_ui():
    global frm, left, right, text_widget, module_frame
    global var_check, var_venv, var_deps, var_license, var_file_helper, var_vpn, template_var

    # create UI-linked variables (create after root exists)
    var_check = tk.BooleanVar(value=True)
    var_venv = tk.BooleanVar(value=False)
    var_deps = tk.BooleanVar(value=False)
    var_license = tk.BooleanVar(value=False)
    var_file_helper = tk.BooleanVar(value=False)
    var_vpn = tk.BooleanVar(value=False)
    template_var = tk.StringVar(value='dev')
    frm = ttk.Frame(root, padding=12)
    frm.pack(fill='both', expand=True)

    top_frame = ttk.Frame(frm)
    top_frame.pack(fill='x')
    ttk.Label(top_frame, text=t('language_label') + ':').pack(side='left')
    lang_var = tk.StringVar(value=LANG)
    lang_menu = ttk.OptionMenu(top_frame, lang_var, LANG, 'zh', 'en', command=lambda v: set_lang(v))
    lang_menu.pack(side='left', padx=6)
    # target system selector
    ttk.Label(top_frame, text='Target:').pack(side='left', padx=(12,0))
    target_var = tk.StringVar(value=TARGET_SYSTEM)
    tgt_menu = ttk.OptionMenu(top_frame, target_var, TARGET_SYSTEM, 'windows', 'ubuntu', command=lambda v: set_target_system(v))
    tgt_menu.pack(side='left', padx=6)

    # left: main actions and templates (existing)
    left = ttk.Frame(frm)
    left.pack(side='left', fill='y')

    # middle: module list + info
    mid = ttk.Frame(frm)
    mid.pack(side='left', fill='both', expand=False, padx=(8,8))

    # right: actions and output
    right = ttk.Frame(frm)
    right.pack(side='right', fill='both', expand=True)

    # Checkboxes and actions
    ttk.Label(left, text=t('select_actions')).pack(anchor='w')
    ttk.Checkbutton(left, text=t('system_check'), variable=var_check).pack(anchor='w')
    ttk.Checkbutton(left, text=t('create_venv'), variable=var_venv).pack(anchor='w')
    ttk.Checkbutton(left, text=t('install_deps'), variable=var_deps).pack(anchor='w')
    ttk.Checkbutton(left, text=t('generate_license'), variable=var_license).pack(anchor='w')
    ttk.Checkbutton(left, text=t('start_file_helper'), variable=var_file_helper).pack(anchor='w')
    ttk.Checkbutton(left, text=t('vpn_connect'), variable=var_vpn).pack(anchor='w')

    ttk.Button(left, text=t('run_selected'), command=lambda: thread_fn(on_run_selected)()).pack(pady=8)

    ttk.Label(left, text=t('templates')).pack(anchor='w', pady=(10,0))
    ttk.Radiobutton(left, text=t('template_dev'), variable=template_var, value='dev').pack(anchor='w')
    ttk.Radiobutton(left, text=t('template_min'), variable=template_var, value='min').pack(anchor='w')
    ttk.Radiobutton(left, text=t('template_full'), variable=template_var, value='full').pack(anchor='w')

    ttk.Button(left, text=t('recommend_install'), command=lambda: thread_fn(lambda: recommend_install_selected(selected_dev_tools()))()).pack(pady=8)

    # Modules list (middle)
    ttk.Label(mid, text=t('modules')).pack(anchor='w')
    modules_listbox = tk.Listbox(mid, height=12)
    modules_listbox.pack(fill='y')
    module_keys = []
    for k, meta in EXT_MODULES.items():
        modules_listbox.insert('end', meta['title'])
        module_keys.append(k)
    modules_listbox.bind('<<ListboxSelect>>', on_module_select)

    # module info panel
    info_text = scrolledtext.ScrolledText(mid, height=10, width=40, state='disabled')
    info_text.pack(fill='both', expand=False, pady=(6,0))

    # Actions panel (right)
    actions_frame = ttk.Frame(right, padding=6)
    actions_frame.pack(fill='x', pady=4)

    # Output area (bottom-right)
    text_widget = scrolledtext.ScrolledText(right, state='disabled')
    text_widget.pack(fill='both', expand=True)

    # initial info
    append_output('multi_tool Installer / Repair\n')
    append_output('Root: ' + ROOT + '\n')

    # build extension module menu
    build_menu_from_modules()


if __name__ == '__main__':
    root = tk.Tk()
    root.title(t('title'))
    root.geometry('820x560')
    build_ui()
    root.mainloop()

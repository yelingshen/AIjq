Graphical installer/repair build instructions

This project includes `installer_app.py`, a small Tkinter-based GUI that
lets users run common maintenance tasks (system checks, create venv,
install deps, generate license, start file-helper GUI, run VPN dry-run).

How to build the installer exe (Windows)

1. Ensure you have a working Python installation and Git repo checked out.
2. From the repository root run:

```powershell
.\build_installer.ps1
```
Release packaging (zip containing source, linux launcher, windows exe)

We provide helper scripts to create a release zip that contains:
- `source/` — full source code of the repo
- `multi_tool.exe` — the Windows executable (if present in `dist/`)
- `run_multi_tool_ubuntu.sh` — a small launcher script for Ubuntu

From repository root (Windows PowerShell):

```powershell
.
\scripts\package_release.ps1
```

From repository root (Linux / WSL):

```bash
./scripts/package_release.sh
```

After creating the ZIP, unpacking it produces a folder with the `source/` tree,
the ubuntu launcher and a windows exe (if you built it earlier).

Packaging strategy notes & recommendations
- Include both source and platform binaries so users can run from source on
  systems where building an exe is not ideal (Ubuntu), and use prebuilt exe on
  Windows.
- Test the ubuntu launcher by running the included `run_multi_tool_ubuntu.sh` in
  a clean environment (python3 + virtualenv). The launcher expects Python 3 and
  will run `python3 -m multi_tool.cli`.
- For reliability, the packaging script intentionally excludes virtualenv
  artifacts and build/ directories.

Next steps for robustness (suggestions)
- Add automated smoke tests that run a few non-destructive commands from the
  packaged app to validate the runtime environment.
- Add a small installation script that can optionally install system deps
  required on Ubuntu (e.g., `python3-tk`, `htop`) to make the launcher more
  user-friendly.


What the script does

- Ensures a virtualenv exists and activates it.
- Installs PyInstaller.
- If `dist\multi_tool.exe` is not present, it runs `build_windows.ps1` to build the CLI exe.
- Runs PyInstaller to create `dist_installer\multi_tool_installer.exe` and embeds `dist\multi_tool.exe` as a data file inside the installer.

Runtime behavior

- When users run `multi_tool_installer.exe`, the GUI appears. The embedded `multi_tool.exe` is extracted to a temporary location at runtime and invoked when the user chooses the related actions.

Notes and caveats

- The installer GUI depends on Tkinter which is normally present in standard Python Windows installers. If Tkinter is missing on a target, provide instructions to install the appropriate Tcl/Tk runtime.
- Some actions (VPN configuration, system-level changes) require administrator privileges. The installer does not automatically elevate; instruct users to run the installer as Administrator when needed.
- `netifaces` is intentionally skipped on Windows builds to avoid requiring Visual C++ Build Tools. If you need `netifaces` functionality on Windows, either:
  - Install Visual C++ Build Tools and then install `netifaces` in the virtualenv, or
  - Replace `netifaces` usage with a pure-Python alternative (e.g., `psutil.net_if_addrs`).

Security

- The installer will not include any secrets. License generation writes to the user's home by default; instruct users where to place license files if required.

Customization

- You can edit `installer_app.py` to expose more actions or to change defaults.
- To include additional resources with PyInstaller, update the `--add-data` argument in `build_installer.ps1` or a generated spec file.

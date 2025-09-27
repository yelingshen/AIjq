#!/usr/bin/env python3
"""Check for system-level prerequisites and print install suggestions.

This script does NOT perform package manager installs by default. It detects
common missing pieces (python3-venv/ensurepip) and prints the commands a user
should run. If run with --auto and with sufficient privileges it will attempt
to install using apt (Debian/Ubuntu)."""
import argparse
import shutil
import sys
import subprocess

def check_venv_available():
    # Check if ensurepip/venv support is available
    try:
        import venv
        return True
    except Exception:
        return False

def has_command(cmd):
    return shutil.which(cmd) is not None

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--auto', action='store_true', help='Attempt to auto-install using apt (requires sudo)')
    args = p.parse_args()

    missing = []
    if not check_venv_available():
        missing.append('python3-venv')
    if not has_command('git'):
        missing.append('git')

    if missing:
        print('Missing system packages detected:')
        for m in missing:
            print('  -', m)
        print('\nSuggested install commands (Debian/Ubuntu):')
        print('  sudo apt update')
        print('  sudo apt install -y ' + ' '.join(missing))
        if args.auto:
            # attempt to install
            try:
                print('\nAttempting to install via apt...')
                subprocess.check_call(['sudo', 'apt', 'update'])
                subprocess.check_call(['sudo', 'apt', 'install', '-y'] + missing)
                print('Install attempt finished. Re-run the starter after this.')
            except Exception as e:
                print('Auto-install failed:', e)
                sys.exit(2)
        else:
            sys.exit(1)
    else:
        print('All system prereqs appear present.')
        sys.exit(0)

if __name__ == '__main__':
    main()

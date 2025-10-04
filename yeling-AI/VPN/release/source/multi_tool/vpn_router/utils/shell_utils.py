import os
import subprocess

def check_license():
    # Example license check logic
    license_file = os.path.expanduser("~/.multi_tool_license")
    if not os.path.exists(license_file):
        return False
    with open(license_file, 'r') as f:
        license_key = f.read().strip()
    # Replace with actual license validation logic
    return license_key == "VALID_LICENSE_KEY"

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(result.stderr)
    return result.stdout.strip()

def generate_license(key='VALID_LICENSE_KEY', path=None):
    if path is None:
        path = os.path.expanduser('~/.multi_tool_license')
    with open(path, 'w') as f:
        f.write(key)
    return path


def license_status(path=None):
    license_file = path or os.path.expanduser('~/.multi_tool_license')
    if not os.path.exists(license_file):
        return False, 'License file not found'
    with open(license_file, 'r') as f:
        license_key = f.read().strip()
    if license_key == 'VALID_LICENSE_KEY':
        return True, 'License valid'
    return False, 'License invalid'

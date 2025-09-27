"""Lightweight import smoke-test for project proxies and key modules.

This script intentionally does not start servers or install packages. It only
attempts to import modules and records success/failure. It writes a JSON report
into `scripts/import_report.json`.
"""
import importlib
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
REPORT_PATH = PROJECT_ROOT / 'scripts' / 'import_report.json'

MODULES = [
    'cli.cli',
    'services.server',
    'services.server_minimal',
    'services.assistant',
    'scanners.dispatcher',
    'scanners.file_scanner',
    'scanners.complexity_scanner',
    'scanners.dependency_scanner',
    'scanners.security_scanner',
    'utils.model_loader',
    'utils.memory_cache',
    'utils.responder',
    'utils.context_manager',
    'utils.report_generator',
    'ai.server',
    'ai.server_minimal',
    'ai.start_ai_assistant',
]

results = {}
for m in MODULES:
    try:
        importlib.import_module(m)
        results[m] = {'ok': True}
        print('OK', m)
    except Exception as e:
        results[m] = {'ok': False, 'error': str(e)}
        print('FAIL', m, str(e))

REPORT_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False))
print('\nWrote import report to', REPORT_PATH)

# Exit non-zero if any import failed so CI can detect failures.
any_failed = any(not v.get('ok', False) for v in results.values())
if any_failed:
    print('[ERROR] One or more module imports failed. See import_report.json for details.')
    sys.exit(1)
else:
    print('[INFO] All imports succeeded.')
    sys.exit(0)

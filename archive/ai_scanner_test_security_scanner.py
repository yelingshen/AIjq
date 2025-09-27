import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scanner.security_scanner import SecurityScanner

def test_run_detects_secrets(tmp_path):
    # 创建测试文件
    test_file = tmp_path / "test_secret.py"
    test_file.write_text("api_key = '12345678ABCDEFG'\nsecret_key = 'ABCDEFGH87654321'\nsk_live_ABCDEFGH12345678\n")
    scanner = SecurityScanner()
    result = scanner.run([str(tmp_path)], None, None)
    assert any('api_key' in f['match'] for f in result['security_findings'])
    assert any('secret_key' in f['match'] for f in result['security_findings'])
    assert any('sk_live_' in f['match'] for f in result['security_findings'])
    assert str(test_file) in result['files']

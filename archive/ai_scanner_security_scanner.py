"""Search for secret-like patterns in files."""
import re, os
from pathlib import Path
class SecurityScanner:
    name = 'security_scanner'
    PATTERNS = [
        re.compile(r"(?i)api[_-]?key\s*[:=]\s*['\"]([0-9a-zA-Z_\-]{8,})['\"]"),
        re.compile(r"(?i)secret[_-]?key\s*[:=]\s*['\"]([0-9a-zA-Z_\-]{8,})['\"]"),
        re.compile(r"(?i)sk_live_[0-9a-zA-Z_]{8,}")
    ]
    def run(self, paths, cache, settings):
        findings=[]; files=[]
        for p in paths:
            for root,dirs,fs in os.walk(p):
                for f in fs:
                    if any(f.endswith(ext) for ext in ('.py','.env','.yaml','.yml','.ini','.txt')):
                        fp = str(Path(root)/f); files.append(fp)
                        try:
                            txt = open(fp,'r',encoding='utf-8',errors='ignore').read()
                        except Exception:
                            continue
                        for pat in self.PATTERNS:
                            for m in pat.finditer(txt):
                                findings.append({'file':fp,'match':m.group(0),'pattern':pat.pattern})
        return {'files':files,'security_findings':findings,'nodes':[],'edges':[]}
def register(): return SecurityScanner()
if __name__ == "__main__":
    print("SecurityScanner 仅作为模块使用，不建议直接运行。")

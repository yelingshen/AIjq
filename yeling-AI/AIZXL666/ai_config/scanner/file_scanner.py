"""List files and basic metadata under given paths."""
import os, hashlib
from pathlib import Path
class FileScanner:
    name = 'file_scanner'
    def _hash(self, path):
        try:
            h = hashlib.sha256()
            with open(path,'rb') as f:
                while True:
                    b = f.read(8192)
                    if not b: break
                    h.update(b)
            return h.hexdigest()
        except Exception:
            return None
    def run(self, paths, cache, settings):
        files=[]; meta={}
        exts = settings.get('file_types') if settings else None
        for p in paths:
            for root,dirs,fs in os.walk(p):
                for f in fs:
                    fp = str(Path(root)/f)
                    if exts and not any(fp.endswith(e) for e in exts): continue
                    files.append(fp)
                    meta[fp] = {'size': Path(fp).stat().st_size if Path(fp).exists() else 0, 'hash': self._hash(fp)}
        return {'files':files,'meta':meta,'nodes':[],'edges':[]}
def register(): return FileScanner()
if __name__ == "__main__":
    print("FileScanner 仅作为模块使用，不建议直接运行。")

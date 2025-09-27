"""Estimate simple complexity scores per Python file."""
import ast, time, os
from pathlib import Path
class ComplexityScanner:
    name = 'complexity_analyzer'
    def score_file(self, fp):
        try:
            src = open(fp, 'r', encoding='utf-8').read()
        except Exception:
            return {'file':fp,'error':'read'}
        try:
            tree = ast.parse(src)
            funcs = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
            branches = len([n for n in ast.walk(tree) if isinstance(n, (ast.If, ast.For, ast.While))])
            # heuristic score
            score = funcs*2 + branches
            time.sleep(0.005)
            return {'file':fp,'score':score}
        except Exception as e:
            return {'file':fp,'error':str(e)}
    def run(self, paths, cache, settings):
        files=[]
        for p in paths:
            for root,dirs,fs in os.walk(p):
                for f in fs:
                    if f.endswith('.py'):
                        files.append(str(Path(root)/f))
        out=[]
        for fp in files:
            cached = cache.get('complexity:'+fp) if cache else None
            if cached is not None:
                out.append(cached); continue
            r = self.score_file(fp)
            if cache: cache.set('complexity:'+fp, r, ttl=settings.get('scanner',{}).get('heavy_ttl',300))
            out.append(r)
        return {'files':files,'complexity':out,'nodes':[],'edges':[]}
def register(): return ComplexityScanner()
if __name__ == "__main__":
    print("ComplexityScanner 仅作为模块使用，不建议直接运行。")

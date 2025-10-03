"""Parse imports from Python files to build simple dependency mapping."""
import ast, os
from pathlib import Path
import subprocess, sys
class DependencyScanner:
    name = 'dependency_parser'
    def run(self, paths, cache, settings):
        deps={}; files=[]; missing=set()
        for p in paths:
            for root,dirs,fs in os.walk(p):
                for f in fs:
                    if f.endswith('.py'):
                        fp = str(Path(root)/f); files.append(fp)
                        try:
                            tree = ast.parse(open(fp,'r',encoding='utf-8').read())
                            imports = []
                            for n in ast.walk(tree):
                                if isinstance(n, ast.Import):
                                    for name in n.names:
                                        imports.append(name.name)
                                elif isinstance(n, ast.ImportFrom):
                                    if n.module: imports.append(n.module)
                            deps[fp] = imports
                            # 检查依赖是否已安装
                            for mod in imports:
                                try:
                                    __import__(mod)
                                except ImportError:
                                    missing.add(mod)
                        except Exception:
                            deps[fp] = []
        # 自动安装缺失依赖
        for mod in missing:
            try:
                print(f'[依赖补齐] 自动安装: {mod}')
                subprocess.run([sys.executable, '-m', 'pip', 'install', mod])
            except Exception as e:
                print(f'[依赖补齐] 安装失败: {mod}, 错误: {e}')
        return {'files':files,'dependencies':deps,'missing':list(missing),'nodes':[],'edges':[]}
def register(): return DependencyScanner()
if __name__ == "__main__":
    print("DependencyScanner 仅作为模块使用，不建议直接运行。")

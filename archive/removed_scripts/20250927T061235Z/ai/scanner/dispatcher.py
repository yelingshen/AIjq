"""Pluginized scanner loader + async runner using ThreadPoolExecutor for heavy tasks."""
import importlib.util, asyncio, os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
class ScannerDispatcher:
    def __init__(self, scanner_folder:Path, cache=None, settings=None):
        self.scanner_folder = Path(scanner_folder)
        self.cache = cache
        self.settings = settings or {}
        self.plugins = {}
        self.plugin_files = set()

    def find_gpt_folder(start_dir=None):
        if start_dir is None:
            start_dir = Path(__file__).resolve().parent
        for parent in [start_dir] + list(start_dir.parents):
            gpt_dir = parent / 'GPT'
            if gpt_dir.exists() and gpt_dir.is_dir():
                return gpt_dir
        return None

    GPT_DIR = find_gpt_folder()
    async def load_plugins(self):
        if not self.scanner_folder.exists(): return
        for p in self.scanner_folder.glob('*.py'):
            if p.stem in ('__init__','dispatcher'): continue
            if p.name in self.plugin_files:
                continue  # 已加载，无需重复
            spec = importlib.util.spec_from_file_location(f'scanner.{p.stem}', str(p))
            mod = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(mod)
                if hasattr(mod,'register'):
                    plug = mod.register()
                    self.plugins[plug.name] = plug
                    self.plugin_files.add(p.name)
            except Exception as e:
                print('plugin load fail', p.name, e)

    def reload_plugin(self, plugin_name):
        """支持热插拔，动态重新加载指定插件"""
        p = self.scanner_folder / f'{plugin_name}.py'
        if not p.exists():
            print(f'plugin {plugin_name} not found')
            return False
        spec = importlib.util.spec_from_file_location(f'scanner.{plugin_name}', str(p))
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
            if hasattr(mod,'register'):
                plug = mod.register()
                self.plugins[plug.name] = plug
                self.plugin_files.add(p.name)
                print(f'plugin {plugin_name} reloaded')
                return True
        except Exception as e:
            print('plugin reload fail', p.name, e)
        return False
    async def run_all(self, paths, parallel=True):
        loop = asyncio.get_running_loop()
        results = {}
        if parallel:
            with ThreadPoolExecutor(max_workers=self.settings.get('scanner',{}).get('parallel_workers',4)) as ex:
                tasks = [loop.run_in_executor(ex, plug.run, paths, self.cache, self.settings) for plug in self.plugins.values()]
                completed = await asyncio.gather(*tasks, return_exceptions=True)
                for plug, res in zip(self.plugins.values(), completed):
                    if isinstance(res, Exception):
                        results[plug.name] = {'error':str(res)}
                    else:
                        results[plug.name] = res
        else:
            for plug in self.plugins.values():
                try:
                    results[plug.name] = plug.run(paths, self.cache, self.settings)
                except Exception as e:
                    results[plug.name] = {'error':str(e)}
        return results

if __name__ == "__main__":
    print("ScannerDispatcher 仅作为模块使用，不建议直接运行。")

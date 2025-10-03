#!/usr/bin/env python3
"""Entry point: scan fixed workspace, auto-detect model, build context, and optionally start server."""
import os
import sys
from pathlib import Path

# 获取当前脚本所在目录
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
#!/usr/bin/env python3
"""Entry point: scan fixed workspace, auto-detect model, build context, and optionally start server."""
import os
import sys
from pathlib import Path

# 获取当前脚本所在目录
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR.parent))
import asyncio, logging
LOG = logging.getLogger('ai_assistant')
logging.basicConfig(level=logging.INFO)
PROJECT_ROOT = Path(__file__).parent
DEFAULT_WORKSPACE = Path('/home/xiedaima/桌面/GZQ')
from utils.memory_cache import MemoryCache
from scanners.dispatcher import ScannerDispatcher
from ai.context_manager import ContextManager
from ai.model_loader import ModelLoader
from utils.report_generator import ReportGenerator
from utils.structure_visualizer import StructureVisualizer


async def main():
    LOG.info('AI Assistant starting...')
    settings_path = PROJECT_ROOT / 'config' / 'settings.yaml'
    import yaml
    settings = {}
    try:
        with open(settings_path,'r',encoding='utf-8') as f:
            settings = yaml.safe_load(f) or {}
    except Exception as e:
        LOG.warning('Could not load settings.yaml: %s', e)
    cache = MemoryCache(max_items=settings.get('cache',{}).get('max_items',2000),
                        default_ttl=settings.get('cache',{}).get('default_ttl',600))
    # model loader: auto-detect in nomic path if available
    model_loader = ModelLoader(preferred_dir=settings.get('model',{}).get('auto_dir'))
    model = model_loader.load_model()
    if model:
        LOG.info('Model ready: %s', model.get('meta','(unknown)'))
    # dispatcher -> scan
    dispatcher = ScannerDispatcher(scanner_folder=PROJECT_ROOT / 'scanner', cache=cache, settings=settings)
    await dispatcher.load_plugins()
    workspace = Path(settings.get('workspace', DEFAULT_WORKSPACE))
    if not workspace.exists():
        LOG.warning('Workspace %s does not exist; using project root.', workspace)
        workspace = PROJECT_ROOT
    LOG.info('Scanning workspace: %s', workspace)
    scan_results = await dispatcher.run_all(paths=[str(workspace)], parallel=True)
    # build context
    ctxm = ContextManager(cache=cache)
    context = await ctxm.build_context(scan_results, workspace=str(workspace))
    # suggestions (refactor + security combined)
    from ai.refactor_suggester import RefactorSuggester
    suggester = RefactorSuggester()
    suggestions = suggester.suggest(scan_results, context)
    # reports
    report_dir = PROJECT_ROOT / 'reports'
    report_dir.mkdir(exist_ok=True)
    report = ReportGenerator(output_dir=report_dir)
    report.save_markdown('scan_report.md', scan_results, suggestions, context)
    report.save_html('scan_report.html', scan_results, suggestions, context)
    # structure JSON
    vis = StructureVisualizer()
    vis_path = report_dir / 'structure.json'
    with open(vis_path,'w',encoding='utf-8') as fh:
        import json as _json
        fh.write(_json.dumps(vis.to_json(scan_results), indent=2, ensure_ascii=False))
    LOG.info('Reports written to %s', report_dir)
    LOG.info('Done.')


if __name__ == '__main__':
    asyncio.run(main())

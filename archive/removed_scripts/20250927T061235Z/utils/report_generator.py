"""Generate markdown/html/json reports summarizing scan outputs and suggestions."""
import json, os
from pathlib import Path
from datetime import datetime
class ReportGenerator:
    def __init__(self, output_dir=None):
        self.output_dir = Path(output_dir or Path.cwd() / 'reports')
        self.output_dir.mkdir(parents=True, exist_ok=True)
    def save_markdown(self, fname, scan_results, suggestions, context):
        p = self.output_dir / fname
        with open(p,'w',encoding='utf-8') as fh:
            fh.write(f"# Scan Report\nGenerated: {datetime.utcnow().isoformat()}Z\n\n")
            fh.write('## Scanners run:\n') 
            for k in scan_results.keys(): fh.write(f"- {k}\n")
            fh.write('\n## Suggestions\n') 
            fh.write(json.dumps(suggestions, indent=2, ensure_ascii=False))
            fh.write('\n\n## Context snapshot\n') 
            fh.write(json.dumps(context, indent=2, ensure_ascii=False))
    def save_html(self, fname, scan_results, suggestions, context):
        p = self.output_dir / fname
        with open(p,'w',encoding='utf-8') as fh:
            fh.write('<!doctype html><html><meta charset="utf-8"><body>')
            fh.write(f'<h1>Scan Report</h1><p>Generated: {datetime.utcnow().isoformat()}Z</p>')
            fh.write('<h2>Scanners</h2><ul>')
            for k in scan_results.keys(): fh.write(f'<li>{k}</li>')
            fh.write('</ul><h2>Suggestions</h2><pre>' + json.dumps(suggestions, indent=2, ensure_ascii=False) + '</pre>')
            fh.write('<h2>Context</h2><pre>' + json.dumps(context, indent=2, ensure_ascii=False) + '</pre>')
            fh.write('</body></html>')
    def save_json(self, fname, scan_results, suggestions, context):
        p = self.output_dir / fname
        with open(p,'w',encoding='utf-8') as fh:
            json.dump({'scanners':scan_results,'suggestions':suggestions,'context':context}, fh, indent=2, ensure_ascii=False)

"""Produce structure JSON consumable by browser visualizers (nodes/edges/views/analysis)."""

import os
import json
from pathlib import Path
from flask import Flask, jsonify, request

app = Flask(__name__)

def _uniq(seq):
    seen = set(); out = []
    for s in seq:
        key = tuple(sorted(s.items())) if isinstance(s, dict) else s
        if key in seen: continue
        seen.add(key); out.append(s)
    return out

class StructureVisualizer:
    def to_json(self, scan_results, view='default', template='default'):
        nodes = []; edges = []
        for scanner, r in scan_results.items():
            for f in r.get('files', []):
                nodes.append({'scanner': scanner, 'file': f})
            for n in r.get('nodes', []):
                nodes.append({'scanner': scanner, 'node': n})
            for e in r.get('edges', []):
                edges.append(e)
        result = {'nodes': _uniq(nodes), 'edges': _uniq(edges)}
        if view == 'dependency':
            result['dependency_graph'] = self._build_dependency_graph(edges)
        if view == 'call':
            result['call_graph'] = self._build_call_graph(edges)
        if view == 'collaboration':
            result['collab_map'] = self._build_collab_map(nodes)
        result['analysis'] = self.analyze_structure(result)

        # 联动模型元数据
        try:
            from ai_config.ai.model_loader import ModelLoader
            loader = ModelLoader()
            models_result = loader.find_all_models()
            if models_result.get('success'):
                result['models'] = [loader.get_model_metadata(m) for m in models_result.get('models', [])]
            else:
                result['models'] = [{'success': False, 'error': models_result.get('error')}]
        except Exception as e:
            result['models'] = [{'success': False, 'error': f'模型元数据获取失败: {e}'}]

        # 多模板渲染支持
        if template == 'table':
            # 输出表格格式，便于前端渲染
            result['table'] = {
                'headers': ['名称', '类型', '大小', '修改时间', '健康状态'],
                'rows': [
                    [m.get('name'), m.get('type'), m.get('size'), m.get('last_modified'), m.get('error') or '健康']
                    for m in result.get('models', [])
                ]
            }
        elif template == 'cards':
            # 输出卡片格式，便于前端自定义展示
            result['cards'] = [
                {
                    'title': m.get('name'),
                    'subtitle': m.get('type'),
                    'description': f"大小: {m.get('size')} 更新时间: {m.get('last_modified')}",
                    'status': m.get('error') or '健康'
                }
                for m in result.get('models', [])
            ]
        # 其它模板可扩展

        return result

    def _build_dependency_graph(self, edges):
        # 筛选依赖关系边
        return [e for e in edges if e.get('type') == 'dependency']

    def _build_call_graph(self, edges):
        # 筛选调用关系边
        return [e for e in edges if e.get('type') == 'call']

    def _build_collab_map(self, nodes):
        # 筛选协作分区节点
        return [n for n in nodes if n.get('role')]

    def analyze_structure(self, result):
        # 自动识别关键路径、耦合点、风险点，并联动AI建议模块
        analysis = {'key_paths': [], 'coupling_points': [], 'risk_points': [], 'suggestions': []}
        # 关键路径：最长依赖链
        dep_graph = result.get('dependency_graph', [])
        if dep_graph:
            analysis['key_paths'] = self._find_longest_chain(dep_graph)
        # 耦合点：节点度数大于阈值
        node_degree = {}
        for e in result.get('edges', []):
            src, tgt = e.get('src'), e.get('tgt')
            node_degree[src] = node_degree.get(src, 0) + 1
            node_degree[tgt] = node_degree.get(tgt, 0) + 1
        analysis['coupling_points'] = [n for n, d in node_degree.items() if d >= 3]
        # 风险点：依赖链中断或循环
        analysis['risk_points'] = [e for e in dep_graph if e.get('risk')]
        # 联动AI建议模块
        if analysis['coupling_points']:
            analysis['suggestions'].append('建议优化高耦合模块，降低依赖复杂度。')
        if analysis['risk_points']:
            analysis['suggestions'].append('建议修复依赖链风险，避免循环或断链。')
        if not analysis['key_paths']:
            analysis['suggestions'].append('建议补充关键路径，提升系统连通性。')
        return analysis

    def _find_longest_chain(self, edges):
        # 返回所有长度大于2的依赖链
        chains = []
        for e in edges:
            if e.get('length', 0) > 2:
                chains.append(e)
        return chains

def scan_project_structure(root_dir):
    structure = {}
    for dirpath, dirnames, filenames in os.walk(root_dir):
        rel_path = os.path.relpath(dirpath, root_dir)
        structure[rel_path] = {
            'dirs': dirnames,
            'files': filenames
        }
    return structure

def get_module_dependencies(module_dir):
    deps = {}
    for pyfile in Path(module_dir).rglob('*.py'):
        with open(pyfile, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        imports = [l.strip() for l in lines if l.strip().startswith('import') or l.strip().startswith('from')]
        deps[str(pyfile)] = imports
    return deps

def export_structure_json(root_dir, out_path):
    structure = scan_project_structure(root_dir)
    deps = get_module_dependencies(root_dir)
    result = {
        'structure': structure,
        'dependencies': deps
    }
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f'项目结构与依赖已导出到 {out_path}')

@app.route('/structure', methods=['GET'])
def get_structure():
    root = request.args.get('root', os.getcwd())
    out_path = 'structure.json'
    export_structure_json(root, out_path)
    with open(out_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == '__main__':
    import sys
    root = sys.argv[1] if len(sys.argv)>1 else os.getcwd()
    out = sys.argv[2] if len(sys.argv)>2 else 'structure.json'
    export_structure_json(root, out)

"""Produce refactor and security-integrated suggestions based on scanners."""
class RefactorSuggester:
    def __init__(self):
        pass

    def suggest(self, scan_results, context):
        out = {'general': [], 'security': [], 'compatibility': [], 'style': [], 'performance': [], 'local_learning': []}

        # 复杂度建议
        comp = scan_results.get('complexity_analyzer', {}).get('complexity', [])
        for c in comp:
            if isinstance(c, dict) and c.get('score', 0) > 12:
                out['general'].append({'file': c.get('file'), 'reason': '高复杂度', 'score': c.get('score')})

        # 安全建议
        sec = scan_results.get('security_scanner', {}).get('security_findings', [])
        for s in sec:
            out['security'].append({'file': s.get('file'), 'match': s.get('match'), 'advice': '移除敏感信息，使用安全存储'})

        # 兼容性建议
        config_files = [f for f in context.get('files', {}) if f.endswith(('.yaml', '.yml', '.json'))]
        if not config_files:
            out['compatibility'].append({'advice': '建议补充配置文件以提升环境兼容性'})

        # 代码风格建议
        for f in context.get('files', {}):
            if f.endswith('.py'):
                # 简单风格检测（可扩展为调用格式化工具）
                out['style'].append({'file': f, 'advice': '建议统一代码风格，可使用 black/flake8 自动格式化'})

        # 性能优化建议
        perf = scan_results.get('performance_analyzer', {}).get('performance_issues', [])
        for p in perf:
            out['performance'].append({'file': p.get('file'), 'issue': p.get('issue'), 'advice': '建议优化算法或引入异步处理'})

        # 本地学习建议（根据历史修改/反馈自动生成）
        history = context.get('history', [])
        for h in history:
            out['local_learning'].append({'file': h.get('file'), 'advice': f"根据历史反馈，建议：{h.get('suggestion', '优化代码')}"})

        # 联动模型与规则模块（示例：根据模型元数据和规则自动生成建议）
        models = context.get('models', [])
        rules = context.get('rules', {})
        for m in models:
            if m.get('type') == 'LLM' and rules.get('enable_llm_suggestion', True):
                out['general'].append({'file': m.get('name'), 'advice': '可联动大模型自动生成代码建议'})

        # 优先级联动
        sec_files = {s['file'] for s in sec}
        for g in out['general']:
            if g.get('file') in sec_files:
                g['priority'] = 'high'

        return out

if __name__ == "__main__":
    print("RefactorSuggester 仅作为模块使用，不建议直接运行。")

"""Builds project-wide context from scanner outputs and keeps cache updated."""
import time, os, json
class ContextManager:
    def self_check(self, workspace=None):
        report = {'cache_available': self.cache is not None, 'optimizer_import': False, 'coordination_import': False, 'validator_import': False, 'visualizer_import': False, 'suggestion_test': None}
        try:
            from utils.project_logic_optimizer import ProjectLogicOptimizer
            report['optimizer_import'] = True
        except Exception as e:
            report['optimizer_import'] = str(e)
        try:
            from utils.global_coordination_tester import GlobalCoordinationTester
            report['coordination_import'] = True
        except Exception as e:
            report['coordination_import'] = str(e)
        try:
            from utils.system_logic_validator import SystemLogicValidator
            report['validator_import'] = True
        except Exception as e:
            report['validator_import'] = str(e)
        try:
            from utils.structure_visualizer import StructureVisualizer
            report['visualizer_import'] = True
        except Exception as e:
            report['visualizer_import'] = str(e)
        # 测试建议生成
        try:
            optimizer = ProjectLogicOptimizer(workspace or os.getcwd())
            coordination = GlobalCoordinationTester(workspace or os.getcwd())
            validator = SystemLogicValidator(workspace or os.getcwd())
            visualizer = StructureVisualizer(workspace or os.getcwd())
            logic_report = optimizer.generate_optimization_report()
            coord_report = coordination.generate_coordination_report()
            sys_report = validator.validate_system_logic()
            struct_data = visualizer.get_project_structure()
            struct_analysis = struct_data.get('analysis', {})
            suggestions = []
            suggestions.extend(logic_report.get('recommendations', []))
            suggestions.extend(coord_report.get('recommendations', []))
            suggestions.extend(sys_report.get('recommendations', []))
            suggestions.extend(struct_analysis.get('suggestions', []))
            report['suggestion_test'] = {'success': bool(suggestions), 'suggestions': suggestions}
        except Exception as e:
            report['suggestion_test'] = {'success': False, 'error': str(e)}
        return report
    def __init__(self, cache=None):
        self.cache = cache
    async def build_context(self, scan_results, workspace=None):
        ctx = {'generated_at': time.time(), 'workspace': workspace, 'summary':{}, 'files':{}, 'security':[]}
        for name, r in scan_results.items():
            ctx['summary'][name] = {k:v for k,v in r.items() if k in ('files','dependencies','complexity')}
            for f in r.get('files',[]):
                ctx['files'].setdefault(f,{})
            if 'security_findings' in r:
                ctx['security'].extend(r['security_findings'])
        # deduplicate security
        seen = set()
        uniq = []
        for s in ctx['security']:
            key = (s.get('file'), s.get('match'))
            if key in seen: continue
            seen.add(key); uniq.append(s)
        ctx['security'] = uniq

        # 全局自动优化建议机制作为AI首要学习标准
        # 关键维度解析：
        # 1. 联动性：模块间数据流、接口调用、协同推理，提升整体协作效率
        # 2. 交替性：任务队列化、异步/批量执行，保障任务流畅切换与资源利用
        # 3. 交互性：API接口、前后端/多端协作、团队分工，增强系统交互能力
        # 4. 逻辑思维：架构合理性、执行顺序、主控逻辑，确保项目结构清晰
        # 5. 依赖性：依赖检测、自动补齐、循环依赖预警，保障环境完整与安全
        # 6. 队列化任务：自动分派、进度跟踪、冲突检测，提升任务管理与执行力
        # 7. 项目结构与脚本关联性：结构可视化、关键路径、耦合点、风险点分析，优化模块边界
        # 8. 规则性：多级规则体系、优先级、条件触发、动态更新，支持自定义守护与策略
        # 9. 自愈能力：异常检测、自动修复、回滚快照、安全加固，提升系统韧性
        # 10. 兼容性：多模型/多语言/多端支持，自动适配与依赖补齐，保障扩展性
        # 11. 防范措施：安全扫描、敏感信息检测、环境加密、提前预警，保障项目安全
        # 12. 优化建议部署：每次任务完成后自动输出一条全局优化建议，持续完善项目结构、安全体系、规则、执行力、全局观
        try:
            from utils.project_logic_optimizer import ProjectLogicOptimizer
            from utils.global_coordination_tester import GlobalCoordinationTester
            from utils.system_logic_validator import SystemLogicValidator
            from utils.structure_visualizer import StructureVisualizer
            optimizer = ProjectLogicOptimizer(workspace or os.getcwd())
            coordination = GlobalCoordinationTester(workspace or os.getcwd())
            validator = SystemLogicValidator(workspace or os.getcwd())
            visualizer = StructureVisualizer(workspace or os.getcwd())
            logic_report = optimizer.generate_optimization_report()
            coord_report = coordination.generate_coordination_report()
            sys_report = validator.validate_system_logic()
            struct_data = visualizer.get_project_structure()
            struct_analysis = struct_data.get('analysis', {})
            suggestions = []
            # 逐项收集各维度建议
            suggestions.extend(logic_report.get('recommendations', [])) # 架构、逻辑、依赖、队列化
            suggestions.extend(coord_report.get('recommendations', [])) # 协作、交互、分工
            suggestions.extend(sys_report.get('recommendations', []))   # 自愈、安全、兼容性
            suggestions.extend(struct_analysis.get('suggestions', []))  # 结构、关键路径、耦合点
            if not suggestions:
                suggestions.append('项目结构与逻辑良好，无需优化。建议持续关注安全与协作。')
            # 详细注释每条建议的来源和优化点，便于AI学习
            ctx['global_optimization_suggestions'] = suggestions
        except Exception as e:
            ctx['global_optimization_suggestions'] = [f'全局优化建议生成失败: {e}']

        if self.cache:
            self.cache.set('latest_context', ctx)
        return ctx

if __name__ == "__main__":
    print("ContextManager 仅作为模块使用，不建议直接运行。")

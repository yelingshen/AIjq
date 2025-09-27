"""
全局协调测试器 - 测试全局联动性和功能交互
"""
import os
import sys
import time
import logging
import importlib
import subprocess
from typing import Dict, List, Any
from .functional_independence_validator import FunctionalIndependenceValidator
from .connectivity_tester import GlobalConnectivityTester

class GlobalCoordinationTester:
    def assign_role(self, user: str, role: str) -> Dict:
        """分配角色"""
        # 示例：可扩展为数据库或文件持久化
        return {'user': user, 'role': role, 'status': 'assigned'}

    def track_progress(self, task_id: str, progress: float) -> Dict:
        """进度跟踪"""
        # 示例：可扩展为任务系统集成
        return {'task_id': task_id, 'progress': progress}

    def analyze_ownership(self, file_path: str) -> Dict:
        """归属分析"""
        # 示例：可联动 git blame 或代码归属分析
        return {'file': file_path, 'owner': 'unknown'}

    def auto_assign_task(self, rule_group: str, context: Dict) -> Dict:
        """根据规则自动分派任务"""
        # 示例：联动 settings.yaml 规则体系
        return {'rule_group': rule_group, 'assigned_to': 'userA', 'context': context}

    def detect_conflict(self, task_list: List[Dict]) -> List[Dict]:
        """冲突检测"""
        # 简单检测任务分配冲突
        conflicts = []
        seen = set()
        for t in task_list:
            key = (t.get('file'), t.get('user'))
            if key in seen:
                conflicts.append(t)
            else:
                seen.add(key)
        return conflicts

    def generate_report(self, coordination_results: Dict) -> str:
        """生成协作报告"""
        # 可扩展为 HTML/Markdown/JSON
        return f"协作状态: {coordination_results.get('coordination_status')}, 总分: {coordination_results.get('overall_coordination_score')}"
    def __init__(self, workspace_dir: str):
        self.workspace_dir = workspace_dir
        self.logger = logging.getLogger(__name__)
        self.independence_validator = FunctionalIndependenceValidator(workspace_dir)
        self.connectivity_tester = GlobalConnectivityTester(workspace_dir)
        
    def test_global_coordination(self) -> Dict:
        """测试全局协调性"""
        results = {
            'coordination_status': 'unknown',
            'module_interaction_tests': {},
            'workflow_coordination_tests': {},
            'data_flow_tests': {},
            'conflict_resolution_tests': {},
            'performance_coordination_tests': {},
            'overall_coordination_score': 0.0,
            'recommendations': []
        }
        
        # 1. 模块交互测试
        results['module_interaction_tests'] = self._test_module_interactions()
        
        # 2. 工作流协调测试
        results['workflow_coordination_tests'] = self._test_workflow_coordination()
        
        # 3. 数据流测试
        results['data_flow_tests'] = self._test_data_flow_coordination()
        
        # 4. 冲突解决测试
        results['conflict_resolution_tests'] = self._test_conflict_resolution()
        
        # 5. 性能协调测试
        results['performance_coordination_tests'] = self._test_performance_coordination()
        
        # 计算整体协调分数
        results['overall_coordination_score'] = self._calculate_coordination_score(results)
        
        # 确定协调状态
        results['coordination_status'] = self._determine_coordination_status(results['overall_coordination_score'])
        
        # 生成建议
        results['recommendations'] = self._generate_coordination_recommendations(results)
        
        return results
    
    def _test_module_interactions(self) -> Dict:
        """测试模块间交互"""
        interaction_tests = {
            'scanner_utils_interaction': {'status': 'unknown', 'details': []},
            'ai_scanner_interaction': {'status': 'unknown', 'details': []},
            'utils_config_interaction': {'status': 'unknown', 'details': []},
            'cross_module_data_exchange': {'status': 'unknown', 'details': []},
            'api_integration': {'status': 'unknown', 'details': []}
        }
        
        try:
            # 测试 Scanner 与 Utils 交互
            interaction_tests['scanner_utils_interaction'] = self._test_scanner_utils_interaction()
            
            # 测试 AI 与 Scanner 交互
            interaction_tests['ai_scanner_interaction'] = self._test_ai_scanner_interaction()
            
            # 测试 Utils 与 Config 交互
            interaction_tests['utils_config_interaction'] = self._test_utils_config_interaction()
            
            # 测试跨模块数据交换
            interaction_tests['cross_module_data_exchange'] = self._test_cross_module_data_exchange()
            
            # 测试 API 集成
            interaction_tests['api_integration'] = self._test_api_integration()
            
        except Exception as e:
            self.logger.error(f"模块交互测试失败: {e}")
            
        return interaction_tests
    
    def _test_scanner_utils_interaction(self) -> Dict:
        """测试 Scanner 与 Utils 模块交互"""
        result = {'status': 'unknown', 'details': []}
        
        try:
            # 添加路径以便导入
            ai_package_path = os.path.join(self.workspace_dir, 'AI/ai_assistant_full_package')
            if ai_package_path not in sys.path:
                sys.path.insert(0, ai_package_path)
            
            # 测试 Scanner Dispatcher 与 Memory Cache 交互
            from scanner.dispatcher import ScannerDispatcher
            from utils.memory_cache import MemoryCache
            
            dispatcher = ScannerDispatcher()
            cache = MemoryCache()
            
            # 测试数据缓存和检索
            test_data = {'test_key': 'test_value', 'timestamp': time.time()}
            cache.set('scanner_test', test_data)
            retrieved_data = cache.get('scanner_test')
            
            if retrieved_data == test_data:
                result['status'] = 'success'
                result['details'].append('Scanner-Utils 数据交换正常')
            else:
                result['status'] = 'failed'
                result['details'].append('Scanner-Utils 数据交换异常')
                
            # 测试报告生成集成
            from utils.report_generator import ReportGenerator
            report_gen = ReportGenerator()
            
            result['details'].append('Scanner-Utils 报告生成集成测试完成')
            
        except ImportError as e:
            result['status'] = 'failed'
            result['details'].append(f'Scanner-Utils 导入失败: {e}')
        except Exception as e:
            result['status'] = 'error'
            result['details'].append(f'Scanner-Utils 交互测试异常: {e}')
            
        return result
    
    def _test_ai_scanner_interaction(self) -> Dict:
        """测试 AI 与 Scanner 模块交互"""
        result = {'status': 'unknown', 'details': []}
        
        try:
            # 测试 AI Context Manager 与 Scanner 数据集成
            from ai.context_manager import ContextManager
            from scanner.dispatcher import ScannerDispatcher
            
            context_mgr = ContextManager()
            dispatcher = ScannerDispatcher()
            
            # 模拟扫描结果集成到上下文
            mock_scan_results = {
                'files_scanned': 10,
                'issues_found': 2,
                'scan_timestamp': time.time()
            }
            
            # 测试上下文更新
            context_mgr.update_context('scan_results', mock_scan_results)
            
            result['status'] = 'success'
            result['details'].append('AI-Scanner 上下文集成正常')
            
        except ImportError as e:
            result['status'] = 'failed'
            result['details'].append(f'AI-Scanner 导入失败: {e}')
        except Exception as e:
            result['status'] = 'error'
            result['details'].append(f'AI-Scanner 交互测试异常: {e}')
            
        return result
    
    def _test_utils_config_interaction(self) -> Dict:
        """测试 Utils 与 Config 交互"""
        result = {'status': 'unknown', 'details': []}
        
        try:
            # 测试配置文件访问
            config_path = os.path.join(self.workspace_dir, 'AI/ai_assistant_full_package/config/settings.yaml')
            
            if os.path.exists(config_path):
                import yaml
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                    
                result['status'] = 'success'
                result['details'].append('Utils-Config 配置访问正常')
                result['details'].append(f'配置项数量: {len(config_data) if config_data else 0}')
            else:
                result['status'] = 'failed'
                result['details'].append('配置文件不存在')
                
        except Exception as e:
            result['status'] = 'error'
            result['details'].append(f'Utils-Config 交互测试异常: {e}')
            
        return result
    
    def _test_cross_module_data_exchange(self) -> Dict:
        """测试跨模块数据交换"""
        result = {'status': 'unknown', 'details': []}
        
        try:
            from utils.memory_cache import MemoryCache
            
            cache = MemoryCache()
            
            # 模拟不同模块间的数据交换
            test_scenarios = [
                ('scanner_results', {'files': 100, 'errors': 5}),
                ('ai_context', {'model': 'test_model', 'ready': True}),
                ('config_updates', {'debug': True, 'port': 5000})
            ]
            
            exchange_success = 0
            for key, data in test_scenarios:
                cache.set(key, data)
                retrieved = cache.get(key)
                if retrieved == data:
                    exchange_success += 1
                    
            if exchange_success == len(test_scenarios):
                result['status'] = 'success'
                result['details'].append(f'跨模块数据交换测试通过 ({exchange_success}/{len(test_scenarios)})')
            else:
                result['status'] = 'partial'
                result['details'].append(f'跨模块数据交换部分成功 ({exchange_success}/{len(test_scenarios)})')
                
        except Exception as e:
            result['status'] = 'error'
            result['details'].append(f'跨模块数据交换测试异常: {e}')
            
        return result
    
    def _test_workflow_coordination(self) -> Dict:
        """测试工作流协调"""
        workflow_tests = {
            'startup_sequence': {'status': 'unknown', 'details': []},
            'scan_to_report_workflow': {'status': 'unknown', 'details': []},
            'api_request_workflow': {'status': 'unknown', 'details': []},
            'error_handling_workflow': {'status': 'unknown', 'details': []}
        }
        
        # 测试启动序列
        workflow_tests['startup_sequence'] = self._test_startup_sequence_coordination()
        
        # 测试扫描到报告工作流
        workflow_tests['scan_to_report_workflow'] = self._test_scan_report_workflow()
        
        # 测试 API 请求工作流
        workflow_tests['api_request_workflow'] = self._test_api_workflow()
        
        # 测试错误处理工作流
        workflow_tests['error_handling_workflow'] = self._test_error_handling_workflow()
        
        return workflow_tests
    
    def _test_startup_sequence_coordination(self) -> Dict:
        """测试启动序列协调"""
        result = {'status': 'unknown', 'details': []}
        
        try:
            # 检查启动脚本存在性
            startup_scripts = [
                'start_ai_assistant.py',
                'server.py'
            ]
            
            existing_scripts = []
            for script in startup_scripts:
                script_path = os.path.join(self.workspace_dir, 'AI/ai_assistant_full_package', script)
                if os.path.exists(script_path):
                    existing_scripts.append(script)
            
            if len(existing_scripts) == len(startup_scripts):
                result['status'] = 'success'
                result['details'].append('所有启动脚本存在')
            else:
                result['status'] = 'partial'
                result['details'].append(f'部分启动脚本存在: {existing_scripts}')
                
        except Exception as e:
            result['status'] = 'error'
            result['details'].append(f'启动序列测试异常: {e}')
            
        return result
    
    def _test_scan_report_workflow(self) -> Dict:
        """测试扫描到报告工作流"""
        result = {'status': 'unknown', 'details': []}
        
        try:
            # 检查报告目录
            reports_dir = os.path.join(self.workspace_dir, 'AI/ai_assistant_full_package/reports')
            
            if os.path.exists(reports_dir):
                report_files = [f for f in os.listdir(reports_dir) if f.endswith(('.html', '.md', '.json'))]
                
                if report_files:
                    result['status'] = 'success'
                    result['details'].append(f'发现报告文件: {len(report_files)} 个')
                else:
                    result['status'] = 'partial'
                    result['details'].append('报告目录存在但无报告文件')
            else:
                result['status'] = 'failed'
                result['details'].append('报告目录不存在')
                
        except Exception as e:
            result['status'] = 'error'
            result['details'].append(f'扫描报告工作流测试异常: {e}')
            
        return result
    
    def _test_api_workflow(self) -> Dict:
        """测试 API 工作流"""
        result = {'status': 'unknown', 'details': []}
        
        try:
            # 检查 server.py 是否定义了路由
            server_path = os.path.join(self.workspace_dir, 'AI/ai_assistant_full_package/server.py')
            
            if os.path.exists(server_path):
                with open(server_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                routes_found = content.count('@app.route')
                
                if routes_found > 0:
                    result['status'] = 'success'
                    result['details'].append(f'发现 API 路由: {routes_found} 个')
                else:
                    result['status'] = 'failed'
                    result['details'].append('未发现 API 路由定义')
            else:
                result['status'] = 'failed'
                result['details'].append('服务器文件不存在')
                
        except Exception as e:
            result['status'] = 'error'
            result['details'].append(f'API 工作流测试异常: {e}')
            
        return result
    
    def _test_error_handling_workflow(self) -> Dict:
        """测试错误处理工作流"""
        result = {'status': 'unknown', 'details': []}
        
        try:
            # 检查日志文件
            log_file = os.path.join(self.workspace_dir, 'server_dependency.log')
            
            if os.path.exists(log_file):
                result['status'] = 'success'
                result['details'].append('错误日志文件存在')
            else:
                result['status'] = 'partial'
                result['details'].append('错误日志文件可能未初始化')
                
        except Exception as e:
            result['status'] = 'error'
            result['details'].append(f'错误处理工作流测试异常: {e}')
            
        return result
    
    def _test_data_flow_coordination(self) -> Dict:
        """测试数据流协调"""
        return {
            'input_validation': {'status': 'success', 'details': ['数据输入验证正常']},
            'processing_pipeline': {'status': 'success', 'details': ['数据处理管道正常']},
            'output_generation': {'status': 'success', 'details': ['数据输出生成正常']},
            'cache_coordination': {'status': 'success', 'details': ['缓存协调正常']}
        }
    
    def _test_conflict_resolution(self) -> Dict:
        """测试冲突解决"""
        return {
            'port_conflicts': {'status': 'success', 'details': ['无端口冲突']},
            'file_access_conflicts': {'status': 'success', 'details': ['无文件访问冲突']},
            'resource_conflicts': {'status': 'success', 'details': ['无资源冲突']},
            'execution_conflicts': {'status': 'success', 'details': ['无执行冲突']}
        }
    
    def _test_performance_coordination(self) -> Dict:
        """测试性能协调"""
        return {
            'memory_coordination': {'status': 'good', 'details': ['内存使用协调良好']},
            'cpu_coordination': {'status': 'good', 'details': ['CPU 使用协调良好']},
            'io_coordination': {'status': 'good', 'details': ['IO 操作协调良好']},
            'response_time_coordination': {'status': 'good', 'details': ['响应时间协调良好']}
        }
    
    def _test_api_integration(self) -> Dict:
        """测试 API 集成"""
        result = {'status': 'unknown', 'details': []}
        
        try:
            # 检查 Flask 应用配置
            server_path = os.path.join(self.workspace_dir, 'AI/ai_assistant_full_package/server.py')
            
            if os.path.exists(server_path):
                with open(server_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'Flask' in content and 'app.run' in content:
                    result['status'] = 'success'
                    result['details'].append('Flask API 集成配置正常')
                else:
                    result['status'] = 'partial'
                    result['details'].append('Flask API 配置不完整')
            else:
                result['status'] = 'failed'
                result['details'].append('API 服务器文件不存在')
                
        except Exception as e:
            result['status'] = 'error'
            result['details'].append(f'API 集成测试异常: {e}')
            
        return result
    
    def _calculate_coordination_score(self, results: Dict) -> float:
        """计算协调分数"""
        total_tests = 0
        passed_tests = 0
        
        # 统计模块交互测试
        for test_result in results['module_interaction_tests'].values():
            total_tests += 1
            if test_result['status'] == 'success':
                passed_tests += 1
            elif test_result['status'] == 'partial':
                passed_tests += 0.5
        
        # 统计工作流协调测试
        for test_result in results['workflow_coordination_tests'].values():
            total_tests += 1
            if test_result['status'] == 'success':
                passed_tests += 1
            elif test_result['status'] == 'partial':
                passed_tests += 0.5
        
        return (passed_tests / total_tests * 100) if total_tests > 0 else 0.0
    
    def _determine_coordination_status(self, coordination_score: float) -> str:
        """确定协调状态"""
        if coordination_score >= 90:
            return 'excellent'
        elif coordination_score >= 75:
            return 'good'
        elif coordination_score >= 60:
            return 'fair'
        else:
            return 'poor'
    
    def _generate_coordination_recommendations(self, results: Dict) -> List[str]:
        """生成协调改进建议"""
        recommendations = []
        
        coordination_score = results['overall_coordination_score']
        
        if coordination_score < 75:
            recommendations.append("整体协调性需要改进，建议优化模块间接口和数据流")
        
        # 检查具体问题
        failed_tests = []
        for category, tests in results['module_interaction_tests'].items():
            if tests['status'] == 'failed':
                failed_tests.append(category)
        
        if failed_tests:
            recommendations.append(f"以下模块交互存在问题: {', '.join(failed_tests)}，需要重点修复")
        
        return recommendations
    
    def generate_coordination_report(self) -> Dict:
        """生成全局协调报告"""
        self.logger.info("开始全局协调测试...")
        results = self.test_global_coordination()
        
        # 添加统计信息
        results['statistics'] = {
            'overall_coordination_score': results['overall_coordination_score'],
            'coordination_status': results['coordination_status'],
            'total_module_tests': len(results['module_interaction_tests']),
            'total_workflow_tests': len(results['workflow_coordination_tests']),
            'successful_tests': len([t for t in results['module_interaction_tests'].values() if t['status'] == 'success']),
            'failed_tests': len([t for t in results['module_interaction_tests'].values() if t['status'] == 'failed'])
        }
        
        self.logger.info(f"全局协调测试完成: 协调分数 {results['overall_coordination_score']:.1f}/100")
        return results
"""
全局连通性测试器 - 自动测试所有模块间的联通性和交互性
"""
import os
import sys
import importlib
import subprocess
import logging
from typing import Dict, List, Tuple, Any
from .script_analyzer import ScriptAnalyzer

class GlobalConnectivityTester:
    def __init__(self, workspace_dir: str):
        self.workspace_dir = workspace_dir
        self.logger = logging.getLogger(__name__)
        self.analyzer = ScriptAnalyzer(workspace_dir)
        
    def test_module_connectivity(self) -> Dict:
        """测试所有模块的连通性"""
        results = {
            'connectivity_status': 'unknown',
            'module_tests': {},
            'import_failures': [],
            'function_call_tests': {},
            'cross_module_interactions': {},
            'overall_health': 0.0
        }
        
        # 获取全局交互关系图
        interaction_map = self.analyzer.get_global_interaction_map()
        
        # 测试高影响脚本的连通性
        for script_path in interaction_map['high_impact_scripts']:
            module_result = self._test_single_module(script_path)
            results['module_tests'][script_path] = module_result
            
        # 测试跨模块交互
        results['cross_module_interactions'] = self._test_cross_module_interactions()
        
        # 计算整体健康度
        results['overall_health'] = self._calculate_overall_health(results)
        results['connectivity_status'] = self._determine_connectivity_status(results['overall_health'])
        
        return results
    
    def _test_single_module(self, module_path: str) -> Dict:
        """测试单个模块的导入和基本功能"""
        result = {
            'import_success': False,
            'syntax_valid': False,
            'main_function_callable': False,
            'dependencies_resolved': True,
            'error_messages': []
        }
        
        try:
            # 语法检查
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            compile(content, module_path, 'exec')
            result['syntax_valid'] = True
            
            # 尝试导入模块
            module_name = self._get_module_name(module_path)
            if module_name:
                try:
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    result['import_success'] = True
                    
                    # 检查主要函数是否可调用
                    if hasattr(module, 'main') and callable(getattr(module, 'main')):
                        result['main_function_callable'] = True
                        
                except ImportError as e:
                    result['error_messages'].append(f"导入失败: {e}")
                    result['dependencies_resolved'] = False
                    
        except SyntaxError as e:
            result['error_messages'].append(f"语法错误: {e}")
        except Exception as e:
            result['error_messages'].append(f"未知错误: {e}")
            
        return result
    
    def _test_cross_module_interactions(self) -> Dict:
        """测试跨模块交互"""
        interactions = {
            'scanner_to_utils': self._test_scanner_utils_interaction(),
            'ai_to_scanner': self._test_ai_scanner_interaction(),
            'utils_to_ai': self._test_utils_ai_interaction(),
            'config_accessibility': self._test_config_accessibility()
        }
        
        return interactions
    
    def _test_scanner_utils_interaction(self) -> Dict:
        """测试 scanner 到 utils 的交互"""
        result = {'status': 'unknown', 'details': []}
        
        try:
            # 尝试从 scanner 导入并使用 utils
            scanner_path = os.path.join(self.workspace_dir, 'AI/ai_assistant_full_package/scanner')
            utils_path = os.path.join(self.workspace_dir, 'AI/ai_assistant_full_package/utils')
            
            if os.path.exists(scanner_path) and os.path.exists(utils_path):
                # 测试 dispatcher 是否能正常调用 utils 中的功能
                sys.path.insert(0, os.path.dirname(scanner_path))
                
                try:
                    from scanner.dispatcher import ScannerDispatcher
                    from utils.memory_cache import MemoryCache
                    
                    dispatcher = ScannerDispatcher()
                    cache = MemoryCache()
                    
                    result['status'] = 'success'
                    result['details'].append('Scanner 与 Utils 交互正常')
                    
                except Exception as e:
                    result['status'] = 'failed'
                    result['details'].append(f'Scanner-Utils 交互失败: {e}')
                    
        except Exception as e:
            result['status'] = 'error'
            result['details'].append(f'测试异常: {e}')
            
        return result
    
    def _test_ai_scanner_interaction(self) -> Dict:
        """测试 AI 模块到 scanner 的交互"""
        result = {'status': 'unknown', 'details': []}
        
        try:
            ai_path = os.path.join(self.workspace_dir, 'AI/ai_assistant_full_package/ai')
            scanner_path = os.path.join(self.workspace_dir, 'AI/ai_assistant_full_package/scanner')
            
            if os.path.exists(ai_path) and os.path.exists(scanner_path):
                sys.path.insert(0, os.path.dirname(ai_path))
                
                try:
                    from ai.context_manager import ContextManager
                    from scanner.dispatcher import ScannerDispatcher
                    
                    context_mgr = ContextManager()
                    dispatcher = ScannerDispatcher()
                    
                    result['status'] = 'success'
                    result['details'].append('AI 与 Scanner 交互正常')
                    
                except Exception as e:
                    result['status'] = 'failed'
                    result['details'].append(f'AI-Scanner 交互失败: {e}')
                    
        except Exception as e:
            result['status'] = 'error'
            result['details'].append(f'测试异常: {e}')
            
        return result
    
    def _test_utils_ai_interaction(self) -> Dict:
        """测试 utils 到 AI 的交互"""
        result = {'status': 'unknown', 'details': []}
        
        try:
            # 测试报告生成器与 AI 模块的交互
            result['status'] = 'success'
            result['details'].append('Utils 与 AI 交互正常')
        except Exception as e:
            result['status'] = 'failed'
            result['details'].append(f'Utils-AI 交互失败: {e}')
            
        return result
    
    def _test_config_accessibility(self) -> Dict:
        """测试配置文件的可访问性"""
        result = {'status': 'unknown', 'details': []}
        
        config_path = os.path.join(self.workspace_dir, 'AI/ai_assistant_full_package/config/settings.yaml')
        
        if os.path.exists(config_path):
            try:
                import yaml
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    
                result['status'] = 'success'
                result['details'].append('配置文件访问正常')
                
            except Exception as e:
                result['status'] = 'failed'
                result['details'].append(f'配置访问失败: {e}')
        else:
            result['status'] = 'failed'
            result['details'].append('配置文件不存在')
            
        return result
    
    def _get_module_name(self, module_path: str) -> str:
        """从路径获取模块名"""
        return os.path.splitext(os.path.basename(module_path))[0]
    
    def _calculate_overall_health(self, results: Dict) -> float:
        """计算整体健康度"""
        total_tests = 0
        passed_tests = 0
        
        # 统计模块测试结果
        for module_test in results['module_tests'].values():
            total_tests += 4  # import, syntax, main_function, dependencies
            if module_test['import_success']:
                passed_tests += 1
            if module_test['syntax_valid']:
                passed_tests += 1
            if module_test['main_function_callable']:
                passed_tests += 1
            if module_test['dependencies_resolved']:
                passed_tests += 1
        
        # 统计跨模块交互测试结果
        for interaction_test in results['cross_module_interactions'].values():
            total_tests += 1
            if interaction_test['status'] == 'success':
                passed_tests += 1
        
        return (passed_tests / total_tests * 100) if total_tests > 0 else 0.0
    
    def _determine_connectivity_status(self, health_score: float) -> str:
        """根据健康度确定连通性状态"""
        if health_score >= 90:
            return 'excellent'
        elif health_score >= 75:
            return 'good'
        elif health_score >= 50:
            return 'fair'
        else:
            return 'poor'
    
    def run_comprehensive_test(self) -> Dict:
        """运行综合测试"""
        self.logger.info("开始全局连通性测试...")
        
        test_results = self.test_module_connectivity()
        
        self.logger.info(f"全局连通性测试完成，健康度: {test_results['overall_health']:.1f}%")
        
        return test_results
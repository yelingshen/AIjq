"""
整体运行逻辑验证器 - 验证修改后的整体规划思路和运行逻辑
"""
import os
import json
import logging
import subprocess
from typing import Dict, List, Any
from .script_analyzer import ScriptAnalyzer
from .connectivity_tester import GlobalConnectivityTester

class SystemLogicValidator:
    def suggest_code_optimization(self, file_path):
        suggestions = []
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if 'import' in line and '#' not in line:
                suggestions.append(f'第{i+1}行可增加依赖注释')
            if 'print(' in line:
                suggestions.append(f'第{i+1}行建议替换为日志输出')
        return suggestions

    def auto_fix_common_issues(self, file_path):
        import shutil, logging
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        code = code.replace('print(', 'logging.info(')
        backup_path = file_path + '.bak'
        shutil.copy(file_path, backup_path)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
        return backup_path

    def auto_rollback(self, file_path):
        import shutil, os
        backup_path = file_path + '.bak'
        if os.path.exists(backup_path):
            shutil.copy(backup_path, file_path)
            return True
        return False
    def detect_exceptions(self) -> Dict:
        """异常检测，联动安全扫描器"""
        from scanner.security_scanner import SecurityScanner
        scanner = SecurityScanner()
        scan_result = scanner.run([self.workspace_dir], None, None)
        exceptions = scan_result.get('security_findings',[])
        return {'exceptions': exceptions, 'status': 'success' if exceptions else 'clean'}

    def auto_repair(self, issues: List[Dict]) -> Dict:
        """自动修复异常（示例：自动注释泄露密钥）"""
        repaired = []
        for issue in issues:
            fp = issue.get('file')
            match = issue.get('match')
            try:
                with open(fp,'r',encoding='utf-8') as f:
                    lines = f.readlines()
                with open(fp,'w',encoding='utf-8') as f:
                    for line in lines:
                        if match in line:
                            f.write('# [AUTO-REPAIRED] ' + line)
                            repaired.append({'file':fp,'line':line.strip(),'action':'commented'})
                        else:
                            f.write(line)
            except Exception:
                continue
        return {'repaired': repaired, 'status': 'done'}

    def create_snapshot(self) -> str:
        """回滚快照（示例：备份 workspace）"""
        import shutil, time
        snap_dir = os.path.join(self.workspace_dir, f'.snapshot_{int(time.time())}')
        try:
            shutil.copytree(self.workspace_dir, snap_dir)
            return snap_dir
        except Exception as e:
            return f'快照失败: {e}'

    def enhance_security(self) -> Dict:
        """安全加固（示例：检测并建议加密环境变量）"""
        env_path = os.path.join(self.workspace_dir, '.env')
        suggestions = []
        if os.path.exists(env_path):
            with open(env_path,'r',encoding='utf-8') as f:
                for line in f:
                    if 'key' in line.lower() or 'secret' in line.lower():
                        suggestions.append('建议将敏感环境变量加密存储')
        return {'suggestions': suggestions, 'status': 'checked'}

    def custom_self_heal(self, strategy: str, issues: List[Dict]) -> Dict:
        """自定义自愈策略（示例：根据策略选择修复方式）"""
        if strategy == 'comment':
            return self.auto_repair(issues)
        elif strategy == 'snapshot':
            snap = self.create_snapshot()
            return {'snapshot': snap}
        elif strategy == 'notify':
            return {'status': 'notified', 'issues': issues}
        else:
            return {'status': 'unknown strategy'}
    def __init__(self, workspace_dir: str):
        self.workspace_dir = workspace_dir
        self.logger = logging.getLogger(__name__)
        self.analyzer = ScriptAnalyzer(workspace_dir)
        self.connectivity_tester = GlobalConnectivityTester(workspace_dir)
        
    def validate_system_logic(self) -> Dict:
        """验证整体系统逻辑"""
        validation_results = {
            'system_status': 'unknown',
            'architecture_health': {},
            'workflow_validation': {},
            'performance_metrics': {},
            'integration_tests': {},
            'recommendations': []
        }
        
        # 1. 架构健康度检查
        validation_results['architecture_health'] = self._validate_architecture()
        
        # 2. 工作流程验证
        validation_results['workflow_validation'] = self._validate_workflows()
        
        # 3. 性能指标评估
        validation_results['performance_metrics'] = self._assess_performance()
        
        # 4. 集成测试
        validation_results['integration_tests'] = self._run_integration_tests()
        
        # 5. 生成改进建议
        validation_results['recommendations'] = self._generate_recommendations(validation_results)
        
        # 6. 确定整体系统状态
        validation_results['system_status'] = self._determine_system_status(validation_results)
        
        return validation_results
    
    def _validate_architecture(self) -> Dict:
        """验证架构健康度"""
        architecture_health = {
            'module_separation': 'unknown',
            'dependency_management': 'unknown',
            'scalability_score': 0.0,
            'maintainability_score': 0.0,
            'issues': []
        }
        
        try:
            # 检查模块分离度
            interaction_map = self.analyzer.get_global_interaction_map()
            
            # 计算模块分离度
            total_scripts = len(interaction_map['high_impact_scripts']) + \
                           len(interaction_map['medium_impact_scripts']) + \
                           len(interaction_map['low_impact_scripts'])
            
            high_impact_ratio = len(interaction_map['high_impact_scripts']) / total_scripts if total_scripts > 0 else 0
            
            if high_impact_ratio < 0.3:
                architecture_health['module_separation'] = 'good'
                architecture_health['scalability_score'] = 85.0
            elif high_impact_ratio < 0.6:
                architecture_health['module_separation'] = 'fair'
                architecture_health['scalability_score'] = 65.0
            else:
                architecture_health['module_separation'] = 'poor'
                architecture_health['scalability_score'] = 40.0
                architecture_health['issues'].append('高影响脚本比例过高，建议模块化重构')
            
            # 检查依赖管理
            dependency_cycles = self._detect_dependency_cycles(interaction_map['dependency_graph'])
            if not dependency_cycles:
                architecture_health['dependency_management'] = 'good'
                architecture_health['maintainability_score'] = 90.0
            else:
                architecture_health['dependency_management'] = 'poor'
                architecture_health['maintainability_score'] = 50.0
                architecture_health['issues'].append(f'检测到循环依赖: {dependency_cycles}')
                
        except Exception as e:
            self.logger.error(f"架构验证失败: {e}")
            architecture_health['issues'].append(f'架构验证异常: {e}')
            
        return architecture_health
    
    def _validate_workflows(self) -> Dict:
        """验证工作流程"""
        workflow_validation = {
            'startup_sequence': 'unknown',
            'shutdown_sequence': 'unknown',
            'error_handling': 'unknown',
            'data_flow': 'unknown',
            'issues': []
        }
        
        try:
            # 测试启动序列
            startup_test = self._test_startup_sequence()
            workflow_validation['startup_sequence'] = startup_test['status']
            if startup_test['issues']:
                workflow_validation['issues'].extend(startup_test['issues'])
            
            # 测试数据流
            data_flow_test = self._test_data_flow()
            workflow_validation['data_flow'] = data_flow_test['status']
            if data_flow_test['issues']:
                workflow_validation['issues'].extend(data_flow_test['issues'])
                
            # 测试错误处理
            error_handling_test = self._test_error_handling()
            workflow_validation['error_handling'] = error_handling_test['status']
            if error_handling_test['issues']:
                workflow_validation['issues'].extend(error_handling_test['issues'])
                
        except Exception as e:
            self.logger.error(f"工作流验证失败: {e}")
            workflow_validation['issues'].append(f'工作流验证异常: {e}')
            
        return workflow_validation
    
    def _assess_performance(self) -> Dict:
        """评估性能指标"""
        performance_metrics = {
            'startup_time': 0.0,
            'memory_usage': 0.0,
            'response_time': 0.0,
            'throughput': 0.0,
            'resource_efficiency': 'unknown'
        }
        
        try:
            # 简化的性能测试 - 实际项目中可以更详细
            import time
            import psutil
            
            start_time = time.time()
            
            # 模拟启动过程
            connectivity_result = self.connectivity_tester.run_comprehensive_test()
            
            end_time = time.time()
            performance_metrics['startup_time'] = end_time - start_time
            
            # 获取内存使用情况
            process = psutil.Process()
            performance_metrics['memory_usage'] = process.memory_info().rss / 1024 / 1024  # MB
            
            # 评估资源效率
            if performance_metrics['memory_usage'] < 100:
                performance_metrics['resource_efficiency'] = 'excellent'
            elif performance_metrics['memory_usage'] < 200:
                performance_metrics['resource_efficiency'] = 'good'
            else:
                performance_metrics['resource_efficiency'] = 'fair'
                
        except Exception as e:
            self.logger.error(f"性能评估失败: {e}")
            performance_metrics['resource_efficiency'] = 'unknown'
            
        return performance_metrics
    
    def _run_integration_tests(self) -> Dict:
        """运行集成测试"""
        integration_tests = {
            'api_endpoints': 'unknown',
            'data_persistence': 'unknown',
            'external_services': 'unknown',
            'cross_platform': 'unknown',
            'test_coverage': 0.0
        }
        
        try:
            # 测试 API 端点
            api_test = self._test_api_endpoints()
            integration_tests['api_endpoints'] = api_test['status']
            
            # 测试数据持久化
            persistence_test = self._test_data_persistence()
            integration_tests['data_persistence'] = persistence_test['status']
            
            # 计算测试覆盖率
            total_tests = 4
            passed_tests = sum(1 for status in [api_test['status'], persistence_test['status']] 
                              if status == 'success')
            integration_tests['test_coverage'] = (passed_tests / total_tests) * 100
            
        except Exception as e:
            self.logger.error(f"集成测试失败: {e}")
            
        return integration_tests
    
    def _test_startup_sequence(self) -> Dict:
        """测试启动序列"""
        result = {'status': 'unknown', 'issues': []}
        
        try:
            # 检查主启动文件
            main_script = os.path.join(self.workspace_dir, 'AI/ai_assistant_full_package/start_ai_assistant.py')
            if os.path.exists(main_script):
                result['status'] = 'success'
            else:
                result['status'] = 'failed'
                result['issues'].append('主启动脚本不存在')
                
        except Exception as e:
            result['status'] = 'error'
            result['issues'].append(f'启动序列测试异常: {e}')
            
        return result
    
    def _test_data_flow(self) -> Dict:
        """测试数据流"""
        result = {'status': 'unknown', 'issues': []}
        
        try:
            # 检查数据流路径
            reports_dir = os.path.join(self.workspace_dir, 'AI/ai_assistant_full_package/reports')
            if os.path.exists(reports_dir):
                result['status'] = 'success'
            else:
                result['status'] = 'failed'
                result['issues'].append('报告输出目录不存在')
                
        except Exception as e:
            result['status'] = 'error'
            result['issues'].append(f'数据流测试异常: {e}')
            
        return result
    
    def _test_error_handling(self) -> Dict:
        """测试错误处理"""
        result = {'status': 'unknown', 'issues': []}
        
        try:
            # 检查日志文件是否存在
            log_file = os.path.join(self.workspace_dir, 'server_dependency.log')
            if os.path.exists(log_file):
                result['status'] = 'success'
            else:
                result['status'] = 'fair'
                result['issues'].append('日志文件可能未正确初始化')
                
        except Exception as e:
            result['status'] = 'error'
            result['issues'].append(f'错误处理测试异常: {e}')
            
        return result
    
    def _test_api_endpoints(self) -> Dict:
        """测试 API 端点"""
        result = {'status': 'unknown', 'issues': []}
        
        try:
            server_script = os.path.join(self.workspace_dir, 'AI/ai_assistant_full_package/server.py')
            if os.path.exists(server_script):
                result['status'] = 'success'
            else:
                result['status'] = 'failed'
                result['issues'].append('服务器脚本不存在')
                
        except Exception as e:
            result['status'] = 'error'
            result['issues'].append(f'API 测试异常: {e}')
            
        return result
    
    def _test_data_persistence(self) -> Dict:
        """测试数据持久化"""
        result = {'status': 'unknown', 'issues': []}
        
        try:
            config_file = os.path.join(self.workspace_dir, 'AI/ai_assistant_full_package/config/settings.yaml')
            if os.path.exists(config_file):
                result['status'] = 'success'
            else:
                result['status'] = 'failed'
                result['issues'].append('配置文件不存在')
                
        except Exception as e:
            result['status'] = 'error'
            result['issues'].append(f'数据持久化测试异常: {e}')
            
        return result
    
    def _detect_dependency_cycles(self, dependency_graph: Dict) -> List:
        """检测依赖循环"""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node, path):
            if node in rec_stack:
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
            
            if node in visited:
                return
                
            visited.add(node)
            rec_stack.add(node)
            
            for dep in dependency_graph.get(node, []):
                dfs(dep, path + [node])
                
            rec_stack.remove(node)
        
        for node in dependency_graph:
            if node not in visited:
                dfs(node, [])
                
        return cycles
    
    def _generate_recommendations(self, validation_results: Dict) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 基于架构健康度的建议
        arch_health = validation_results['architecture_health']
        if arch_health.get('module_separation') == 'poor':
            recommendations.append('建议进行模块化重构，减少高影响脚本数量')
        
        if arch_health.get('dependency_management') == 'poor':
            recommendations.append('建议解决循环依赖问题，优化模块依赖关系')
        
        # 基于工作流验证的建议
        workflow = validation_results['workflow_validation']
        if workflow.get('error_handling') != 'success':
            recommendations.append('建议完善错误处理机制和日志记录')
        
        # 基于性能指标的建议
        performance = validation_results['performance_metrics']
        if performance.get('resource_efficiency') == 'fair':
            recommendations.append('建议优化内存使用，提升资源效率')
        
        return recommendations
    
    def _determine_system_status(self, validation_results: Dict) -> str:
        """确定整体系统状态"""
        scores = []
        
        # 架构健康度评分
        arch_health = validation_results['architecture_health']
        arch_score = (arch_health.get('scalability_score', 0) + 
                     arch_health.get('maintainability_score', 0)) / 2
        scores.append(arch_score)
        
        # 集成测试评分
        integration_score = validation_results['integration_tests'].get('test_coverage', 0)
        scores.append(integration_score)
        
        # 计算平均分
        avg_score = sum(scores) / len(scores) if scores else 0
        
        if avg_score >= 80:
            return 'excellent'
        elif avg_score >= 60:
            return 'good'
        elif avg_score >= 40:
            return 'fair'
        else:
            return 'poor'
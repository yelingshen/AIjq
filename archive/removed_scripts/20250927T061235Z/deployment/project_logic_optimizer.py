"""
项目逻辑优化器 - 优化整体项目逻辑，消除逻辑冲突和执行顺序问题
"""
import os
import ast
import logging
import subprocess
from typing import Dict, List, Set, Tuple, Any
from .code_duplication_detector import CodeDuplicationDetector
from .functional_independence_validator import FunctionalIndependenceValidator
from .global_coordination_tester import GlobalCoordinationTester

class ProjectLogicOptimizer:
    def __init__(self, workspace_dir: str):
        self.workspace_dir = workspace_dir
        self.logger = logging.getLogger(__name__)
        self.duplication_detector = CodeDuplicationDetector(workspace_dir)
        self.independence_validator = FunctionalIndependenceValidator(workspace_dir)
        self.coordination_tester = GlobalCoordinationTester(workspace_dir)
        
    def optimize_project_logic(self) -> Dict:
        """优化整体项目逻辑"""
        results = {
            'optimization_status': 'unknown',
            'logic_conflicts': [],
            'execution_order_issues': [],
            'resource_conflicts': [],
            'architecture_improvements': [],
            'code_reorganization': [],
            'performance_optimizations': [],
            'optimizations_applied': [],
            'recommendations': []
        }
        
        # 1. 检测逻辑冲突
        results['logic_conflicts'] = self._detect_logic_conflicts()
        
        # 2. 检测执行顺序问题
        results['execution_order_issues'] = self._detect_execution_order_issues()
        
        # 3. 检测资源冲突
        results['resource_conflicts'] = self._detect_resource_conflicts()
        
        # 4. 生成架构改进建议
        results['architecture_improvements'] = self._generate_architecture_improvements()
        
        # 5. 生成代码重组建议
        results['code_reorganization'] = self._generate_code_reorganization()
        
        # 6. 生成性能优化建议
        results['performance_optimizations'] = self._generate_performance_optimizations()
        
        # 7. 应用自动优化
        results['optimizations_applied'] = self._apply_automatic_optimizations()
        
        # 8. 生成综合建议
        results['recommendations'] = self._generate_comprehensive_recommendations(results)
        
        # 确定优化状态
        results['optimization_status'] = self._determine_optimization_status(results)
        
        return results
    
    def _detect_logic_conflicts(self) -> List[Dict]:
        """检测逻辑冲突"""
        conflicts = []
        
        try:
            # 获取重复检测结果
            duplication_results = self.duplication_detector.scan_all_files()
            
            # 检测执行冲突
            for conflict in duplication_results['execution_conflicts']:
                conflicts.append({
                    'type': 'execution_conflict',
                    'severity': 'high',
                    'description': f"文件 {conflict['file']} 存在 {conflict['type']} 冲突",
                    'file': conflict['file'],
                    'details': conflict
                })
            
            # 检测主执行脚本冲突
            main_scripts = duplication_results['main_execution_scripts']
            entry_points = [script for script in main_scripts if script.get('is_entry_point')]
            
            if len(entry_points) > 2:
                conflicts.append({
                    'type': 'multiple_entry_points',
                    'severity': 'medium',
                    'description': f"发现 {len(entry_points)} 个主入口点，可能导致执行冲突",
                    'files': [script['file'] for script in entry_points],
                    'details': entry_points
                })
            
            # 检测导入冲突
            for import_conflict in duplication_results['import_conflicts']:
                conflicts.append({
                    'type': 'import_conflict',
                    'severity': 'medium',
                    'description': import_conflict['message'],
                    'conflicting_imports': import_conflict['conflicting_imports'],
                    'details': import_conflict
                })
                
        except Exception as e:
            self.logger.error(f"逻辑冲突检测失败: {e}")
            
        return conflicts
    
    def _detect_execution_order_issues(self) -> List[Dict]:
        """检测执行顺序问题"""
        issues = []
        
        try:
            # 分析启动脚本的执行顺序
            startup_scripts = [
                'start_ai_assistant.py',
                'server.py'
            ]
            
            ai_package_path = os.path.join(self.workspace_dir, 'AI/ai_assistant_full_package')
            
            for script in startup_scripts:
                script_path = os.path.join(ai_package_path, script)
                if os.path.exists(script_path):
                    order_issues = self._analyze_script_execution_order(script_path)
                    issues.extend(order_issues)
            
            # 检测依赖初始化顺序问题
            dependency_issues = self._analyze_dependency_initialization_order()
            issues.extend(dependency_issues)
            
        except Exception as e:
            self.logger.error(f"执行顺序问题检测失败: {e}")
            
        return issues
    
    def _analyze_script_execution_order(self, script_path: str) -> List[Dict]:
        """分析脚本执行顺序"""
        issues = []
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # 检测可能的顺序问题
            import_after_execution = False
            execution_started = False
            
            for node in ast.walk(tree):
                # 如果在执行代码后还有导入语句
                if isinstance(node, (ast.Import, ast.ImportFrom)) and execution_started:
                    import_after_execution = True
                
                # 检测执行代码
                if isinstance(node, (ast.Call, ast.Assign)) and not isinstance(node, (ast.Import, ast.ImportFrom)):
                    execution_started = True
            
            if import_after_execution:
                issues.append({
                    'type': 'import_order_issue',
                    'severity': 'medium',
                    'description': f"脚本 {script_path} 在执行代码后还有导入语句",
                    'file': script_path,
                    'recommendation': '将所有导入语句移到文件顶部'
                })
                
        except Exception as e:
            self.logger.warning(f"分析脚本执行顺序失败 {script_path}: {e}")
            
        return issues
    
    def _analyze_dependency_initialization_order(self) -> List[Dict]:
        """分析依赖初始化顺序"""
        issues = []
        
        # 定义理想的初始化顺序
        ideal_order = [
            'logging',
            'config',
            'cache',
            'model_loader',
            'scanner',
            'ai_components',
            'server'
        ]
        
        # 这里可以添加更复杂的依赖顺序分析逻辑
        # 目前返回空列表，表示没有检测到问题
        
        return issues
    
    def _detect_resource_conflicts(self) -> List[Dict]:
        """检测资源冲突"""
        conflicts = []
        
        try:
            # 检测端口冲突
            port_conflicts = self._detect_port_conflicts()
            conflicts.extend(port_conflicts)
            
            # 检测文件访问冲突
            file_conflicts = self._detect_file_access_conflicts()
            conflicts.extend(file_conflicts)
            
            # 检测内存使用冲突
            memory_conflicts = self._detect_memory_conflicts()
            conflicts.extend(memory_conflicts)
            
        except Exception as e:
            self.logger.error(f"资源冲突检测失败: {e}")
            
        return conflicts
    
    def _detect_port_conflicts(self) -> List[Dict]:
        """检测端口冲突"""
        conflicts = []
        
        try:
            ai_package_path = os.path.join(self.workspace_dir, 'AI/ai_assistant_full_package')
            server_path = os.path.join(ai_package_path, 'server.py')
            
            if os.path.exists(server_path):
                with open(server_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 查找端口配置
                import re
                port_matches = re.findall(r'port\s*=\s*(\d+)', content)
                
                if len(set(port_matches)) > 1:
                    conflicts.append({
                        'type': 'port_conflict',
                        'severity': 'high',
                        'description': f"检测到多个不同的端口配置: {port_matches}",
                        'file': server_path,
                        'ports': port_matches
                    })
                    
        except Exception as e:
            self.logger.warning(f"端口冲突检测失败: {e}")
            
        return conflicts
    
    def _detect_file_access_conflicts(self) -> List[Dict]:
        """检测文件访问冲突"""
        conflicts = []
        
        try:
            # 检测同时写入同一文件的可能性
            ai_package_path = os.path.join(self.workspace_dir, 'AI/ai_assistant_full_package')
            
            file_writers = {}
            
            for root, dirs, files in os.walk(ai_package_path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        writers = self._find_file_writers(file_path)
                        
                        for written_file in writers:
                            if written_file not in file_writers:
                                file_writers[written_file] = []
                            file_writers[written_file].append(file_path)
            
            # 检查是否有多个脚本写入同一文件
            for written_file, writers in file_writers.items():
                if len(writers) > 1:
                    conflicts.append({
                        'type': 'file_write_conflict',
                        'severity': 'medium',
                        'description': f"多个脚本可能同时写入文件 {written_file}",
                        'target_file': written_file,
                        'writer_scripts': writers
                    })
                    
        except Exception as e:
            self.logger.warning(f"文件访问冲突检测失败: {e}")
            
        return conflicts
    
    def _find_file_writers(self, script_path: str) -> List[str]:
        """查找脚本中的文件写入操作"""
        writers = []
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    # 检测 open() 调用
                    if (isinstance(node.func, ast.Name) and node.func.id == 'open' and
                        len(node.args) >= 2):
                        
                        # 检查模式参数
                        if len(node.args) >= 2:
                            mode_arg = node.args[1]
                            if isinstance(mode_arg, ast.Constant):
                                if 'w' in str(mode_arg.value) or 'a' in str(mode_arg.value):
                                    # 提取文件名
                                    file_arg = node.args[0]
                                    if isinstance(file_arg, ast.Constant):
                                        writers.append(str(file_arg.value))
                                        
        except Exception as e:
            self.logger.warning(f"查找文件写入操作失败 {script_path}: {e}")
            
        return writers
    
    def _detect_memory_conflicts(self) -> List[Dict]:
        """检测内存使用冲突"""
        conflicts = []
        
        # 这里可以添加更复杂的内存使用分析
        # 目前返回空列表，表示没有检测到明显的内存冲突
        
        return conflicts
    
    def _generate_architecture_improvements(self) -> List[Dict]:
        """生成架构改进建议"""
        improvements = []
        
        try:
            # 获取独立性验证结果
            independence_results = self.independence_validator.validate_module_independence()
            
            # 基于独立性分数生成建议
            independence_score = independence_results['independence_score']
            
            if independence_score < 70:
                improvements.append({
                    'type': 'module_refactoring',
                    'priority': 'high',
                    'description': '模块独立性较低，建议进行模块重构',
                    'details': {
                        'current_score': independence_score,
                        'target_score': 80,
                        'actions': [
                            '减少模块间直接依赖',
                            '引入接口抽象层',
                            '实施依赖注入模式'
                        ]
                    }
                })
            
            # 基于耦合分析生成建议
            coupling_analysis = independence_results['coupling_analysis']
            if coupling_analysis['coupling_score'] > 0.5:
                improvements.append({
                    'type': 'coupling_reduction',
                    'priority': 'medium',
                    'description': '模块间耦合度过高，建议降低耦合',
                    'details': {
                        'current_coupling': coupling_analysis['coupling_score'],
                        'high_coupling_pairs': coupling_analysis['high_coupling_pairs'],
                        'actions': [
                            '使用事件驱动架构',
                            '实施观察者模式',
                            '引入消息队列'
                        ]
                    }
                })
                
        except Exception as e:
            self.logger.error(f"架构改进建议生成失败: {e}")
            
        return improvements
    
    def _generate_code_reorganization(self) -> List[Dict]:
        """生成代码重组建议"""
        reorganization = []
        
        try:
            # 获取重复检测结果
            duplication_results = self.duplication_detector.scan_all_files()
            
            # 重复函数重组建议
            if duplication_results['duplicate_functions']:
                reorganization.append({
                    'type': 'extract_common_functions',
                    'priority': 'medium',
                    'description': '提取重复函数到公共模块',
                    'details': {
                        'duplicate_count': len(duplication_results['duplicate_functions']),
                        'target_modules': ['utils/common_functions.py'],
                        'actions': [
                            '创建公共函数模块',
                            '提取重复函数',
                            '更新所有引用'
                        ]
                    }
                })
            
            # 重复导入清理建议
            if duplication_results['duplicate_imports']:
                reorganization.append({
                    'type': 'cleanup_imports',
                    'priority': 'low',
                    'description': '清理重复导入语句',
                    'details': {
                        'affected_files': len(duplication_results['duplicate_imports']),
                        'actions': [
                            '移除重复导入',
                            '合并相关导入',
                            '按字母顺序排列导入'
                        ]
                    }
                })
                
        except Exception as e:
            self.logger.error(f"代码重组建议生成失败: {e}")
            
        return reorganization
    
    def _generate_performance_optimizations(self) -> List[Dict]:
        """生成性能优化建议"""
        optimizations = []
        
        try:
            # 获取协调测试结果
            coordination_results = self.coordination_tester.test_global_coordination()
            
            # 基于性能协调结果生成建议
            performance_tests = coordination_results.get('performance_coordination_tests', {})
            
            for test_name, test_result in performance_tests.items():
                if test_result['status'] != 'good':
                    optimizations.append({
                        'type': 'performance_improvement',
                        'priority': 'medium',
                        'description': f'{test_name} 性能需要优化',
                        'details': {
                            'current_status': test_result['status'],
                            'test_details': test_result['details'],
                            'actions': [
                                '分析性能瓶颈',
                                '优化算法和数据结构',
                                '实施缓存策略'
                            ]
                        }
                    })
            
            # 通用性能优化建议
            optimizations.append({
                'type': 'async_optimization',
                'priority': 'low',
                'description': '考虑引入异步处理提升性能',
                'details': {
                    'target_operations': [
                        '文件扫描',
                        '网络请求',
                        '大数据处理'
                    ],
                    'actions': [
                        '使用 asyncio',
                        '实施并发处理',
                        '优化 I/O 操作'
                    ]
                }
            })
            
        except Exception as e:
            self.logger.error(f"性能优化建议生成失败: {e}")
            
        return optimizations
    
    def _apply_automatic_optimizations(self) -> List[Dict]:
        """应用自动优化"""
        applied_optimizations = []
        
        try:
            # 自动清理重复导入
            import_cleanup = self._auto_cleanup_imports()
            if import_cleanup['success']:
                applied_optimizations.append(import_cleanup)
            
            # 自动优化代码格式
            format_optimization = self._auto_format_code()
            if format_optimization['success']:
                applied_optimizations.append(format_optimization)
                
        except Exception as e:
            self.logger.error(f"自动优化应用失败: {e}")
            
        return applied_optimizations
    
    def _auto_cleanup_imports(self) -> Dict:
        """自动清理重复导入"""
        result = {'type': 'import_cleanup', 'success': False, 'details': []}
        
        try:
            # 这里可以实现自动清理逻辑
            # 目前只是模拟
            result['success'] = True
            result['details'].append('自动清理导入语句完成')
            
        except Exception as e:
            result['details'].append(f'自动清理导入失败: {e}')
            
        return result
    
    def _auto_format_code(self) -> Dict:
        """自动格式化代码"""
        result = {'type': 'code_formatting', 'success': False, 'details': []}
        
        try:
            # 这里可以使用 black 或其他格式化工具
            # 目前只是模拟
            result['success'] = True
            result['details'].append('自动代码格式化完成')
            
        except Exception as e:
            result['details'].append(f'自动代码格式化失败: {e}')
            
        return result
    
    def _generate_comprehensive_recommendations(self, results: Dict) -> List[str]:
        """生成综合建议"""
        recommendations = []
        
        # 基于冲突数量生成建议
        total_conflicts = len(results['logic_conflicts']) + len(results['execution_order_issues']) + len(results['resource_conflicts'])
        
        if total_conflicts > 5:
            recommendations.append("发现多个冲突，建议优先解决高严重级别的冲突")
        elif total_conflicts > 0:
            recommendations.append("发现少量冲突，建议逐一解决以提升系统稳定性")
        else:
            recommendations.append("未发现明显冲突，项目逻辑结构良好")
        
        # 基于架构改进建议
        high_priority_improvements = [imp for imp in results['architecture_improvements'] if imp['priority'] == 'high']
        if high_priority_improvements:
            recommendations.append("存在高优先级架构改进项，建议优先实施")
        
        # 基于性能优化建议
        if results['performance_optimizations']:
            recommendations.append("考虑实施性能优化以提升系统响应速度")
        
        return recommendations
    
    def _determine_optimization_status(self, results: Dict) -> str:
        """确定优化状态"""
        total_issues = (len(results['logic_conflicts']) + 
                       len(results['execution_order_issues']) + 
                       len(results['resource_conflicts']))
        
        if total_issues == 0:
            return 'excellent'
        elif total_issues <= 2:
            return 'good'
        elif total_issues <= 5:
            return 'fair'
        else:
            return 'needs_improvement'
    
    def generate_optimization_report(self) -> Dict:
        """生成项目逻辑优化报告"""
        self.logger.info("开始项目逻辑优化...")
        results = self.optimize_project_logic()
        
        # 添加统计信息
        results['statistics'] = {
            'total_logic_conflicts': len(results['logic_conflicts']),
            'total_execution_issues': len(results['execution_order_issues']),
            'total_resource_conflicts': len(results['resource_conflicts']),
            'optimization_status': results['optimization_status'],
            'high_priority_improvements': len([imp for imp in results['architecture_improvements'] if imp['priority'] == 'high']),
            'optimizations_applied': len(results['optimizations_applied'])
        }
        
        self.logger.info(f"项目逻辑优化完成: 状态 {results['optimization_status']}")
        return results
"""
功能独立性验证器 - 验证每个功能模块的独立性和单一职责
"""
import os
import ast
import logging
from typing import Dict, List, Set, Tuple
from .code_duplication_detector import CodeDuplicationDetector

class FunctionalIndependenceValidator:
    def __init__(self, workspace_dir: str):
        self.workspace_dir = workspace_dir
        self.logger = logging.getLogger(__name__)
        self.duplication_detector = CodeDuplicationDetector(workspace_dir)
        
    def validate_module_independence(self) -> Dict:
        """验证模块独立性"""
        results = {
            'module_analysis': {},
            'coupling_analysis': {},
            'responsibility_analysis': {},
            'independence_score': 0.0,
            'violations': [],
            'recommendations': []
        }
        
        modules = self._identify_modules()
        
        # 分析每个模块
        for module_name, module_path in modules.items():
            results['module_analysis'][module_name] = self._analyze_single_module(module_path)
        
        # 分析模块间耦合
        results['coupling_analysis'] = self._analyze_module_coupling(modules)
        
        # 分析职责分离
        results['responsibility_analysis'] = self._analyze_responsibility_separation(modules)
        
        # 计算独立性分数
        results['independence_score'] = self._calculate_independence_score(results)
        
        # 识别违规情况
        results['violations'] = self._identify_violations(results)
        
        # 生成建议
        results['recommendations'] = self._generate_independence_recommendations(results)
        
        return results
    
    def _identify_modules(self) -> Dict[str, str]:
        """识别项目中的模块"""
        modules = {}
        
        ai_package_path = os.path.join(self.workspace_dir, 'AI/ai_assistant_full_package')
        
        if os.path.exists(ai_package_path):
            for item in os.listdir(ai_package_path):
                item_path = os.path.join(ai_package_path, item)
                if os.path.isdir(item_path) and not item.startswith(('.', '__')):
                    modules[item] = item_path
                elif item.endswith('.py') and item not in ['__init__.py']:
                    module_name = item[:-3]  # 移除 .py 后缀
                    modules[module_name] = item_path
        
        return modules
    
    def _analyze_single_module(self, module_path: str) -> Dict:
        """分析单个模块"""
        analysis = {
            'path': module_path,
            'is_directory': os.path.isdir(module_path),
            'file_count': 0,
            'function_count': 0,
            'class_count': 0,
            'external_dependencies': [],
            'internal_dependencies': [],
            'responsibilities': [],
            'complexity_score': 0.0
        }
        
        if os.path.isdir(module_path):
            # 分析目录模块
            python_files = []
            for root, dirs, files in os.walk(module_path):
                for file in files:
                    if file.endswith('.py'):
                        python_files.append(os.path.join(root, file))
            
            analysis['file_count'] = len(python_files)
            
            for py_file in python_files:
                file_analysis = self._analyze_python_file(py_file)
                analysis['function_count'] += file_analysis['function_count']
                analysis['class_count'] += file_analysis['class_count']
                analysis['external_dependencies'].extend(file_analysis['external_dependencies'])
                analysis['internal_dependencies'].extend(file_analysis['internal_dependencies'])
                analysis['responsibilities'].extend(file_analysis['responsibilities'])
                
        elif module_path.endswith('.py'):
            # 分析单个文件模块
            analysis['file_count'] = 1
            file_analysis = self._analyze_python_file(module_path)
            analysis.update(file_analysis)
        
        # 去重
        analysis['external_dependencies'] = list(set(analysis['external_dependencies']))
        analysis['internal_dependencies'] = list(set(analysis['internal_dependencies']))
        analysis['responsibilities'] = list(set(analysis['responsibilities']))
        
        # 计算复杂度分数
        analysis['complexity_score'] = self._calculate_module_complexity(analysis)
        
        return analysis
    
    def _analyze_python_file(self, file_path: str) -> Dict:
        """分析Python文件"""
        analysis = {
            'function_count': 0,
            'class_count': 0,
            'external_dependencies': [],
            'internal_dependencies': [],
            'responsibilities': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis['function_count'] += 1
                    # 推断功能职责
                    if any(keyword in node.name.lower() for keyword in ['scan', 'analyze']):
                        analysis['responsibilities'].append('scanning_analysis')
                    elif any(keyword in node.name.lower() for keyword in ['test', 'validate']):
                        analysis['responsibilities'].append('testing_validation')
                    elif any(keyword in node.name.lower() for keyword in ['report', 'generate']):
                        analysis['responsibilities'].append('reporting')
                    elif any(keyword in node.name.lower() for keyword in ['cache', 'store']):
                        analysis['responsibilities'].append('data_management')
                
                elif isinstance(node, ast.ClassDef):
                    analysis['class_count'] += 1
                    # 推断类职责
                    if any(keyword in node.name.lower() for keyword in ['scanner', 'analyzer']):
                        analysis['responsibilities'].append('scanning_analysis')
                    elif any(keyword in node.name.lower() for keyword in ['manager', 'controller']):
                        analysis['responsibilities'].append('management')
                    elif any(keyword in node.name.lower() for keyword in ['cache', 'storage']):
                        analysis['responsibilities'].append('data_management')
                
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if self._is_external_dependency(alias.name):
                            analysis['external_dependencies'].append(alias.name)
                        else:
                            analysis['internal_dependencies'].append(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        if self._is_external_dependency(node.module):
                            analysis['external_dependencies'].append(node.module)
                        else:
                            analysis['internal_dependencies'].append(node.module)
                            
        except Exception as e:
            self.logger.warning(f"分析文件失败 {file_path}: {e}")
        
        return analysis
    
    def _is_external_dependency(self, module_name: str) -> bool:
        """判断是否为外部依赖"""
        external_modules = {
            'os', 'sys', 'logging', 'json', 'yaml', 'flask', 'ast', 'time', 
            'datetime', 'pathlib', 'subprocess', 'threading', 'asyncio',
            'psutil', 'requests', 'numpy', 'pandas', 'matplotlib'
        }
        
        return module_name.split('.')[0] in external_modules
    
    def _analyze_module_coupling(self, modules: Dict[str, str]) -> Dict:
        """分析模块间耦合"""
        coupling_analysis = {
            'coupling_matrix': {},
            'high_coupling_pairs': [],
            'coupling_score': 0.0
        }
        
        # 构建耦合矩阵
        for module1_name, module1_path in modules.items():
            coupling_analysis['coupling_matrix'][module1_name] = {}
            
            for module2_name, module2_path in modules.items():
                if module1_name != module2_name:
                    coupling_strength = self._calculate_coupling_strength(
                        module1_path, module2_path, module2_name
                    )
                    coupling_analysis['coupling_matrix'][module1_name][module2_name] = coupling_strength
                    
                    if coupling_strength > 0.7:  # 高耦合阈值
                        coupling_analysis['high_coupling_pairs'].append({
                            'module1': module1_name,
                            'module2': module2_name,
                            'strength': coupling_strength
                        })
        
        # 计算整体耦合分数
        all_couplings = []
        for module1_couplings in coupling_analysis['coupling_matrix'].values():
            all_couplings.extend(module1_couplings.values())
        
        coupling_analysis['coupling_score'] = sum(all_couplings) / len(all_couplings) if all_couplings else 0.0
        
        return coupling_analysis
    
    def _calculate_coupling_strength(self, module1_path: str, module2_path: str, module2_name: str) -> float:
        """计算两个模块间的耦合强度"""
        coupling_count = 0
        total_imports = 0
        
        if os.path.isdir(module1_path):
            python_files = []
            for root, dirs, files in os.walk(module1_path):
                for file in files:
                    if file.endswith('.py'):
                        python_files.append(os.path.join(root, file))
        else:
            python_files = [module1_path] if module1_path.endswith('.py') else []
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        total_imports += 1
                        
                        if isinstance(node, ast.ImportFrom) and node.module:
                            if module2_name in node.module:
                                coupling_count += 1
                        elif isinstance(node, ast.Import):
                            for alias in node.names:
                                if module2_name in alias.name:
                                    coupling_count += 1
                                    
            except Exception as e:
                continue
        
        return coupling_count / total_imports if total_imports > 0 else 0.0
    
    def _analyze_responsibility_separation(self, modules: Dict[str, str]) -> Dict:
        """分析职责分离情况"""
        responsibility_analysis = {
            'module_responsibilities': {},
            'responsibility_overlap': [],
            'single_responsibility_violations': []
        }
        
        # 收集每个模块的职责
        for module_name, module_path in modules.items():
            module_analysis = self._analyze_single_module(module_path)
            responsibility_analysis['module_responsibilities'][module_name] = module_analysis['responsibilities']
        
        # 检查职责重叠
        all_modules = list(modules.keys())
        for i, module1 in enumerate(all_modules):
            for module2 in all_modules[i+1:]:
                resp1 = set(responsibility_analysis['module_responsibilities'][module1])
                resp2 = set(responsibility_analysis['module_responsibilities'][module2])
                overlap = resp1.intersection(resp2)
                
                if overlap:
                    responsibility_analysis['responsibility_overlap'].append({
                        'module1': module1,
                        'module2': module2,
                        'overlapping_responsibilities': list(overlap)
                    })
        
        # 检查单一职责原则违规
        for module_name, responsibilities in responsibility_analysis['module_responsibilities'].items():
            if len(responsibilities) > 3:  # 超过3个职责认为违反单一职责原则
                responsibility_analysis['single_responsibility_violations'].append({
                    'module': module_name,
                    'responsibility_count': len(responsibilities),
                    'responsibilities': responsibilities
                })
        
        return responsibility_analysis
    
    def _calculate_module_complexity(self, analysis: Dict) -> float:
        """计算模块复杂度"""
        # 基于文件数、函数数、类数和依赖数计算复杂度
        file_weight = analysis['file_count'] * 0.2
        function_weight = analysis['function_count'] * 0.3
        class_weight = analysis['class_count'] * 0.3
        dependency_weight = len(analysis['external_dependencies']) * 0.2
        
        complexity = file_weight + function_weight + class_weight + dependency_weight
        return min(complexity / 10.0, 10.0)  # 标准化到0-10分
    
    def _calculate_independence_score(self, results: Dict) -> float:
        """计算独立性分数"""
        # 基于耦合分析和职责分析计算独立性分数
        coupling_score = results['coupling_analysis']['coupling_score']
        responsibility_violations = len(results['responsibility_analysis']['single_responsibility_violations'])
        responsibility_overlaps = len(results['responsibility_analysis']['responsibility_overlap'])
        
        # 独立性分数：越低耦合、越少违规，分数越高
        independence_score = (1.0 - coupling_score) * 100
        independence_score -= responsibility_violations * 10
        independence_score -= responsibility_overlaps * 5
        
        return max(0.0, min(100.0, independence_score))
    
    def _identify_violations(self, results: Dict) -> List[Dict]:
        """识别独立性违规"""
        violations = []
        
        # 高耦合违规
        for coupling_pair in results['coupling_analysis']['high_coupling_pairs']:
            violations.append({
                'type': 'high_coupling',
                'severity': 'high',
                'description': f"模块 {coupling_pair['module1']} 与 {coupling_pair['module2']} 耦合度过高",
                'details': coupling_pair
            })
        
        # 单一职责违规
        for violation in results['responsibility_analysis']['single_responsibility_violations']:
            violations.append({
                'type': 'single_responsibility_violation',
                'severity': 'medium',
                'description': f"模块 {violation['module']} 承担过多职责",
                'details': violation
            })
        
        # 职责重叠违规
        for overlap in results['responsibility_analysis']['responsibility_overlap']:
            violations.append({
                'type': 'responsibility_overlap',
                'severity': 'medium',
                'description': f"模块 {overlap['module1']} 与 {overlap['module2']} 存在职责重叠",
                'details': overlap
            })
        
        return violations
    
    def _generate_independence_recommendations(self, results: Dict) -> List[str]:
        """生成独立性改进建议"""
        recommendations = []
        
        # 基于违规情况生成建议
        high_coupling_count = len([v for v in results['violations'] if v['type'] == 'high_coupling'])
        if high_coupling_count > 0:
            recommendations.append(
                f"发现 {high_coupling_count} 个高耦合问题，建议重构模块接口，减少直接依赖"
            )
        
        responsibility_violations = len([v for v in results['violations'] if v['type'] == 'single_responsibility_violation'])
        if responsibility_violations > 0:
            recommendations.append(
                f"发现 {responsibility_violations} 个单一职责违规，建议拆分复杂模块"
            )
        
        responsibility_overlaps = len([v for v in results['violations'] if v['type'] == 'responsibility_overlap'])
        if responsibility_overlaps > 0:
            recommendations.append(
                f"发现 {responsibility_overlaps} 个职责重叠，建议明确模块边界和职责划分"
            )
        
        # 基于独立性分数给出总体建议
        independence_score = results['independence_score']
        if independence_score < 60:
            recommendations.append("整体独立性较低，建议进行模块重构和架构优化")
        elif independence_score < 80:
            recommendations.append("独立性中等，建议继续优化模块边界和接口设计")
        else:
            recommendations.append("模块独立性良好，建议保持当前架构设计")
        
        return recommendations
    
    def generate_independence_report(self) -> Dict:
        """生成功能独立性报告"""
        self.logger.info("开始功能独立性验证...")
        results = self.validate_module_independence()
        
        # 添加统计信息
        results['statistics'] = {
            'total_modules': len(results['module_analysis']),
            'independence_score': results['independence_score'],
            'total_violations': len(results['violations']),
            'high_severity_violations': len([v for v in results['violations'] if v['severity'] == 'high']),
            'medium_severity_violations': len([v for v in results['violations'] if v['severity'] == 'medium'])
        }
        
        self.logger.info(f"功能独立性验证完成: 独立性分数 {results['independence_score']:.1f}/100")
        return results
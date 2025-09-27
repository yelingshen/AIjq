"""
智能脚本分析器 - 自动判断脚本修改规模和全局影响
"""
import os
import ast
import logging
from typing import Dict, List, Set, Tuple

class ScriptAnalyzer:
    def __init__(self, workspace_dir: str):
        self.workspace_dir = workspace_dir
        self.logger = logging.getLogger(__name__)
        
    def analyze_script_impact(self, file_path: str) -> Dict:
        """分析脚本的影响范围和修改规模"""
        result = {
            'file_path': file_path,
            'script_type': 'unknown',
            'impact_level': 'low',  # low, medium, high
            'global_dependencies': [],
            'module_imports': [],
            'function_exports': [],
            'requires_global_test': False
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 解析 Python AST
            if file_path.endswith('.py'):
                result.update(self._analyze_python_script(content, file_path))
            
            # 根据分析结果判断影响级别
            result['impact_level'] = self._determine_impact_level(result)
            result['requires_global_test'] = result['impact_level'] in ['medium', 'high']
            
        except Exception as e:
            self.logger.error(f"分析脚本失败: {file_path}, 错误: {e}")
            
        return result
    
    def _analyze_python_script(self, content: str, file_path: str) -> Dict:
        """分析 Python 脚本的依赖和影响"""
        result = {
            'script_type': 'python',
            'global_dependencies': [],
            'module_imports': [],
            'function_exports': [],
            'class_definitions': [],
            'has_main_execution': False,
            'import_count': 0
        }
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # 分析导入语句
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    result['import_count'] += 1
                    if isinstance(node, ast.ImportFrom):
                        if node.module:
                            result['module_imports'].append(node.module)
                            # 检查是否导入本地模块
                            if any(local_mod in node.module for local_mod in 
                                  ['scanner', 'utils', 'ai', 'config']):
                                result['global_dependencies'].append(node.module)
                    else:
                        for alias in node.names:
                            result['module_imports'].append(alias.name)
                
                # 分析函数定义
                elif isinstance(node, ast.FunctionDef):
                    result['function_exports'].append(node.name)
                
                # 分析类定义
                elif isinstance(node, ast.ClassDef):
                    result['class_definitions'].append(node.name)
                
                # 检查是否有主执行逻辑
                elif isinstance(node, ast.If):
                    if (isinstance(node.test, ast.Compare) and 
                        isinstance(node.test.left, ast.Name) and 
                        node.test.left.id == '__name__'):
                        result['has_main_execution'] = True
                        
        except SyntaxError as e:
            self.logger.warning(f"Python 语法解析失败: {file_path}, 错误: {e}")
            
        return result
    
    def _determine_impact_level(self, analysis: Dict) -> str:
        """根据分析结果确定影响级别"""
        # 高影响级别条件
        if (len(analysis['global_dependencies']) > 2 or 
            analysis['has_main_execution'] or
            len(analysis['function_exports']) > 5 or
            len(analysis['class_definitions']) > 2):
            return 'high'
        
        # 中等影响级别条件
        elif (len(analysis['global_dependencies']) > 0 or
              len(analysis['function_exports']) > 2 or
              analysis['import_count'] > 5):
            return 'medium'
        
        # 低影响级别
        else:
            return 'low'
    
    def scan_all_scripts(self) -> List[Dict]:
        """扫描工作区所有脚本并分析影响"""
        results = []
        
        for root, dirs, files in os.walk(self.workspace_dir):
            for file in files:
                if file.endswith(('.py', '.js', '.ts')):
                    file_path = os.path.join(root, file)
                    analysis = self.analyze_script_impact(file_path)
                    results.append(analysis)
                    
        return results
    
    def get_global_interaction_map(self) -> Dict:
        """构建全局交互关系图"""
        scripts = self.scan_all_scripts()
        interaction_map = {
            'high_impact_scripts': [],
            'medium_impact_scripts': [],
            'low_impact_scripts': [],
            'dependency_graph': {},
            'potential_conflicts': []
        }
        
        for script in scripts:
            if script['impact_level'] == 'high':
                interaction_map['high_impact_scripts'].append(script['file_path'])
            elif script['impact_level'] == 'medium':
                interaction_map['medium_impact_scripts'].append(script['file_path'])
            else:
                interaction_map['low_impact_scripts'].append(script['file_path'])
                
            # 构建依赖图
            interaction_map['dependency_graph'][script['file_path']] = script['global_dependencies']
        
        return interaction_map
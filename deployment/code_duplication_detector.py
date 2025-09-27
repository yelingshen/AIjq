"""
代码重复检测器 - 检查所有脚本中的重复运行代码和潜在冲突
"""
import os
import ast
import hashlib
import logging
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class CodeDuplicationDetector:
    def __init__(self, workspace_dir: str):
        self.workspace_dir = workspace_dir
        self.logger = logging.getLogger(__name__)
        self.duplicate_functions = {}
        self.duplicate_imports = {}
        self.execution_conflicts = []
        
    def scan_all_files(self) -> Dict:
        """扫描所有文件，检测重复和冲突"""
        results = {
            'duplicate_functions': {},
            'duplicate_imports': {},
            'execution_conflicts': [],
            'main_execution_scripts': [],
            'import_conflicts': [],
            'recommendations': []
        }
        
        python_files = self._find_python_files()
        
        # 检测重复函数
        results['duplicate_functions'] = self._detect_duplicate_functions(python_files)
        
        # 检测重复导入
        results['duplicate_imports'] = self._detect_duplicate_imports(python_files)
        
        # 检测执行冲突
        results['execution_conflicts'] = self._detect_execution_conflicts(python_files)
        
        # 检测主执行脚本
        results['main_execution_scripts'] = self._find_main_execution_scripts(python_files)
        
        # 检测导入冲突
        results['import_conflicts'] = self._detect_import_conflicts(python_files)
        
        # 生成建议
        results['recommendations'] = self._generate_recommendations(results)
        
        return results
    
    def _find_python_files(self) -> List[str]:
        """查找所有Python文件"""
        python_files = []
        for root, dirs, files in os.walk(self.workspace_dir):
            # 跳过 __pycache__ 和 .git 目录
            dirs[:] = [d for d in dirs if not d.startswith(('.git', '__pycache__', '.venv'))]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        return python_files
    
    def _detect_duplicate_functions(self, python_files: List[str]) -> Dict:
        """检测重复函数定义"""
        function_signatures = defaultdict(list)
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # 创建函数签名
                        args = [arg.arg for arg in node.args.args]
                        signature = f"{node.name}({', '.join(args)})"
                        
                        # 计算函数体的哈希值
                        body_code = ast.unparse(node) if hasattr(ast, 'unparse') else str(node.lineno)
                        body_hash = hashlib.md5(body_code.encode()).hexdigest()[:8]
                        
                        function_signatures[f"{signature}_{body_hash}"].append({
                            'file': file_path,
                            'name': node.name,
                            'line': node.lineno,
                            'signature': signature
                        })
                        
            except Exception as e:
                self.logger.warning(f"解析文件失败 {file_path}: {e}")
        
        # 找出重复的函数
        duplicates = {}
        for sig, occurrences in function_signatures.items():
            if len(occurrences) > 1:
                duplicates[sig] = occurrences
                
        return duplicates
    
    def _detect_duplicate_imports(self, python_files: List[str]) -> Dict:
        """检测重复导入"""
        import_statements = defaultdict(list)
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            import_stmt = f"import {alias.name}"
                            import_statements[import_stmt].append({
                                'file': file_path,
                                'line': node.lineno,
                                'statement': import_stmt
                            })
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            for alias in node.names:
                                import_stmt = f"from {node.module} import {alias.name}"
                                import_statements[import_stmt].append({
                                    'file': file_path,
                                    'line': node.lineno,
                                    'statement': import_stmt
                                })
                                
            except Exception as e:
                self.logger.warning(f"解析导入失败 {file_path}: {e}")
        
        # 找出在同一文件中重复的导入
        file_duplicates = {}
        for stmt, occurrences in import_statements.items():
            file_groups = defaultdict(list)
            for occ in occurrences:
                file_groups[occ['file']].append(occ)
            
            for file_path, file_occs in file_groups.items():
                if len(file_occs) > 1:
                    if file_path not in file_duplicates:
                        file_duplicates[file_path] = []
                    file_duplicates[file_path].append({
                        'statement': stmt,
                        'occurrences': file_occs
                    })
        
        return file_duplicates
    
    def _detect_execution_conflicts(self, python_files: List[str]) -> List[Dict]:
        """检测执行冲突"""
        conflicts = []
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检测可能的冲突模式
                conflict_patterns = [
                    ('Flask app.run', 'app.run'),
                    ('服务器启动', 'server.'),
                    ('主循环', 'while True'),
                    ('全局变量修改', 'global '),
                    ('配置文件写入', 'open(.*w')
                ]
                
                for pattern_name, pattern in conflict_patterns:
                    if pattern in content:
                        conflicts.append({
                            'file': file_path,
                            'type': pattern_name,
                            'pattern': pattern,
                            'potential_conflict': True
                        })
                        
            except Exception as e:
                self.logger.warning(f"检测执行冲突失败 {file_path}: {e}")
        
        return conflicts
    
    def _find_main_execution_scripts(self, python_files: List[str]) -> List[Dict]:
        """查找主执行脚本"""
        main_scripts = []
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                has_main_check = False
                has_execution_code = False
                
                for node in ast.walk(tree):
                    # 检查 if __name__ == '__main__'
                    if (isinstance(node, ast.If) and 
                        isinstance(node.test, ast.Compare) and
                        isinstance(node.test.left, ast.Name) and
                        node.test.left.id == '__name__'):
                        has_main_check = True
                    
                    # 检查是否有执行代码
                    if (isinstance(node, (ast.FunctionDef, ast.ClassDef)) or
                        (isinstance(node, ast.Expr) and 
                         isinstance(node.value, ast.Call))):
                        has_execution_code = True
                
                if has_main_check or has_execution_code:
                    main_scripts.append({
                        'file': file_path,
                        'has_main_check': has_main_check,
                        'has_execution_code': has_execution_code,
                        'is_entry_point': has_main_check and has_execution_code
                    })
                    
            except Exception as e:
                self.logger.warning(f"分析主执行脚本失败 {file_path}: {e}")
        
        return main_scripts
    
    def _detect_import_conflicts(self, python_files: List[str]) -> List[Dict]:
        """检测导入冲突"""
        conflicts = []
        
        # 检测可能的导入冲突
        conflicting_imports = [
            (['flask', 'django'], '不应同时使用Flask和Django'),
            (['asyncio', 'threading'], '需要注意异步和线程的兼容性'),
            (['numpy', 'tensorflow'], '需要确保版本兼容'),
        ]
        
        all_imports = set()
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            all_imports.add(alias.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            all_imports.add(node.module.split('.')[0])
                            
            except Exception as e:
                continue
        
        for conflict_group, message in conflicting_imports:
            found_conflicts = [imp for imp in conflict_group if imp in all_imports]
            if len(found_conflicts) > 1:
                conflicts.append({
                    'conflicting_imports': found_conflicts,
                    'message': message,
                    'severity': 'warning'
                })
        
        return conflicts
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        # 重复函数建议
        if results['duplicate_functions']:
            recommendations.append(
                f"发现 {len(results['duplicate_functions'])} 个重复函数定义，"
                "建议将公共函数提取到工具模块中"
            )
        
        # 重复导入建议
        if results['duplicate_imports']:
            recommendations.append(
                f"发现 {len(results['duplicate_imports'])} 个文件有重复导入，"
                "建议清理重复的import语句"
            )
        
        # 执行冲突建议
        execution_conflicts = len(results['execution_conflicts'])
        if execution_conflicts > 0:
            recommendations.append(
                f"发现 {execution_conflicts} 个潜在的执行冲突，"
                "建议检查并隔离并发执行的代码"
            )
        
        # 主执行脚本建议
        main_scripts = len(results['main_execution_scripts'])
        if main_scripts > 3:
            recommendations.append(
                f"发现 {main_scripts} 个主执行脚本，"
                "建议整合为统一的入口点以避免冲突"
            )
        
        # 导入冲突建议
        if results['import_conflicts']:
            for conflict in results['import_conflicts']:
                recommendations.append(f"导入冲突警告: {conflict['message']}")
        
        return recommendations
    
    def generate_report(self) -> Dict:
        """生成完整的检测报告"""
        self.logger.info("开始代码重复检测...")
        results = self.scan_all_files()
        
        # 统计信息
        stats = {
            'total_files_scanned': len(self._find_python_files()),
            'duplicate_functions_found': len(results['duplicate_functions']),
            'duplicate_imports_found': len(results['duplicate_imports']),
            'execution_conflicts_found': len(results['execution_conflicts']),
            'main_scripts_found': len(results['main_execution_scripts']),
            'import_conflicts_found': len(results['import_conflicts'])
        }
        
        results['statistics'] = stats
        
        self.logger.info(f"代码重复检测完成: {stats}")
        return results
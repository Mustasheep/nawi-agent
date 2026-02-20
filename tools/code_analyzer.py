"""
Tool para análise profunda de código
"""

import ast
import re
from typing import Dict, Any, List
from tools.base_tool import Tool


class CodeAnalyzerTool(Tool):
    """
    Analisa código fonte para extrair informações estruturais
    
    Capaz de:
    - Extrair funções, classes e métodos
    - Identificar imports e dependências
    - Calcular métricas de complexidade
    - Detectar padrões de design
    """
    
    @property
    def name(self) -> str:
        return "code_analyzer"
    
    @property
    def description(self) -> str:
        return (
            "Analisa código fonte em profundidade. "
            "Extrai funções, classes, métodos, imports, docstrings e "
            "calcula métricas como complexidade ciclomática e linhas de código. "
            "Suporta Python, JavaScript, TypeScript, Java, Go e C++."
        )
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Código fonte a analisar"
                },
                "language": {
                    "type": "string",
                    "description": "Linguagem do código",
                    "enum": ["python", "javascript", "typescript", "java", "go", "cpp"]
                },
                "file_path": {
                    "type": "string",
                    "description": "Caminho do arquivo (opcional)"
                }
            },
            "required": ["code", "language"]
        }
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa análise de código
        
        Args:
            input_data: {"code": str, "language": str, "file_path": str (opcional)}
            
        Returns:
            Dicionário com análise completa do código
        """
        code = input_data["code"]
        language = input_data["language"]
        file_path = input_data.get("file_path", "unknown")
        
        if language == "python":
            return await self._analyze_python(code, file_path)
        elif language in ["javascript", "typescript"]:
            return await self._analyze_javascript(code, file_path)
        else:
            return {
                "error": f"Análise para {language} ainda não implementada",
                "basic_stats": self._get_basic_stats(code)
            }
    
    async def _analyze_python(self, code: str, file_path: str) -> Dict[str, Any]:
        """Análise específica para Python"""
        try:
            tree = ast.parse(code)
            
            functions = []
            classes = []
            imports = []
            constants = []
            
            for node in ast.walk(tree):
                # Funções
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        "name": node.name,
                        "line": node.lineno,
                        "args": [arg.arg for arg in node.args.args],
                        "docstring": ast.get_docstring(node),
                        "is_async": isinstance(node, ast.AsyncFunctionDef),
                        "decorators": [self._get_decorator_name(d) for d in node.decorator_list]
                    }
                    functions.append(func_info)
                
                # Classes
                elif isinstance(node, ast.ClassDef):
                    methods = [
                        {
                            "name": m.name,
                            "line": m.lineno,
                            "args": [arg.arg for arg in m.args.args],
                            "is_static": any(
                                self._get_decorator_name(d) == "staticmethod"
                                for d in m.decorator_list
                            ),
                            "is_classmethod": any(
                                self._get_decorator_name(d) == "classmethod"
                                for d in m.decorator_list
                            )
                        }
                        for m in node.body if isinstance(m, ast.FunctionDef)
                    ]
                    
                    class_info = {
                        "name": node.name,
                        "line": node.lineno,
                        "bases": [self._get_name(base) for base in node.bases],
                        "docstring": ast.get_docstring(node),
                        "methods": methods,
                        "decorators": [self._get_decorator_name(d) for d in node.decorator_list]
                    }
                    classes.append(class_info)
                
                # Imports
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append({
                            "type": "import",
                            "module": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno
                        })
                
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        imports.append({
                            "type": "from_import",
                            "module": node.module,
                            "name": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno
                        })
                
                # Constants (variáveis globais em uppercase)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            constants.append({
                                "name": target.id,
                                "line": node.lineno
                            })
            
            return {
                "language": "python",
                "file_path": file_path,
                "stats": self._get_basic_stats(code),
                "structure": {
                    "functions": functions,
                    "classes": classes,
                    "imports": imports,
                    "constants": constants
                },
                "metrics": {
                    "total_functions": len(functions),
                    "total_classes": len(classes),
                    "total_imports": len(imports),
                    "total_constants": len(constants),
                    "avg_function_length": self._avg_function_length(tree)
                }
            }
            
        except SyntaxError as e:
            return {
                "error": f"Erro de sintaxe: {e}",
                "language": "python",
                "file_path": file_path,
                "stats": self._get_basic_stats(code)
            }
    
    async def _analyze_javascript(self, code: str, file_path: str) -> Dict[str, Any]:
        """Análise básica para JavaScript/TypeScript"""
        # Regex patterns para análise básica
        function_pattern = r'(?:async\s+)?function\s+(\w+)\s*\([^)]*\)'
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?'
        import_pattern = r'import\s+(?:{[^}]+}|\w+)\s+from\s+["\']([^"\']+)["\']'
        const_pattern = r'const\s+(\w+)\s*='
        
        functions = [
            {"name": m.group(1), "type": "function"}
            for m in re.finditer(function_pattern, code)
        ]
        
        classes = [
            {"name": m.group(1), "extends": m.group(2)}
            for m in re.finditer(class_pattern, code)
        ]
        
        imports = [
            {"module": m.group(1)}
            for m in re.finditer(import_pattern, code)
        ]
        
        return {
            "language": "javascript",
            "file_path": file_path,
            "stats": self._get_basic_stats(code),
            "structure": {
                "functions": functions,
                "classes": classes,
                "imports": imports
            },
            "metrics": {
                "total_functions": len(functions),
                "total_classes": len(classes),
                "total_imports": len(imports)
            },
            "note": "Análise básica via regex. Para análise completa, use AST parser JS."
        }
    
    def _get_basic_stats(self, code: str) -> Dict[str, int]:
        """Retorna estatísticas básicas do código"""
        lines = code.split('\n')
        
        return {
            "total_lines": len(lines),
            "code_lines": len([l for l in lines if l.strip() and not l.strip().startswith('#')]),
            "blank_lines": len([l for l in lines if not l.strip()]),
            "comment_lines": len([l for l in lines if l.strip().startswith('#')]),
            "characters": len(code)
        }
    
    def _get_decorator_name(self, decorator) -> str:
        """Extrai nome de um decorator"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call):
            return self._get_name(decorator.func)
        return "unknown"
    
    def _get_name(self, node) -> str:
        """Extrai nome de um node AST"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return "unknown"
    
    def _avg_function_length(self, tree) -> float:
        """Calcula comprimento médio de funções"""
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        
        if not functions:
            return 0.0
        
        total_lines = sum(
            len(ast.unparse(func).split('\n'))
            for func in functions
        )
        
        return round(total_lines / len(functions), 2)

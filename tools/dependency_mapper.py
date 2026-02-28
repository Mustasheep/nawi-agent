"""
Tool para mapear dependências do projeto
"""

import re
import json
from typing import Dict, Any, List, Set
from tools.base_tool import Tool


class DependencyMapperTool(Tool):
    """
    Mapeia dependências e relacionamentos entre módulos
    
    Identifica:
    - Dependências diretas e transitivas
    - Imports entre módulos
    - Dependências externas (npm, pip, maven, etc)
    - Grafos de dependências
    - Dependências circulares
    """
    
    @property
    def name(self) -> str:
        return "dependency_mapper"
    
    @property
    def description(self) -> str:
        return (
            "Mapeia todas as dependências do projeto. "
            "Analisa imports, requirements, package.json, pom.xml, go.mod "
            "e outros arquivos de dependências. Identifica dependências "
            "diretas, transitivas e circulares. Retorna grafo de dependências."
        )
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "files": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "content": {"type": "string"},
                            "type": {"type": "string"}
                        }
                    },
                    "description": "Lista de arquivos do projeto"
                },
                "language": {
                    "type": "string",
                    "description": "Linguagem principal do projeto",
                    "enum": ["python", "javascript", "typescript", "java", "go"]
                }
            },
            "required": ["files", "language"]
        }
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mapeia dependências do projeto
        
        Args:
            input_data: Arquivos e linguagem do projeto
            
        Returns:
            Mapa completo de dependências
        """
        files = input_data["files"]
        language = input_data["language"]
        
        # Mapeia dependências externas
        external_deps = self._extract_external_dependencies(files, language)
        
        # Mapeia dependências internas
        internal_deps = self._extract_internal_dependencies(files, language)
        
        # Detecta dependências circulares
        circular_deps = self._detect_circular_dependencies(internal_deps)
        
        # Calcula métricas
        metrics = self._calculate_dependency_metrics(internal_deps, external_deps)
        
        return {
            "external_dependencies": external_deps,
            "internal_dependencies": internal_deps,
            "circular_dependencies": circular_deps,
            "metrics": metrics,
            "dependency_graph": self._build_graph(internal_deps),
            "recommendations": self._get_dependency_recommendations(
                circular_deps, metrics
            )
        }
    
    def _extract_external_dependencies(
        self,
        files: List[Dict],
        language: str
    ) -> Dict[str, Any]:
        """Extrai dependências externas de arquivos de configuração"""
        dependencies = {
            "production": [],
            "development": [],
            "total_count": 0
        }
        
        for file_info in files:
            path = file_info["path"]
            content = file_info["content"]
            
            # Python - requirements.txt, setup.py, pyproject.toml
            if language == "python":
                if "requirements" in path.lower():
                    deps = self._parse_requirements_txt(content)
                    dependencies["production"].extend(deps)
                
                elif "setup.py" in path:
                    deps = self._parse_setup_py(content)
                    dependencies["production"].extend(deps)
                
                elif "pyproject.toml" in path:
                    deps = self._parse_pyproject_toml(content)
                    dependencies["production"].extend(deps)
            
            # JavaScript/TypeScript - package.json
            elif language in ["javascript", "typescript"]:
                if "package.json" in path:
                    deps = self._parse_package_json(content)
                    dependencies.update(deps)
            
            # Java - pom.xml, build.gradle
            elif language == "java":
                if "pom.xml" in path:
                    deps = self._parse_pom_xml(content)
                    dependencies["production"].extend(deps)
            
            # Go - go.mod
            elif language == "go":
                if "go.mod" in path:
                    deps = self._parse_go_mod(content)
                    dependencies["production"].extend(deps)
        
        # Remove duplicatas
        dependencies["production"] = list(set(dependencies["production"]))
        dependencies["development"] = list(set(dependencies["development"]))
        dependencies["total_count"] = (
            len(dependencies["production"]) +
            len(dependencies["development"])
        )
        
        return dependencies
    
    def _extract_internal_dependencies(
        self,
        files: List[Dict],
        language: str
    ) -> Dict[str, List[str]]:
        """Extrai dependências internas entre módulos"""
        dependency_map = {}
        
        for file_info in files:
            path = file_info["path"]
            content = file_info["content"]
            
            # Extrai imports baseado na linguagem
            if language == "python":
                imports = self._extract_python_imports(content)
            elif language in ["javascript", "typescript"]:
                imports = self._extract_js_imports(content)
            else:
                imports = []
            
            # Filtra apenas imports internos (relativos ao projeto)
            internal_imports = [
                imp for imp in imports
                if imp.startswith('.') or not any(
                    imp.startswith(pkg)
                    for pkg in ['os', 'sys', 'json', 'react', 'vue']
                )
            ]
            
            if internal_imports:
                dependency_map[path] = internal_imports
        
        return dependency_map
    
    def _detect_circular_dependencies(
        self,
        dependency_map: Dict[str, List[str]]
    ) -> List[List[str]]:
        """Detecta dependências circulares"""
        circular = []
        visited = set()
        rec_stack = set()
        
        def dfs(node: str, path: List[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in dependency_map.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor, path.copy()):
                        return True
                elif neighbor in rec_stack:
                    # Encontrou ciclo
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    if cycle not in circular:
                        circular.append(cycle)
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in dependency_map:
            if node not in visited:
                dfs(node, [])
        
        return circular
    
    def _calculate_dependency_metrics(
        self,
        internal_deps: Dict,
        external_deps: Dict
    ) -> Dict[str, Any]:
        """Calcula métricas de dependências"""
        total_internal = sum(len(deps) for deps in internal_deps.values())
        total_external = external_deps["total_count"]
        
        # Módulo com mais dependências
        max_deps_module = None
        max_deps_count = 0
        
        for module, deps in internal_deps.items():
            if len(deps) > max_deps_count:
                max_deps_count = len(deps)
                max_deps_module = module
        
        return {
            "total_internal_dependencies": total_internal,
            "total_external_dependencies": total_external,
            "avg_dependencies_per_module": (
                round(total_internal / len(internal_deps), 2)
                if internal_deps else 0
            ),
            "most_dependent_module": {
                "path": max_deps_module,
                "count": max_deps_count
            } if max_deps_module else None,
            "coupling_level": self._calculate_coupling(internal_deps)
        }
    
    def _calculate_coupling(self, dependency_map: Dict) -> str:
        """Calcula nível de acoplamento"""
        if not dependency_map:
            return "none"
        
        avg_deps = sum(len(deps) for deps in dependency_map.values()) / len(dependency_map)
        
        if avg_deps > 10:
            return "high"
        elif avg_deps > 5:
            return "medium"
        else:
            return "low"
    
    def _build_graph(self, dependency_map: Dict) -> str:
        """Constrói representação do grafo de dependências"""
        if not dependency_map:
            return "No internal dependencies"
        
        graph_lines = []
        
        for module, deps in dependency_map.items():
            module_name = module.split('/')[-1]
            
            for dep in deps:
                dep_name = dep.split('/')[-1] if '/' in dep else dep
                graph_lines.append(f"{module_name} -> {dep_name}")
        
        return "\n".join(graph_lines[:50])  # Limita a 50 linhas
    
    def _get_dependency_recommendations(
        self,
        circular_deps: List,
        metrics: Dict
    ) -> List[str]:
        """Gera recomendações sobre dependências"""
        recommendations = []
        
        if circular_deps:
            recommendations.append(
                f"⚠️ {len(circular_deps)} dependência(s) circular(es) detectada(s). "
                "Considere refatorar para evitar acoplamento."
            )
        
        coupling = metrics.get("coupling_level", "unknown")
        
        if coupling == "high":
            recommendations.append(
                "Alto acoplamento detectado. Considere aplicar Dependency Injection "
                "ou Inversion of Control."
            )
        
        external_count = metrics.get("total_external_dependencies", 0)
        
        if external_count > 50:
            recommendations.append(
                f"{external_count} dependências externas. Avalie se todas são necessárias. "
                "Muitas dependências aumentam risco de segurança e tamanho do bundle."
            )
        
        if not recommendations:
            recommendations.append("✔ Estrutura de dependências saudável")
        
        return recommendations
    
    # Helper parsers
    def _parse_requirements_txt(self, content: str) -> List[str]:
        """Parse requirements.txt"""
        deps = []
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                # Remove version specifiers
                pkg = re.split(r'[><=!]', line)[0].strip()
                deps.append(pkg)
        return deps
    
    def _parse_setup_py(self, content: str) -> List[str]:
        """Parse setup.py"""
        deps = []
        # Regex simples para extrair install_requires
        match = re.search(r'install_requires\s*=\s*\[(.*?)\]', content, re.DOTALL)
        if match:
            deps_str = match.group(1)
            deps = [
                d.strip().strip('"\'').split('>=')[0].split('==')[0]
                for d in deps_str.split(',')
                if d.strip()
            ]
        return deps
    
    def _parse_pyproject_toml(self, content: str) -> List[str]:
        """Parse pyproject.toml (básico)"""
        deps = []
        in_deps_section = False
        
        for line in content.split('\n'):
            if '[tool.poetry.dependencies]' in line or '[project.dependencies]' in line:
                in_deps_section = True
                continue
            
            if in_deps_section:
                if line.startswith('['):
                    break
                
                if '=' in line:
                    pkg = line.split('=')[0].strip()
                    if pkg and pkg != 'python':
                        deps.append(pkg)
        
        return deps
    
    def _parse_package_json(self, content: str) -> Dict[str, List[str]]:
        """Parse package.json"""
        try:
            data = json.loads(content)
            return {
                "production": list(data.get("dependencies", {}).keys()),
                "development": list(data.get("devDependencies", {}).keys()),
                "total_count": len(data.get("dependencies", {})) + len(data.get("devDependencies", {}))
            }
        except:
            return {"production": [], "development": [], "total_count": 0}
    
    def _parse_pom_xml(self, content: str) -> List[str]:
        """Parse pom.xml (básico)"""
        deps = []
        # Regex para <artifactId>
        matches = re.findall(r'<artifactId>(.*?)</artifactId>', content)
        deps.extend(matches)
        return list(set(deps))
    
    def _parse_go_mod(self, content: str) -> List[str]:
        """Parse go.mod"""
        deps = []
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('//') and not line.startswith('module'):
                if line.startswith('require'):
                    continue
                # Format: "github.com/user/repo v1.2.3"
                parts = line.split()
                if len(parts) >= 1:
                    deps.append(parts[0])
        return deps
    
    def _extract_python_imports(self, content: str) -> List[str]:
        """Extrai imports Python"""
        imports = []
        
        for line in content.split('\n'):
            line = line.strip()
            
            if line.startswith('import '):
                pkg = line.replace('import ', '').split(' as ')[0].split(',')[0].strip()
                imports.append(pkg)
            
            elif line.startswith('from '):
                match = re.match(r'from\s+([\w.]+)\s+import', line)
                if match:
                    imports.append(match.group(1))
        
        return imports
    
    def _extract_js_imports(self, content: str) -> List[str]:
        """Extrai imports JavaScript/TypeScript"""
        imports = []
        
        # import X from 'module'
        pattern1 = r"import\s+.*?\s+from\s+['\"]([^'\"]+)['\"]"
        imports.extend(re.findall(pattern1, content))
        
        # import 'module'
        pattern2 = r"import\s+['\"]([^'\"]+)['\"]"
        imports.extend(re.findall(pattern2, content))
        
        # require('module')
        pattern3 = r"require\(['\"]([^'\"]+)['\"]\)"
        imports.extend(re.findall(pattern3, content))
        
        return list(set(imports))

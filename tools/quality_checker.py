"""
Tool para verificação de qualidade de código
"""

import re
from typing import Dict, Any, List
from tools.base_tool import Tool


class QualityCheckerTool(Tool):
    """
    Verifica qualidade do código
    
    Analisa:
    - Cobertura de testes
    - Documentação (docstrings, comentários)
    - Convenções de nomenclatura
    - Complexidade de código
    - Code smells
    - Boas práticas
    """
    
    @property
    def name(self) -> str:
        return "quality_checker"
    
    @property
    def description(self) -> str:
        return (
            "Verifica qualidade do código. Analisa documentação, "
            "cobertura de testes, convenções de nomenclatura, "
            "complexidade, code smells e boas práticas. "
            "Retorna score de qualidade e recomendações de melhoria."
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
                            "language": {"type": "string"}
                        }
                    },
                    "description": "Lista de arquivos a analisar"
                }
            },
            "required": ["files"]
        }
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verifica qualidade do código
        
        Args:
            input_data: Lista de arquivos
            
        Returns:
            Relatório completo de qualidade
        """
        files = input_data["files"]
        
        # Análises individuais
        documentation_score = self._check_documentation(files)
        testing_score = self._check_testing(files)
        naming_score = self._check_naming_conventions(files)
        complexity_score = self._check_complexity(files)
        best_practices_score = self._check_best_practices(files)
        
        # Score geral (média ponderada)
        overall_score = self._calculate_overall_score({
            "documentation": documentation_score,
            "testing": testing_score,
            "naming": naming_score,
            "complexity": complexity_score,
            "best_practices": best_practices_score
        })
        
        # Recomendações
        recommendations = self._generate_recommendations({
            "documentation": documentation_score,
            "testing": testing_score,
            "naming": naming_score,
            "complexity": complexity_score,
            "best_practices": best_practices_score
        })
        
        return {
            "overall_quality_score": overall_score,
            "quality_grade": self._get_grade(overall_score),
            "detailed_scores": {
                "documentation": documentation_score,
                "testing": testing_score,
                "naming_conventions": naming_score,
                "code_complexity": complexity_score,
                "best_practices": best_practices_score
            },
            "recommendations": recommendations,
            "summary": self._generate_summary(overall_score, recommendations)
        }
    
    def _check_documentation(self, files: List[Dict]) -> Dict[str, Any]:
        """Verifica qualidade da documentação"""
        total_functions = 0
        documented_functions = 0
        total_classes = 0
        documented_classes = 0
        
        for file_info in files:
            content = file_info["content"]
            language = file_info.get("language", "unknown")
            
            if language == "python":
                # Funções
                functions = re.findall(r'def\s+(\w+)\s*\(', content)
                total_functions += len(functions)
                
                # Docstrings em funções
                func_with_docs = re.findall(
                    r'def\s+\w+\s*\([^)]*\)\s*:\s*"""',
                    content
                )
                documented_functions += len(func_with_docs)
                
                # Classes
                classes = re.findall(r'class\s+(\w+)', content)
                total_classes += len(classes)
                
                # Docstrings em classes
                class_with_docs = re.findall(
                    r'class\s+\w+[^:]*:\s*"""',
                    content
                )
                documented_classes += len(class_with_docs)
        
        # Calcula porcentagens
        func_coverage = (
            (documented_functions / total_functions * 100)
            if total_functions > 0 else 0
        )
        
        class_coverage = (
            (documented_classes / total_classes * 100)
            if total_classes > 0 else 0
        )
        
        overall_coverage = (func_coverage + class_coverage) / 2 if (total_functions + total_classes) > 0 else 0
        
        return {
            "score": round(overall_coverage, 2),
            "function_coverage": round(func_coverage, 2),
            "class_coverage": round(class_coverage, 2),
            "total_items": total_functions + total_classes,
            "documented_items": documented_functions + documented_classes
        }
    
    def _check_testing(self, files: List[Dict]) -> Dict[str, Any]:
        """Verifica presença e qualidade de testes"""
        test_files = 0
        total_files = len(files)
        test_functions = 0
        
        for file_info in files:
            path = file_info["path"]
            content = file_info["content"]
            
            # Identifica arquivos de teste
            if any(indicator in path.lower() for indicator in ['test_', '_test', 'spec', 'test/']):
                test_files += 1
                
                # Conta funções de teste
                test_functions += len(re.findall(r'def\s+test_\w+', content))
                test_functions += len(re.findall(r'it\s*\(|test\s*\(', content))
        
        # Estima cobertura (simplificado)
        estimated_coverage = min((test_files / max(total_files * 0.3, 1)) * 100, 100)
        
        return {
            "score": round(estimated_coverage, 2),
            "test_files": test_files,
            "total_files": total_files,
            "test_functions": test_functions,
            "has_tests": test_files > 0
        }
    
    def _check_naming_conventions(self, files: List[Dict]) -> Dict[str, Any]:
        """Verifica convenções de nomenclatura"""
        violations = []
        total_checks = 0
        
        for file_info in files:
            content = file_info["content"]
            language = file_info.get("language", "python")
            
            if language == "python":
                # Classes devem ser PascalCase
                classes = re.findall(r'class\s+([a-z_]\w*)', content)
                violations.extend([f"Classe '{c}' não está em PascalCase" for c in classes])
                total_checks += len(re.findall(r'class\s+(\w+)', content))
                
                # Funções devem ser snake_case
                functions = re.findall(r'def\s+([A-Z]\w*)\s*\(', content)
                violations.extend([f"Função '{f}' não está em snake_case" for f in functions])
                total_checks += len(re.findall(r'def\s+(\w+)', content))
                
                # Constantes devem ser UPPER_CASE
                constants = re.findall(r'^([a-z_]\w+)\s*=\s*["\'\d]', content, re.MULTILINE)
                # Filtra apenas constantes óbvias (simplificado)
                total_checks += 1  # Simplified
        
        compliance_rate = ((total_checks - len(violations)) / max(total_checks, 1)) * 100
        
        return {
            "score": round(compliance_rate, 2),
            "violations": violations[:10],  # Top 10
            "total_violations": len(violations),
            "total_checks": total_checks
        }
    
    def _check_complexity(self, files: List[Dict]) -> Dict[str, Any]:
        """Verifica complexidade do código"""
        complex_functions = []
        total_functions = 0
        
        for file_info in files:
            content = file_info["content"]
            
            # Identifica funções
            function_pattern = r'def\s+(\w+)\s*\([^)]*\):(.*?)(?=\ndef\s|\nclass\s|\Z)'
            functions = re.findall(function_pattern, content, re.DOTALL)
            
            for func_name, func_body in functions:
                total_functions += 1
                
                # Conta condicionais e loops (estimativa de complexidade)
                complexity = 1  # Base
                complexity += len(re.findall(r'\bif\b', func_body))
                complexity += len(re.findall(r'\bfor\b', func_body))
                complexity += len(re.findall(r'\bwhile\b', func_body))
                complexity += len(re.findall(r'\band\b|\bor\b', func_body))
                
                if complexity > 10:
                    complex_functions.append({
                        "name": func_name,
                        "complexity": complexity
                    })
        
        # Score baseado em funções complexas
        complexity_score = max(0, 100 - (len(complex_functions) / max(total_functions, 1) * 100))
        
        return {
            "score": round(complexity_score, 2),
            "complex_functions": complex_functions[:5],  # Top 5
            "total_complex": len(complex_functions),
            "total_functions": total_functions
        }
    
    def _check_best_practices(self, files: List[Dict]) -> Dict[str, Any]:
        """Verifica seguimento de boas práticas"""
        issues = []
        checks_passed = 0
        total_checks = 0
        
        for file_info in files:
            content = file_info["content"]
            path = file_info["path"]
            
            # Check 1: Arquivo não muito grande (< 500 linhas)
            total_checks += 1
            lines = len(content.split('\n'))
            if lines > 500:
                issues.append(f"{path}: Arquivo muito grande ({lines} linhas)")
            else:
                checks_passed += 1
            
            # Check 2: Sem hardcoded secrets
            total_checks += 1
            if re.search(r'(password|secret|api_key)\s*=\s*["\'][^"\']+["\']', content, re.IGNORECASE):
                issues.append(f"{path}: Possível secret hardcoded")
            else:
                checks_passed += 1
            
            # Check 3: Imports organizados
            total_checks += 1
            import_section = '\n'.join(content.split('\n')[:30])
            if 'import' in import_section:
                # Verifica se há imports após código
                rest = '\n'.join(content.split('\n')[30:])
                if 'import ' in rest and 'def ' in rest:
                    issues.append(f"{path}: Imports não estão no topo")
                else:
                    checks_passed += 1
            else:
                checks_passed += 1
            
            # Check 4: Sem TODOs/FIXMEs excessivos
            total_checks += 1
            todos = len(re.findall(r'TODO|FIXME', content))
            if todos > 5:
                issues.append(f"{path}: Muitos TODOs/FIXMEs ({todos})")
            else:
                checks_passed += 1
        
        compliance_rate = (checks_passed / max(total_checks, 1)) * 100
        
        return {
            "score": round(compliance_rate, 2),
            "issues": issues[:10],
            "total_issues": len(issues),
            "checks_passed": checks_passed,
            "total_checks": total_checks
        }
    
    def _calculate_overall_score(self, scores: Dict[str, Dict]) -> float:
        """Calcula score geral ponderado"""
        weights = {
            "documentation": 0.25,
            "testing": 0.30,
            "naming": 0.15,
            "complexity": 0.15,
            "best_practices": 0.15
        }
        
        total = 0.0
        for category, weight in weights.items():
            total += scores[category]["score"] * weight
        
        return round(total, 2)
    
    def _get_grade(self, score: float) -> str:
        """Converte score em nota"""
        if score >= 90:
            return "A (Excelente)"
        elif score >= 80:
            return "B (Bom)"
        elif score >= 70:
            return "C (Regular)"
        elif score >= 60:
            return "D (Precisa Melhorar)"
        else:
            return "F (Inadequado)"
    
    def _generate_recommendations(self, scores: Dict[str, Dict]) -> List[str]:
        """Gera recomendações baseadas nos scores"""
        recommendations = []
        
        for category, data in scores.items():
            score = data["score"]
            
            if category == "documentation" and score < 70:
                recommendations.append(
                    f"↳ Documentação: {score:.1f}% - Adicione docstrings em "
                    "funções e classes. Use padrões como Google Style ou NumPy Style."
                )
            
            elif category == "testing" and score < 70:
                recommendations.append(
                    f"↳ Testes: {score:.1f}% - Implemente testes unitários. "
                    "Considere usar pytest, unittest ou jest."
                )
            
            elif category == "naming" and score < 80:
                recommendations.append(
                    f"↳ Nomenclatura: {score:.1f}% - Siga convenções: "
                    "PascalCase para classes, snake_case para funções."
                )
            
            elif category == "complexity" and score < 70:
                recommendations.append(
                    f"↳ Complexidade: {score:.1f}% - Refatore funções complexas. "
                    "Divida em funções menores e mais testáveis."
                )
            
            elif category == "best_practices" and score < 75:
                recommendations.append(
                    f"↳ Boas Práticas: {score:.1f}% - Organize imports, "
                    "evite hardcoded secrets, reduza TODOs."
                )
        
        if not recommendations:
            recommendations.append("✔ Código de alta qualidade!")
        
        return recommendations
    
    def _generate_summary(self, overall_score: float, recommendations: List[str]) -> str:
        """Gera resumo executivo"""
        grade = self._get_grade(overall_score)
        
        summary = f"Score Geral: {overall_score:.1f}/100 - {grade}\n\n"
        
        if overall_score >= 85:
            summary += "Código bem estruturado e de alta qualidade. "
        elif overall_score >= 70:
            summary += "Código funcional com espaço para melhorias. "
        else:
            summary += "Código necessita de atenção urgente em várias áreas. "
        
        summary += f"\n\nPrincipais ações: {len(recommendations)} recomendação(ões)."
        
        return summary

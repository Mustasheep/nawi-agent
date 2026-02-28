"""
Construtor de contexto para enviar ao Claude
"""

from typing import Dict, List, Any


class ContextBuilder:
    """
    Constrói contexto estruturado dos arquivos para o Claude
    """
    
    def build_context(
        self,
        files_data: Dict[str, List[Dict]],
        project_name: str,
        max_content_per_file: int = 2000
    ) -> str:
        """
        Constrói contexto completo
        
        Args:
            files_data: Dados dos arquivos escaneados
            project_name: Nome do projeto
            max_content_per_file: Máximo de caracteres por arquivo
            
        Returns:
            Contexto formatado em markdown
        """
        context = f"# Análise do Projeto: {project_name}\n\n"
        context += self._build_overview(files_data)
        context += "\n\n"
        context += self._build_file_sections(files_data, max_content_per_file)
        context += "\n\n"
        context += self._build_instructions()
        
        return context
    
    def _build_overview(self, files_data: Dict[str, List[Dict]]) -> str:
        """Constrói visão geral do projeto"""
        overview = "## Visão Geral do Projeto\n\n"
        
        total_files = sum(len(files) for files in files_data.values())
        total_lines = sum(
            sum(f['lines'] for f in files)
            for files in files_data.values()
        )
        
        overview += f"- **Total de arquivos analisados:** {total_files}\n"
        overview += f"- **Total de linhas de código:** {total_lines:,}\n\n"
        
        overview += "### Distribuição por Tipo:\n\n"
        
        for file_type, files in files_data.items():
            if files:
                type_lines = sum(f['lines'] for f in files)
                overview += f"- **{file_type.title()}:** {len(files)} arquivos, {type_lines:,} linhas\n"
        
        return overview
    
    def _build_file_sections(
        self,
        files_data: Dict[str, List[Dict]],
        max_content: int
    ) -> str:
        """Constrói seções de arquivos"""
        sections = "## Arquivos do Projeto\n\n"
        
        for file_type, files in files_data.items():
            if not files:
                continue
            
            sections += f"### {file_type.title()} ({len(files)} arquivos)\n\n"
            
            for file_info in files:
                sections += f"#### `{file_info['relative_path']}`\n\n"
                sections += f"- **Linhas:** {file_info['lines']}\n"
                sections += f"- **Tamanho:** {file_info['size']:,} bytes\n\n"
                
                # Conteúdo truncado se necessário
                content = file_info['content']
                if len(content) > max_content:
                    content = content[:max_content] + "\n\n... (truncado)"
                
                # Determina linguagem para syntax highlighting
                lang = self._get_language_for_highlighting(file_info['extension'])
                
                sections += f"```{lang}\n{content}\n```\n\n"
        
        return sections
    
    def _build_instructions(self) -> str:
        """Constrói instruções para o Claude"""
        return """## Instruções

Analise os arquivos acima e utilize as tools disponíveis para:

1. **Análise de Código** (`code_analyzer`): Extraia estrutura, funções, classes e métricas
2. **Detecção de Arquitetura** (`architecture_detector`): Identifique padrões arquiteturais
3. **Mapeamento de Dependências** (`dependency_mapper`): Mapeie todas as dependências
4. **Verificação de Qualidade** (`quality_checker`): Avalie qualidade do código

Após usar as tools, gere uma documentação completa e profissional.
"""
    
    def _get_language_for_highlighting(self, extension: str) -> str:
        """Retorna linguagem para syntax highlighting"""
        lang_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.tf': 'hcl',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown',
            '.toml': 'toml',
            '.ini': 'ini',
            '.sql': 'sql'
        }
        
        return lang_map.get(extension, '')
    
    def build_single_file_context(
        self,
        file_info: Dict[str, Any],
        file_type: str
    ) -> str:
        """Constrói contexto para arquivo único"""
        context = f"# Documentação: {file_info['name']}\n\n"
        context += f"**Tipo:** {file_type}\n"
        context += f"**Linhas:** {file_info['lines']}\n\n"
        context += "## Conteúdo do Arquivo\n\n"
        
        lang = self._get_language_for_highlighting(file_info['extension'])
        context += f"```{lang}\n{file_info['content']}\n```\n\n"
        context += "Documente ESTE ARQUIVO ESPECÍFICO usando as tools disponíveis."
        
        return context
    
    def build_small_project_context(
        self,
        files_data: Dict[str, List[Dict]],
        project_name: str
    ) -> str:
        """Constrói contexto para projeto pequeno"""
        context = f"# Análise: {project_name}\n\n"
        context += "Projeto pequeno com poucos arquivos. Documente de forma concisa.\n\n"
        context += self._build_overview(files_data)
        context += "\n\n"
        context += self._build_file_sections(files_data, 3000)
        
        return context

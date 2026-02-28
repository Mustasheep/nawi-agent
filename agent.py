#!/usr/bin/env python3
"""
Nawi, O agente Documentador Inteligente - Arquitetura Tool-Based
Sistema modular e extensível para geração de documentação automatizada
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path

from core.claude_client import ClaudeClient
from core.file_scanner import FileScanner
from core.context_builder import ContextBuilder
from tools.base_tool import Tool
from tools.code_analyzer import CodeAnalyzerTool
from tools.architecture import ArchitectureDetectorTool
from tools.dependency_mapper import DependencyMapperTool
from tools.quality_checker import QualityCheckerTool
from utils.logger import Logger
from templates.doc_templates import DocumentationTemplateManager


class DocumentationAgent:
    """
    Agente principal que orquestra o processo de documentação usando tools
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        verbose: bool = True,
        fast_mode: bool = False,
    ):
        """
        Inicializa o agente com suas ferramentas
        
        Args:
            api_key: Chave da API Anthropic (ou usa ANTHROPIC_API_KEY)
            verbose: Se True, mostra logs detalhados
        """
        self.logger = Logger(verbose=verbose)
        self.client = ClaudeClient(api_key)
        self.scanner = FileScanner()
        self.context_builder = ContextBuilder()
        self.template_manager = DocumentationTemplateManager()

        # Configuração de modo rápido (menos contexto/iterações/token)
        self.fast_mode = fast_mode
        self.max_iterations = 4 if fast_mode else 10
        self.max_tokens = 4000 if fast_mode else 8000
        self.max_content_per_file = 1000 if fast_mode else 2000
        
        # Registro de tools disponíveis
        self.tools: List[Tool] = []
        self._register_tools()
        
        self.logger.info("Agente Nawi inicializado")
        self.logger.info(f"Tools disponíveis: {len(self.tools)}")
    
    def _register_tools(self):
        """Registra todas as tools disponíveis"""
        self.tools = [
            CodeAnalyzerTool(),
            ArchitectureDetectorTool(),
            DependencyMapperTool(),
            QualityCheckerTool(),
        ]
        
        for tool in self.tools:
            self.logger.debug(f"Tool registrada: {tool.name}")
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Retorna definições das tools para a API do Claude"""
        return [tool.to_anthropic_format() for tool in self.tools]
    
    async def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """
        Executa uma tool específica
        
        Args:
            tool_name: Nome da tool a executar
            tool_input: Parâmetros de entrada da tool
            
        Returns:
            Resultado da execução da tool
        """
        tool = next((t for t in self.tools if t.name == tool_name), None)
        
        if not tool:
            raise ValueError(f"Tool '{tool_name}' não encontrada")
        
        self.logger.info(f"Executando tool: {tool_name}")
        result = await tool.execute(tool_input)
        self.logger.debug(f"Resultado: {result}")
        
        return result
    
    async def scan_paths(self, paths: List[str]) -> Dict[str, Any]:
        """
        Escaneia os caminhos fornecidos
        
        Args:
            paths: Lista de caminhos (diretórios ou arquivos)
            
        Returns:
            Dados dos arquivos encontrados
        """
        self.logger.section("ESCANEAMENTO DE ARQUIVOS")
        
        for path in paths:
            if os.path.isfile(path):
                self.logger.info(f"Adicionando arquivo: {path}")
                self.scanner.add_file(path)
            elif os.path.isdir(path):
                self.logger.info(f"Escaneando diretório: {path}")
                self.scanner.scan_directory(path)
            else:
                self.logger.warning(f"Path não encontrado: {path}")
        
        files_data = self.scanner.get_files_data()
        total = sum(len(files) for files in files_data.values())
        
        self.logger.info(f"Total de arquivos encontrados: {total}")
        for file_type, files in files_data.items():
            if files:
                self.logger.info(f"  {file_type}: {len(files)} arquivos")
        
        return files_data
    
    def detect_documentation_type(self, files_data: Dict[str, Any]) -> str:
        """
        Detecta o tipo de documentação necessária
        
        Args:
            files_data: Dados dos arquivos escaneados
            
        Returns:
            Tipo de documentação: 'single_file', 'small_project', 'full_project'
        """
        total_files = sum(len(files) for files in files_data.values())
        
        if total_files == 1:
            return 'single_file'
        elif total_files <= 5:
            return 'small_project'
        else:
            return 'full_project'
    
    async def generate_documentation(
        self,
        paths: List[str],
        project_name: str = "Projeto",
        doc_type: Optional[str] = None,
        template: Optional[str] = None
    ) -> str:
        """
        Gera documentação completa usando tools e Claude
        
        Args:
            paths: Caminhos para analisar
            project_name: Nome do projeto
            doc_type: Tipo específico de documentação (ou auto-detecta)
            template: Template específico a usar
            
        Returns:
            Documentação gerada em markdown
        """
        self.logger.section("GERAÇÃO DE DOCUMENTAÇÃO")
        
        # 1. Escaneia arquivos
        files_data = await self.scan_paths(paths)
        
        if not any(files_data.values()):
            self.logger.error("Nenhum arquivo encontrado para documentar")
            return self._generate_empty_doc(project_name)
        
        # 2. Detecta tipo de documentação
        if not doc_type:
            doc_type = self.detect_documentation_type(files_data)
        
        self.logger.info(f"Tipo de documentação: {doc_type}")
        
        # 3. Constrói contexto
        context = self.context_builder.build_context(
            files_data,
            project_name,
            max_content_per_file=self.max_content_per_file,
        )
        
        # 4. Seleciona template
        if not template:
            template = self.template_manager.get_template_for_type(doc_type)
        else:
            template = self.template_manager.get_template(template)
        
        # 5. Prepara system prompt com tools
        system_prompt = template.get_system_prompt()
        
        # 6. Chama Claude com tool use
        self.logger.info("Iniciando interação com Claude...")
        
        messages = [{
            "role": "user",
            "content": context
        }]
        
        documentation = await self._run_agent_loop(
            messages=messages,
            system_prompt=system_prompt,
            max_iterations=self.max_iterations,
        )
        
        self.logger.success("Documentação gerada com sucesso!")
        
        return documentation
    
    async def _run_agent_loop(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str,
        max_iterations: int = 10
    ) -> str:
        """
        Loop principal do agente com suporte a tool use
        
        Args:
            messages: Histórico de mensagens
            system_prompt: Prompt do sistema
            max_iterations: Máximo de iterações permitidas
            
        Returns:
            Resposta final do agente
        """
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            self.logger.debug(f"Iteração {iteration}/{max_iterations}")
            
            # Chama Claude
            response = await self.client.call_api(
                messages=messages,
                system_prompt=system_prompt,
                tools=self.get_tool_definitions(),
                max_tokens=self.max_tokens,
            )
            
            # Adiciona resposta ao histórico
            assistant_message = {
                "role": "assistant",
                "content": response["content"]
            }
            messages.append(assistant_message)
            
            # Verifica se há tool uses
            tool_uses = [
                block for block in response["content"]
                if block.get("type") == "tool_use"
            ]
            
            if not tool_uses:
                # Sem tools, retorna o texto final
                text_blocks = [
                    block["text"] for block in response["content"]
                    if block.get("type") == "text"
                ]
                return "\n".join(text_blocks)
            
            # Executa tools e coleta resultados
            tool_results = []
            
            for tool_use in tool_uses:
                tool_name = tool_use["name"]
                tool_input = tool_use["input"]
                tool_use_id = tool_use["id"]
                
                self.logger.info(f"Executando tool: {tool_name}")
                
                try:
                    result = await self.execute_tool(tool_name, tool_input)
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": json.dumps(result, ensure_ascii=False)
                    })
                    
                except Exception as e:
                    self.logger.error(f"Erro ao executar {tool_name}: {e}")
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "is_error": True,
                        "content": str(e)
                    })
            
            # Adiciona resultados das tools ao histórico
            messages.append({
                "role": "user",
                "content": tool_results
            })
        
        self.logger.warning("Máximo de iterações atingido")
        
        # Retorna última resposta de texto disponível
        for msg in reversed(messages):
            if msg["role"] == "assistant":
                text_blocks = [
                    block["text"] for block in msg["content"]
                    if isinstance(block, dict) and block.get("type") == "text"
                ]
                if text_blocks:
                    return "\n".join(text_blocks)
        
        return "Erro: Não foi possível gerar documentação"
    
    def _generate_empty_doc(self, project_name: str) -> str:
        """Gera documentação vazia quando nenhum arquivo é encontrado"""
        return f"""# {project_name}

*Nenhum arquivo encontrado para documentar*

## Informações

- Data: {self._get_timestamp()}
- Status: Sem arquivos detectados

## O que fazer?

Verifique se os caminhos fornecidos estão corretos e contêm arquivos relevantes.
"""
    
    def _get_timestamp(self) -> str:
        """Retorna timestamp formatado"""
        from datetime import datetime
        return datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    
    async def save_documentation(
        self,
        documentation: str,
        output_path: str
    ) -> bool:
        """
        Salva a documentação em arquivo
        
        Args:
            documentation: Conteúdo da documentação
            output_path: Caminho do arquivo de saída
            
        Returns:
            True se salvou com sucesso
        """
        try:
            # Cria diretório se necessário
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # Salva arquivo
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(documentation)
            
            self.logger.success(f"Documentação salva em: {output_path}")
            self.logger.info(f"Tamanho: {len(documentation)} caracteres")
            self.logger.info(f"Linhas: {len(documentation.splitlines())}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar documentação: {e}")
            return False

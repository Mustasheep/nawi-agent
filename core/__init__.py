"""
Módulos core do agente
"""

from .claude_client import ClaudeClient
from .file_scanner import FileScanner
from .context_builder import ContextBuilder

__all__ = ['ClaudeClient', 'FileScanner', 'ContextBuilder']

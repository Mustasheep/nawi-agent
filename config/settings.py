from dataclasses import dataclass, field
from typing import Dict, Set


@dataclass
class Settings:
    # --- Model ---
    MODEL: str = "claude-sonnet-4-20250514"
    API_URL: str = "https://api.anthropic.com/v1/messages"
    ANTHROPIC_VERSION: str = "2023-06-01"

    # --- Token limits por tipo de documentação ---
    MAX_TOKENS_SINGLE_FILE: int = 6000
    MAX_TOKENS_SMALL_PROJECT: int = 6000
    MAX_TOKENS_FULL_PROJECT: int = 8000

    # --- Limites de arquivos ---
    MAX_FILE_SIZE_BYTES: int = 100_000       # 100KB por arquivo
    MAX_FILES_PER_TYPE: int = 30
    MAX_FILES_IN_CONTEXT_SMALL: int = 5
    MAX_FILES_IN_CONTEXT_FULL: int = 8
    MAX_CONTENT_CHARS_PER_FILE: int = 2000   # truncamento de conteúdo no contexto

    # --- Thresholds de detecção ---
    SINGLE_FILE_THRESHOLD: int = 1
    SMALL_PROJECT_THRESHOLD: int = 5         # <= N arquivos → small_project

    # --- Diretórios ignorados no scan ---
    EXCLUDE_DIRS: Set[str] = field(default_factory=lambda: {
        '.git', '__pycache__', 'node_modules', '.terraform',
        'venv', '.venv', 'env', '.env', 'dist', 'build', 'data',
    })

    # --- Extensões por categoria ---
    EXTENSIONS: Dict[str, tuple] = field(default_factory=lambda: {
        'python':    ('.py',),
        'notebooks': ('.ipynb',),
        'terraform': ('.tf', '.tfvars'),
        'json':      ('.json',),
        'markdown':  ('.md',),
        'sql':       ('.sql',),
        'yaml':      ('.yml', '.yaml'),
    })

    # Arquivos markdown ignorados no scan automático
    MARKDOWN_IGNORE: Set[str] = field(default_factory=lambda: {'readme.md'})
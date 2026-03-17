import os
from typing import Dict, List, Any, Optional

from config import Settings
from utils import Logger

logger = Logger()

class FileScanner:
    """
    Responsável por todo o I/O de disco:
    - Escanear diretórios recursivamente
    - Adicionar arquivos individuais
    - Preparar contexto textual para a API
    - Detectar o tipo de documentação adequado
    """

    def __init__(self, settings: Settings = None, log: Logger = None):
        self._cfg = settings or Settings()
        self._log = log or logger
        self.files_data: Dict[str, List[Dict[str, Any]]] = {
            category: [] for category in self._cfg.EXTENSIONS
        }

    # ------------------------------------------------------------------
    # Ingestão de arquivos
    # ------------------------------------------------------------------

    def add_specific_file(self, file_path: str) -> bool:
        """
        Adiciona um arquivo específico para análise.

        Returns:
            True se o arquivo foi adicionado com sucesso, False caso contrário.
        """
        if not os.path.isfile(file_path):
            self._log.warning(f"Não é um arquivo válido: {file_path}")
            return False

        if os.path.getsize(file_path) > self._cfg.MAX_FILE_SIZE_BYTES:
            self._log.warning(f"Arquivo muito grande (>{self._cfg.MAX_FILE_SIZE_BYTES // 1000}KB): {file_path}")
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except (UnicodeDecodeError, PermissionError) as e:
            self._log.error(f"Não foi possível ler {file_path}: {e}")
            return False

        file_info = self._build_file_info(os.path.basename(file_path), file_path, content)
        category = self._categorize(os.path.basename(file_path))
        if category is None:
            self._log.warning(f"Tipo de arquivo não suportado (extensão ignorada): {os.path.basename(file_path)}")
            return False
        self.files_data[category].append(file_info)
        self._log.success(f"Arquivo adicionado: {os.path.basename(file_path)}")
        return True

    def scan_directory(self, directory: str) -> None:
        """Escaneia diretório recursivamente e coleta arquivos relevantes."""
        self._log.info(f"Escaneando: {directory}")
        cfg = self._cfg

        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in cfg.EXCLUDE_DIRS]

            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, directory)
                category = self._categorize(file)

                if category is None:
                    continue
                if len(self.files_data[category]) >= cfg.MAX_FILES_PER_TYPE:
                    continue
                if os.path.getsize(file_path) > cfg.MAX_FILE_SIZE_BYTES:
                    continue
                # Ignora README.md no scan automático
                if category == 'markdown' and file.lower() in cfg.MARKDOWN_IGNORE:
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.files_data[category].append(
                        self._build_file_info(file, relative_path, content)
                    )
                except (UnicodeDecodeError, PermissionError):
                    continue

        self._print_scan_summary()

    # ------------------------------------------------------------------
    # Detecção de tipo
    # ------------------------------------------------------------------

    def detect_documentation_type(self) -> str:
        """
        Detecta o tipo de documentação adequado com base na quantidade de arquivos.

        Returns:
            'single_file' | 'small_project' | 'full_project'
        """
        total = self.total_files
        if total <= self._cfg.SINGLE_FILE_THRESHOLD:
            return 'single_file'
        if total <= self._cfg.SMALL_PROJECT_THRESHOLD:
            return 'small_project'
        return 'full_project'

    # ------------------------------------------------------------------
    # Construção de contexto
    # ------------------------------------------------------------------

    def prepare_context(self, file_type: str, max_files: int = None) -> str:
        """
        Monta a string de contexto de uma categoria de arquivos para enviar à API.

        Args:
            file_type: chave de categoria (ex: 'python', 'terraform')
            max_files: limite de arquivos a incluir (usa config padrão se None)
        """
        if max_files is None:
            max_files = self._cfg.MAX_FILES_IN_CONTEXT_FULL

        files = self.files_data.get(file_type, [])[:max_files]
        if not files:
            return ""

        context = f"\n## Arquivos {file_type.upper()}\n\n"
        for file_info in files:
            context += f"### {file_info['path']}\n"
            context += f"```\n{file_info['content'][:self._cfg.MAX_CONTENT_CHARS_PER_FILE]}\n```\n\n"
        return context

    def get_single_file_info(self) -> Optional[Dict[str, Any]]:
        """Retorna metadados do único arquivo carregado, se aplicável."""
        for category, files in self.files_data.items():
            if files:
                return {'type': category, 'info': files[0]}
        return None

    # ------------------------------------------------------------------
    # Propriedades auxiliares
    # ------------------------------------------------------------------

    @property
    def total_files(self) -> int:
        return sum(len(files) for files in self.files_data.values())

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    def _build_file_info(self, name: str, path: str, content: str) -> Dict[str, Any]:
        return {
            'name': name,
            'path': path,
            'content': content,
            'size': len(content.encode('utf-8')),
            'lines': len(content.split('\n')),
        }

    def _categorize(self, filename: str) -> Optional[str]:
        """Retorna a categoria do arquivo com base na extensão, ou None se não reconhecido."""
        lower = filename.lower()
        for category, extensions in self._cfg.EXTENSIONS.items():
            if any(lower.endswith(ext) for ext in extensions):
                return category
        return None

    def _print_scan_summary(self) -> None:
        for category, files in self.files_data.items():
            if files:
                self._log.success(f"{category.capitalize()}: {len(files)}")
        self._log.info(f"Total: {self.total_files} arquivos\n")
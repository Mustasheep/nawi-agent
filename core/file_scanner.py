"""
Scanner de arquivos do projeto
"""

import os
from typing import Dict, List, Any
from pathlib import Path


class FileScanner:
    """
    Escaneia e organiza arquivos do projeto
    """
    
    def __init__(self, max_file_size: int = 100000, max_files_per_type: int = 20):
        """
        Inicializa o scanner
        
        Args:
            max_file_size: Tamanho máximo de arquivo em bytes (100KB default)
            max_files_per_type: Máximo de arquivos por tipo
        """
        self.max_file_size = max_file_size
        self.max_files_per_type = max_files_per_type
        
        self.files_data = {
            'python': [],
            'javascript': [],
            'typescript': [],
            'java': [],
            'go': [],
            'notebooks': [],
            'terraform': [],
            'json': [],
            'yaml': [],
            'sql': [],
            'markdown': [],
            'config': [],
            'other': []
        }
        
        self.exclude_dirs = {
            '.git', '__pycache__', 'node_modules', '.terraform',
            'venv', '.venv', 'env', '.env', 'dist', 'build', 'dbt_packages/'
            'data', 'logs', '.idea', '.vscode', 'target', 'logs'
        }
        
        self.file_type_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.ipynb': 'notebooks',
            '.tf': 'terraform',
            '.tfvars': 'terraform',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.sql': 'sql',
            '.md': 'markdown',
            '.toml': 'config',
            '.ini': 'config',
            '.cfg': 'config',
            '.conf': 'config'
        }
    
    def add_file(self, file_path: str) -> bool:
        """
        Adiciona arquivo específico
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            True se adicionou com sucesso
        """
        if not os.path.isfile(file_path):
            return False
        
        try:
            # Verifica tamanho
            if os.path.getsize(file_path) > self.max_file_size:
                print(f"  ⚠️  Arquivo muito grande: {file_path}")
                return False
            
            # Lê conteúdo
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Determina tipo
            file_extension = Path(file_path).suffix.lower()
            file_type = self.file_type_map.get(file_extension, 'other')
            
            # Cria info
            file_info = {
                'name': os.path.basename(file_path),
                'path': file_path,
                'relative_path': file_path,
                'content': content,
                'size': os.path.getsize(file_path),
                'lines': len(content.split('\n')),
                'extension': file_extension
            }
            
            # Adiciona na categoria apropriada
            if len(self.files_data[file_type]) < self.max_files_per_type:
                self.files_data[file_type].append(file_info)
                return True
            
            return False
            
        except (UnicodeDecodeError, PermissionError) as e:
            print(f"  ✘ Erro ao ler {file_path}: {e}")
            return False
    
    def scan_directory(self, directory: str):
        """
        Escaneia diretório recursivamente
        
        Args:
            directory: Caminho do diretório
        """
        for root, dirs, files in os.walk(directory):
            # Remove diretórios excluídos
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, directory)
                
                # Determina tipo
                file_extension = Path(file).suffix.lower()
                file_type = self.file_type_map.get(file_extension, 'other')
                
                # Verifica limites
                if len(self.files_data[file_type]) >= self.max_files_per_type:
                    continue
                
                try:
                    # Verifica tamanho
                    if os.path.getsize(file_path) > self.max_file_size:
                        continue
                    
                    # Lê conteúdo
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Cria info
                    file_info = {
                        'name': file,
                        'path': file_path,
                        'relative_path': relative_path,
                        'content': content,
                        'size': os.path.getsize(file_path),
                        'lines': len(content.split('\n')),
                        'extension': file_extension
                    }
                    
                    self.files_data[file_type].append(file_info)
                    
                except (UnicodeDecodeError, PermissionError):
                    continue
    
    def get_files_data(self) -> Dict[str, List[Dict]]:
        """Retorna dados dos arquivos escaneados"""
        return self.files_data
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do scan"""
        stats = {}
        total_files = 0
        total_lines = 0
        
        for file_type, files in self.files_data.items():
            if files:
                type_lines = sum(f['lines'] for f in files)
                stats[file_type] = {
                    'count': len(files),
                    'lines': type_lines
                }
                total_files += len(files)
                total_lines += type_lines
        
        stats['total'] = {
            'files': total_files,
            'lines': total_lines
        }
        
        return stats

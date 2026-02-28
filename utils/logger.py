"""
Sistema de logging do agente
"""

from datetime import datetime
from typing import Optional

class Logger:
    """Logger customizado para o agente"""

    # Cores ANSI
    COLORS = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m'
    }

    def __init__(self, verbose: bool = True):
        """
        Inicializa o logger

        Args:
            verbose: Se True, mostra logs detalhados
        """
        self.verbose = verbose

    def _format_message(self, level: str, message: str, color: str = 'white') -> str:
        """Formata a mensagem com timestamp, nível e cor"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        color_code = self.COLORS.get(color, self.COLORS['white'])
        reset = self.COLORS['reset']
        bold = self.COLORS['bold']

        return f"{bold}[{timestamp}]{reset} {color_code}[{level}]{reset} {message}"

    def info(self, message:str):
        """Log informativo"""
        print(self._format_message("INFO", message, "blue"))

    def success(self, message:str):
        """Log de sucesso"""
        print(self._format_message("SUCCESS", message, "green"))

    def warning(self, message:str):
        """Log de aviso"""
        print(self._format_message("WARNING", message, "yellow"))
    
    def error(self, message:str):
        """Log de erro"""
        print(self._format_message("ERROR", message, "red"))

    def debug(self, message:str):
        """Log de debug"""
        if not self.verbose:
            return
        print(self._format_message("DEBUG", message, "magenta"))

    def section(self, title:str):
        """Imprime seção destacada"""
        separator = "=" * 60
        print(f"\n{self.COLORS['cyan']}{self.COLORS['bold']}{separator}")
        print(f"  {title}")
        print(f"{separator}{self.COLORS['reset']}\n")

    
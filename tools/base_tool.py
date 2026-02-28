"""
Classe base abstrata para tools de agente
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List

class Tool(ABC):
    """
    Classe base para todas as tools do agente

    Cada tool deve implementar:
    - name: Nome único da tool
    - description: Descrição da tool
    - input_schema: Esquema de entrada da tool
    - execute(): Lógica de execução da tool
    """

    def __init__(self):
        """Inicializa a tool"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Nome único da tool"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Descrição da tool"""
        pass

    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """
        Schema JSON dos parâmetros de entrada

        Formato:
        {
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "Descrição do parâmetro 1"},
                "param2": {"type": "number", "description": "Descrição do parâmetro 2"}
            },
            "required": ["param1", "param2"]
        }
        """
        pass

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Any:
        """
        Executa a lógica da tool

        Args:
            input_data: Parâmetros de entrada conforme input_schema

        Returns:
            Resultado da execução (será serializado para JSON)
        """
        pass

    def to_anthropic_format(self) -> Dict[str, Any]:
        """
        Converte a tool para o formato da API Anthropic

        Returns:
            Definição da tool no formato espero pela API
        """

        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema
        }
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Valida se os parâmetros de entrada estão corretos

        Args:
            input_data: Dados a validar

        Returns:
            True se válido, False caso contrário
        """
        required = self.input_schema.get("required", [])

        for param in required:
            if param not in input_data:
                return False

        return True
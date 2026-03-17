import aiohttp
from typing import List, Dict

from config import Settings


class ClaudeClient:
    """
    Responsável exclusivamente pelo transporte HTTP com a API da Anthropic.
    Não conhece prompts, contexto ou lógica de documentação.
    """

    def __init__(self, api_key: str, settings: Settings = None):
        if not api_key:
            raise ValueError(
                "API Key não encontrada. Defina ANTHROPIC_API_KEY como variável de ambiente "
                "ou passe como parâmetro."
            )
        self._api_key = api_key
        self._cfg = settings or Settings()
        self._headers = {
            "x-api-key": self._api_key,
            "anthropic-version": self._cfg.ANTHROPIC_VERSION,
            "content-type": "application/json",
        }

    async def call(
        self,
        messages: List[Dict],
        system_prompt: str = None,
        max_tokens: int = None,
    ) -> str:
        """
        Envia uma requisição para a API e retorna o texto da resposta.

        Args:
            messages:      lista de dicts no formato {"role": ..., "content": ...}
            system_prompt: prompt de sistema opcional
            max_tokens:    limite de tokens na resposta (usa MAX_TOKENS_FULL_PROJECT como padrão)

        Raises:
            Exception: se a API retornar status != 200
        """
        if max_tokens is None:
            max_tokens = self._cfg.MAX_TOKENS_FULL_PROJECT

        payload: Dict = {
            "model": self._cfg.MODEL,
            "max_tokens": max_tokens,
            "messages": messages,
        }
        if system_prompt:
            payload["system"] = system_prompt

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self._cfg.API_URL,
                headers=self._headers,
                json=payload,
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API Error {response.status}: {error_text}")

                result = await response.json()
                return result["content"][0]["text"]
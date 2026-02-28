"""
Cliente para interação com a API do Claude
"""

import os
import json
from typing import List, Dict, Any, Optional
import aiohttp


class ClaudeClient:
    """Cliente para API da Anthropic com suporte a tool use"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa o cliente
        
        Args:
            api_key: Chave da API (ou usa ANTHROPIC_API_KEY do ambiente)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "API Key não encontrada. Defina ANTHROPIC_API_KEY ou "
                "passe como parâmetro."
            )
        
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-sonnet-4-20250514"
        self.api_version = "2023-06-01"
    
    async def call_api(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 8000,
        temperature: float = 1.0
    ) -> Dict[str, Any]:
        """
        Faz chamada à API do Claude
        
        Args:
            messages: Histórico de mensagens
            system_prompt: Prompt do sistema
            tools: Definições de tools disponíveis
            max_tokens: Máximo de tokens na resposta
            temperature: Temperatura (0-1)
            
        Returns:
            Resposta completa da API
        """
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": self.api_version,
            "content-type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        if tools:
            payload["tools"] = tools
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url,
                headers=headers,
                json=payload
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(
                        f"API Error {response.status}: {error_text}"
                    )
                
                result = await response.json()
                return result
    
    async def stream_api(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 8000
    ):
        """
        Faz chamada com streaming à API do Claude
        
        Args:
            messages: Histórico de mensagens
            system_prompt: Prompt do sistema
            tools: Definições de tools disponíveis
            max_tokens: Máximo de tokens na resposta
            
        Yields:
            Chunks da resposta conforme chegam
        """
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": self.api_version,
            "content-type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": messages,
            "stream": True
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        if tools:
            payload["tools"] = tools
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url,
                headers=headers,
                json=payload
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(
                        f"API Error {response.status}: {error_text}"
                    )
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    
                    if line.startswith('data: '):
                        data = line[6:]  # Remove 'data: '
                        
                        if data == '[DONE]':
                            break
                        
                        try:
                            chunk = json.loads(data)
                            yield chunk
                        except json.JSONDecodeError:
                            continue

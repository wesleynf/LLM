"""
provider_factory.py — Sistema de Failover para Provedores de LLM.
"""
import os
import logging
from typing import List, Dict, Any
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

class LLMProvider:
    def __init__(self, name: str, api_key: str, base_url: str, model: str):
        self.name = name
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    async def generate(self, messages: List[Dict]) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Erro no provedor {self.name}: {e}")
            raise

class ProviderFactory:
    """
    Gerencia a cadeia de provedores com failover automático.
    """
    
    @staticmethod
    def get_provider():
        # Configuração de Failover: Gemini -> Groq -> DeepSeek
        providers = [
            # 1. Gemini (OpenAI Compatible via local proxy ou direto)
            {
                "name": "Gemini",
                "api_key": os.getenv("GEMINI_API_KEY"),
                "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
                "model": "gemini-1.5-flash"
            },
            # 2. Groq (Llama-3)
            {
                "name": "Groq",
                "api_key": os.getenv("GROQ_API_KEY"),
                "base_url": "https://api.groq.com/openai/v1",
                "model": "llama3-70b-8192"
            }
        ]

        return FailoverChain(providers)

class FailoverChain:
    def __init__(self, provider_configs: List[Dict]):
        self.providers = [
            LLMProvider(**cfg) for cfg in provider_configs if cfg['api_key']
        ]

    async def generate(self, messages: List[Dict]) -> str:
        last_error = None
        for provider in self.providers:
            try:
                return await provider.generate(messages)
            except Exception as e:
                logger.warning(f"Failover: {provider.name} falhou, tentando próximo...")
                last_error = e
        
        raise last_error or Exception("Nenhum provedor de LLM disponível.")

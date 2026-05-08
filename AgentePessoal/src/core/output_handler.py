"""
output_handler.py — Gerencia o formato de saída para o usuário.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class OutputHandler:
    """
    Processa a resposta final do agente para garantir que o formato
    seja compatível com as capacidades do Telegram.
    """

    @staticmethod
    def format_for_telegram(text: str) -> str:
        """
        Limpa e formata o texto para Markdown do Telegram.
        """
        # Remover tags de pensamento (ex: <thought>...</thought>)
        clean_text = re.sub(r'<thought>.*?</thought>', '', text, flags=re.DOTALL)
        
        # Escapar caracteres especiais se necessário ou converter estilos
        # O Telegram usa MarkdownV2 ou Markdown (legado)
        return clean_text.strip()

"""
base_tool.py — Contrato base para ferramentas.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseTool(ABC):
    @property
    @abstractmethod
    def definition(self) -> Dict:
        """Retorna a definição da ferramenta no formato OpenAI."""
        pass

    @abstractmethod
    async def execute(self, args: Dict, metadata: Optional[Dict] = None) -> Any:
        """Executa a lógica da ferramenta."""
        pass

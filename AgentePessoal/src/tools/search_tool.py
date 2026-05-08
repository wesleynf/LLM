"""
search_tool.py — Ferramenta de busca web usando DuckDuckGo.
"""
import logging
from typing import Any, Dict, Optional
from duckduckgo_search import DDGS
from src.tools.base_tool import BaseTool

logger = logging.getLogger(__name__)

class SearchWebTool(BaseTool):
    @property
    def definition(self) -> Dict:
        return {
            "name": "search_web",
            "description": "Busca informações em tempo real na internet (preços, notícias, etc).",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Termo de busca"}
                },
                "required": ["query"]
            }
        }

    async def execute(self, args: Dict, metadata: Optional[Dict] = None) -> Any:
        query = args.get("query")
        logger.info(f"Buscando na web por: {query}")
        
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))
                return {"results": results}
        except Exception as e:
            logger.error(f"Erro na busca web: {e}")
            return {"error": str(e)}

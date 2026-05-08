"""
tool_registry.py — Registro centralizado de ferramentas.
"""
import logging
from typing import Dict, List, Any
from src.tools.base_tool import BaseTool

logger = logging.getLogger(__name__)

class ToolRegistry:
    _tools: Dict[str, BaseTool] = {}

    @classmethod
    def register(cls, tool: BaseTool):
        name = tool.definition["name"]
        cls._tools[name] = tool
        logger.info(f"Ferramenta registrada: {name}")

    @classmethod
    def get_tool(cls, name: str) -> Optional[BaseTool]:
        return cls._tools.get(name)

    @classmethod
    def initialize(cls):
        # Evitar import circular
        from src.tools.search_tool import SearchWebTool
        from src.tools.skill_list_tool import SkillListTool
        
        cls.register(SearchWebTool())
        cls.register(SkillListTool())
        
        logger.info("Registro de ferramentas inicializado.")

    @classmethod
    def get_all_definitions(cls) -> List[Dict]:
        return [t.definition for t in cls._tools.values()]

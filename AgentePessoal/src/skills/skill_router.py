"""
skill_router.py — Roteador de Intenção para Seleção de Skill.
"""
import logging
import json
import re
from typing import List, Optional
from src.providers.provider_factory import ProviderFactory

logger = logging.getLogger(__name__)

class SkillRouter:
    """
    Usa o LLM para decidir qual skill é a mais adequada para o input do usuário.
    """

    async def route(self, text: str, available_skills: List[Any]) -> Optional[str]:
        if not available_skills:
            return None

        # Construir descrição das skills para o LLM
        skills_desc = "\n".join([
            f"- {s.metadata.name}: {s.metadata.description}" 
            for s in available_skills
        ])

        prompt = f"""
Identifique a skill mais adequada para o pedido do usuário abaixo.
Responda APENAS com um JSON contendo a chave "skill". Se nenhuma for adequada, use null.

Skills Disponíveis:
{skills_desc}

Usuário: "{text}"

JSON:"""

        try:
            provider = ProviderFactory.get_provider()
            response = await provider.generate([{"role": "user", "content": prompt}])
            
            # Extrair JSON da resposta
            json_match = re.search(r'\{.*\}', response)
            if json_match:
                data = json.loads(json_match.group(0))
                return data.get("skill")
        except Exception as e:
            logger.error(f"Erro no roteamento: {e}")
        
        return None

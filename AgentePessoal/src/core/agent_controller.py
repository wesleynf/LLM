"""
agent_controller.py — Equivalente a AgentController.ts

Este é o controlador principal que gerencia o fluxo de uma mensagem.
Ele é stateless por design, carregando as instruções das skills a cada requisição.
"""
import logging
from typing import Optional, Dict, Any

from src.skills.skill_loader import SkillLoader
from src.skills.skill_router import SkillRouter
from src.core.agent_loop import AgentLoop
from src.providers.provider_factory import ProviderFactory

logger = logging.getLogger(__name__)

class AgentController:
    """
    Controlador central que orquestra o processamento de inputs.
    """

    def __init__(self):
        self.skill_loader = SkillLoader()
        self.skill_router = SkillRouter()

    async def process_input(self, text: str, user_id: int, metadata: Optional[Dict] = None) -> str:
        """
        Processa uma entrada do usuário e retorna a resposta do agente.
        1. Identifica a skill adequada via SkillRouter.
        2. Carrega as instruções da skill via SkillLoader.
        3. Executa o ciclo ReAct via AgentLoop.
        """
        metadata = metadata or {}
        metadata['user_id'] = user_id

        # 1. Obter skills ativas
        available_skills = self.skill_loader.load_active_skills()
        
        # 2. Roteamento de intenção (Identificar qual skill usar)
        selected_skill_name = await self.skill_router.route(text, available_skills)
        
        # 3. Carregar instrução da skill selecionada (ou usar fallback genérico)
        skill_instruction = ""
        if selected_skill_name:
            skill = next((s for s in available_skills if s.metadata.name == selected_skill_name), None)
            if skill:
                skill_instruction = skill.content
                logger.info(f"[AgentController] Usando skill: {selected_skill_name}")
        
        if not skill_instruction:
            logger.info("[AgentController] Nenhuma skill específica. Usando modo assistente genérico.")
            skill_instruction = "Você é um assistente pessoal útil e educado. Ajude o usuário com o que ele precisar."

        # 4. Executar Loop ReAct (O coração da inteligência)
        # O AgentLoop gerencia o pensamento e o uso de ferramentas
        agent_loop = AgentLoop(
            system_instruction=skill_instruction,
            provider=ProviderFactory.get_provider() # Failover provider chain
        )

        try:
            response = await agent_loop.run(text, metadata)
            return response
        except Exception as e:
            logger.error(f"[AgentController] Erro no AgentLoop: {e}")
            return "Sinto muito, tive um problema ao processar sua solicitação. Pode repetir?"

"""
agent_loop.py — Equivalente a AgentLoop.ts

Implementa o motor ReAct (Reasoning and Acting).
Interpreta o pensamento do modelo, executa ferramentas e injeta observações.
"""
import logging
import json
import re
from typing import Dict, List, Any

from src.tools.tool_registry import ToolRegistry

logger = logging.getLogger(__name__)

class AgentLoop:
    """
    Motor ReAct que executa o ciclo Pensamento -> Ação -> Observação.
    """

    def __init__(self, system_instruction: str, provider: Any):
        self.system_instruction = system_instruction
        self.provider = provider
        self.max_iterations = 5
        self.history: List[Dict] = []

    async def run(self, user_input: str, metadata: Dict) -> str:
        """
        Executa o loop de raciocínio.
        """
        # Preparar contexto inicial
        current_prompt = user_input
        self.history = [
            {"role": "system", "content": self.system_instruction},
            {"role": "user", "content": user_input}
        ]

        for i in range(self.max_iterations):
            logger.info(f"[AgentLoop] Iteração {i+1}/{self.max_iterations}")
            
            # 1. Chamar LLM
            response_text = await self.provider.generate(self.history)
            
            # Adicionar pensamento ao histórico
            self.history.append({"role": "assistant", "content": response_text})

            # 2. Verificar se há chamada de ferramenta (Tool Call)
            # Suporta tanto o formato nativo da API quanto o formato ReAct via texto
            tool_call = self._parse_tool_call(response_text)
            
            if not tool_call:
                # Se não houver ferramenta para chamar, a resposta é final
                return response_text

            # 3. Executar Ferramenta
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("args", {})
            
            logger.info(f"[AgentLoop] Executando ferramenta: {tool_name}")
            
            tool = ToolRegistry.get_tool(tool_name)
            if tool:
                try:
                    observation = await tool.execute(tool_args, metadata)
                    observation_str = json.dumps(observation, ensure_ascii=False)
                except Exception as e:
                    observation_str = f"Erro ao executar {tool_name}: {str(e)}"
            else:
                observation_str = f"Ferramenta '{tool_name}' não encontrada."

            # 4. Injetar Observação no histórico
            logger.info(f"[AgentLoop] Observação recebida para {tool_name}")
            self.history.append({
                "role": "user", 
                "content": f"OBSERVAÇÃO: {observation_str}"
            })

        return "Desculpe, excedi o limite de processamento para esta tarefa."

    def _parse_tool_call(self, text: str) -> Optional[Dict]:
        """
        Extrai chamadas de ferramentas de blocos de texto ou formato ReAct.
        Exemplo esperado: Action: tool_name(args) ou Action: {"tool": "name", "args": {}}
        """
        # Padrão ReAct comum: Action: {"tool": "search_web", "query": "..."}
        action_match = re.search(r'Action:\s*(\{.*\})', text, re.DOTALL)
        if action_match:
            try:
                data = json.loads(action_match.group(1))
                return {
                    "name": data.get("tool") or data.get("action"),
                    "args": data.get("args") or {k:v for k,v in data.items() if k not in ["tool", "action"]}
                }
            except:
                pass
        
        # Padrão simplificado: Action: tool_name(arg=val)
        simple_match = re.search(r'Action:\s*(\w+)\((.*)\)', text)
        if simple_match:
            return {
                "name": simple_match.group(1),
                "args": {"query": simple_match.group(2)} # Fallback simplista
            }

        return None

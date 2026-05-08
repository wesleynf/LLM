import asyncio
from src.core.agent_controller import AgentController

async def test():
    controller = AgentController()
    response = await controller.process_input(
        user_id="test-user-2",
        input_text="Chevrolet Onix Premier 2024 com 30.000 km rodados valor fipe",
        metadata={"input_type": "text"}
    )
    print("\n" + "="*50)
    print("RESPOSTA DO AGENTE:")
    print("="*50)
    print(response.get("text"))

if __name__ == "__main__":
    asyncio.run(test())

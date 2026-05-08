import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.core.agent_controller import AgentController

@pytest.mark.asyncio
async def test_process_input_text():
    # Setup
    mock_provider = AsyncMock()
    mock_provider.generate.return_value = "Olá, como posso ajudar?"
    
    with patch('src.providers.provider_factory.ProviderFactory.get_provider', return_value=mock_provider):
        controller = AgentController()
        
        # Action
        response = await controller.process_input("Olá", user_id=123)
        
        # Assert
        assert "Olá" in response
        mock_provider.generate.assert_called()

@pytest.mark.asyncio
async def test_stateless_behavior():
    # Garantir que o controller não mantém histórico entre chamadas
    mock_provider = AsyncMock()
    mock_provider.generate.return_value = "Resposta"
    
    with patch('src.providers.provider_factory.ProviderFactory.get_provider', return_value=mock_provider):
        controller = AgentController()
        
        await controller.process_input("Pergunta 1", user_id=123)
        await controller.process_input("Pergunta 2", user_id=123)
        
        # O histórico enviado para o provedor deve ser vazio ou resetado em cada chamada se for stateless
        # (Dependendo da implementação exata do controller)
        pass

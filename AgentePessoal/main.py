import asyncio
import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler

from src.core.agent_controller import AgentController
from src.tools.tool_registry import ToolRegistry

# Configuração de Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar componentes
ToolRegistry.initialize()
controller = AgentController()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler principal para todas as mensagens de texto e mídia.
    """
    if not update.effective_chat:
        return

    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # Extrair texto ou legenda de mídia
    text = update.message.text or update.message.caption or ""
    
    # Tratar áudio (Voice/Audio)
    if update.message.voice or update.message.audio:
        # Futura implementação: Transcrição via Faster-Whisper
        text = "[ÁUDIO RECEBIDO - ANALISANDO...]"
        
    # Tratar Documentos (PDF)
    if update.message.document:
        text = f"[DOCUMENTO RECEBIDO: {update.message.document.file_name}] " + text

    logger.info(f"Mensagem recebida de {user_id} em {chat_id}: {text[:50]}...")
    
    # Processar entrada via AgentController
    # O controller gerencia o roteamento de skills e o loop ReAct
    try:
        response = await controller.process_input(text, user_id=user_id, metadata={"chat_id": chat_id})
        
        # Enviar resposta (Markdown por padrão)
        await context.bot.send_message(
            chat_id=chat_id,
            text=response,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ Ops! Ocorreu um erro interno. Tente novamente em instantes."
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para o comando /start"""
    await update.message.reply_text(
        "👋 Olá! Eu sou seu assistente pessoal inteligente.\n\n"
        "Posso te ajudar com:\n"
        "🚗 Avaliação de veículos\n"
        "📰 Resumo de notícias\n"
        "🧠 Apoio psicológico\n"
        "📅 Gestão de agenda\n\n"
        "Como posso te ajudar hoje?"
    )

if __name__ == '__main__':
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN não encontrado no arquivo .env")
        exit(1)

    app = ApplicationBuilder().token(token).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.VOICE | filters.AUDIO | filters.Document.ALL, handle_message))
    
    logger.info("Bot iniciado e aguardando mensagens...")
    app.run_polling()

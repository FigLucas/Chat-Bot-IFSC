"""
Dependências compartilhadas da aplicação.
Fornece instância global do ChatService, inicialização assíncrona e status do serviço.
"""

# -----------------------------
# Importações necessárias
# -----------------------------
from .services.chat_service import ChatService
import logging
import asyncio

# -----------------------------
# Logger do módulo
# -----------------------------
logger = logging.getLogger(__name__)

# -----------------------------
# Variáveis globais para o ChatService
# -----------------------------
_chat_service: ChatService = None  # Instância global do ChatService
_initialization_lock = asyncio.Lock()  # Lock para evitar inicialização simultânea

# -----------------------------
# Função para inicializar o ChatService globalmente
# -----------------------------
async def initialize_chat_service():
    """
    Inicializa o serviço de chat globalmente.
    
    - Garante que apenas uma inicialização aconteça por vez usando lock assíncrono.
    - Cria instância de ChatService e chama método initialize().
    """
    global _chat_service
    
    async with _initialization_lock:
        # Se já inicializado, apenas retorna
        if _chat_service and _chat_service.is_initialized:
            logger.info("✅ ChatService já inicializado")
            return
        
        logger.info("🚀 Inicializando sistema IFSC Chat...")
        _chat_service = ChatService()      # Cria instância
        await _chat_service.initialize()   # Inicializa assíncronamente
        logger.info("✅ Sistema inicializado com sucesso!")

# -----------------------------
# Função para obter a instância do ChatService
# -----------------------------
async def get_chat_service() -> ChatService:
    """
    Dependência para obter o ChatService inicializado.
    
    - Se o serviço ainda não estiver inicializado, inicializa automaticamente.
    - Retorna a instância global do ChatService.
    """
    global _chat_service
    
    if _chat_service is None:
        logger.info("🔄 Inicializando ChatService...")
        await initialize_chat_service()
    
    return _chat_service

# -----------------------------
# Função para obter o status do ChatService
# -----------------------------
def get_chat_service_status() -> dict:
    """
    Retorna o status do serviço de chat.
    
    Keys:
        - initialized: True se ChatService foi inicializado
        - service_available: True se a instância do ChatService existe
    """
    global _chat_service
    return {
        "initialized": _chat_service.is_initialized if _chat_service else False,
        "service_available": _chat_service is not None
    }

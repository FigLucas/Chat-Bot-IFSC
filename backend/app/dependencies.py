"""
Dependências compartilhadas da aplicação
"""
from fastapi import HTTPException
from .services.chat_service import ChatService
import logging
import asyncio

logger = logging.getLogger(__name__)

# Instância global do serviço de chat
_chat_service: ChatService = None
_initialization_lock = asyncio.Lock()

async def initialize_chat_service():
    """Inicializa o serviço de chat globalmente"""
    global _chat_service
    
    async with _initialization_lock:
        if _chat_service and _chat_service.is_initialized:
            logger.info("✅ ChatService já inicializado")
            return
            
        try:
            logger.info("🚀 Inicializando sistema IFSC Chat...")
            _chat_service = ChatService()
            await _chat_service.initialize()
            logger.info("✅ Sistema inicializado com sucesso!")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar sistema: {e}")
            # Criar instância mesmo com erro para funcionar em modo limitado
            if not _chat_service:
                _chat_service = ChatService()
                # Forçar inicialização em modo mock
                _chat_service.is_initialized = True
                _chat_service.qa_chain = _chat_service._create_mock_system()
                logger.warning("⚠️ Sistema inicializado em modo MOCK devido a erro")

async def get_chat_service() -> ChatService:
    """Dependência para obter o serviço de chat inicializado"""
    global _chat_service
    
    if _chat_service is None:
        logger.info("🔄 Inicializando ChatService...")
        _chat_service = ChatService()
        await _chat_service.initialize()
        logger.info("✅ ChatService inicializado com sucesso!")
    
    return _chat_service

def get_chat_service_status() -> dict:
    """Obtém o status do serviço de chat"""
    global _chat_service
    return {
        "initialized": _chat_service.is_initialized if _chat_service else False,
        "service_available": _chat_service is not None
    }
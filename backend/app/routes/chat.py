import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status

from ..auth.auth import get_current_user
from ..schemas.chat import ChatRequest, ChatResponse
from ..services.chat_system import process_message

router = APIRouter()
logger = logging.getLogger(__name__)

_process_message_fn = None

def get_process_message():
    global _process_message_fn
    if _process_message_fn:
        return _process_message_fn
    try:
        from ..services.chat_system import process_message
        if not callable(process_message):
            raise TypeError("process_message não é chamável")
        _process_message_fn = process_message
        logger.info("✅ process_message carregado de chat_system.py")
    except Exception as e:
        logger.error(f"❌ Falha ao importar process_message: {e}")
        raise ImportError("Não foi possível importar process_message do chat_system.py")
    return _process_message_fn

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    if not current_user or not current_user.get("username"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autenticado"
        )
    logger.info(f"🔎 Payload unificado -> message='{request.message}' (raw content='{request.content}')")
    try:
        logger.info(f"💬 Pergunta recebida de {current_user.get('username', 'usuário desconhecido')}: '{request.message[:80]}...'")
        process_message_fn = get_process_message()
        response_text = process_message_fn(
            message=request.message,
            conversation_id=request.conversation_id,
            user=current_user.get("username")
        )
        if not response_text:
            response_text = "Não foi possível gerar uma resposta no momento."
        logger.info(f"✅ Resposta gerada: '{response_text[:80]}...'")
        return ChatResponse(
            response=response_text,
            content=response_text,
            conversation_id=request.conversation_id or "default-conversation",
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.exception("Erro ao processar mensagem")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar resposta: {e}")
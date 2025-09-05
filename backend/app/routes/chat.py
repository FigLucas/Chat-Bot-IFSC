# -----------------------------
# Endpoint de chat comentado
# -----------------------------
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, status
import uuid

from ..auth.auth import get_current_user          # Obtém usuário autenticado via token JWT
from ..schemas.chat import ChatRequest, ChatResponse  # Schemas de request e response
from ..services.chat_system import process_message   # Função que processa mensagem do usuário

router = APIRouter()                              # Roteador para endpoints de chat
logger = logging.getLogger(__name__)              # Logger do módulo

_process_message_fn = None                        # Armazena função process_message carregada

def get_process_message():
    """
    Carrega a função process_message de forma dinâmica e guarda globalmente.
    Retorna a função para uso no endpoint.
    """
    global _process_message_fn
    if _process_message_fn:                        # Se já carregada, retorna
        return _process_message_fn
    try:
        from ..services.chat_system import process_message
        if not callable(process_message):         # Verifica se é chamável
            raise TypeError("process_message não é chamável")
        _process_message_fn = process_message
        logger.info("✅ process_message carregado de chat_system.py")
    except Exception as e:
        logger.error(f"❌ Falha ao importar process_message: {e}")
        raise ImportError("Não foi possível importar process_message do chat_system.py")
    return _process_message_fn

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,                          # Dados da mensagem do usuário
    request_raw: Request,                          # Para acessar JSON cru enviado
    current_user: dict = Depends(get_current_user) # Usuário autenticado
):
    """
    Recebe mensagem do usuário, processa com process_message e retorna resposta.
    """

    # Log do JSON cru recebido (debug)
    try:
        raw = await request_raw.json()
        logger.info(f"RAW BODY: {raw}")
    except Exception:
        logger.info("RAW BODY: <não conseguiu ler json bruto>")

    # Verifica autenticação
    if not current_user or not current_user.get("username"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autenticado"
        )

    logger.info(f"🔎 Payload unificado -> message='{request.message}' (raw content='{request.content}')")

    try:
        logger.info(f"💬 Pergunta recebida de {current_user.get('username', 'usuário desconhecido')}: '{request.message[:80]}...'")

        # Gera session_id se não fornecido
        session_id = request.conversation_id or str(uuid.uuid4())
        logger.info(f"📚 Histórico recebido ({len(request.history or [])}): {request.history}")

        # Obtém função de processamento
        process_message_fn = get_process_message()

        # Chama process_message com mensagem, usuário e histórico
        response_obj = process_message_fn(
            message=request.message,
            conversation_id=request.conversation_id,
            user=current_user.get("username"),
            history=request.history
        )

        # Pega texto de resposta
        response_text = response_obj.get("response") or "Não foi possível gerar uma resposta no momento."
        logger.info(f"✅ Resposta gerada: '{response_text[:80]}...'")

        # Retorna resposta ao cliente
        return ChatResponse(
            response=response_text,
            content=response_text,
            conversation_id=session_id,
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        logger.exception("Erro ao processar mensagem")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar resposta: {e}")
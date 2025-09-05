from pydantic import BaseModel, model_validator  # BaseModel para schemas, model_validator para validações pós-criação
from typing import Optional, List, Dict         # Tipos opcionais e coleções
from datetime import datetime                   # Para timestamps

# -----------------------------
# Schema de requisição de chat
# -----------------------------
class ChatRequest(BaseModel):
    """
    Representa a requisição enviada pelo cliente para o endpoint de chat.
    """
    message: Optional[str] = None               # Mensagem principal do usuário
    content: Optional[str] = None               # Campo alternativo para mensagem
    conversation_id: Optional[str] = None       # Identificador da conversa (para histórico)
    history: Optional[List[Dict[str, str]]] = None  # Histórico de mensagens anteriores

    @model_validator(mode="after")
    def unify_message(self):
        """
        Garante que a mensagem principal seja preenchida:
        - Se 'message' estiver vazio, tenta usar 'content'.
        - Se nenhum dos dois estiver presente, lança erro.
        """
        if not self.message and self.content:
            self.message = self.content
        if not self.message:
            raise ValueError("Campo 'message' é obrigatório (ou envie 'content').")
        return self

# -----------------------------
# Schema de resposta de chat
# -----------------------------
class ChatResponse(BaseModel):
    """
    Representa a resposta enviada pelo backend ao cliente.
    """
    response: str                             # Texto da resposta gerada pelo sistema
    content: Optional[str] = None             # Campo alternativo que espelha 'response' se não fornecido
    conversation_id: str                       # ID da conversa (para associar histórico)
    timestamp: datetime                        # Momento em que a resposta foi gerada

    @model_validator(mode="after")
    def fill_content(self):
        """
        Garante que 'content' seja preenchido:
        - Se não for fornecido, copia o valor de 'response'.
        """
        if not self.content:
            self.content = self.response
        return self

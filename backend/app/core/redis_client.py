import os
import redis
import json
import logging
from typing import List, Dict

# -----------------------------
# Configuração do logger
# -----------------------------
logger = logging.getLogger(__name__)

# -----------------------------
# Configuração do Redis
# -----------------------------
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

# -----------------------------
# Testa a conexão com Redis
# -----------------------------
try:
    redis_client.ping()  # Testa se o Redis está ativo
    logger.info("✅ Redis conectado com sucesso!")
except Exception as e:
    logger.error(f"❌ Erro ao conectar com Redis: {e}")
    # Se a conexão falhar, vai lançar uma exceção e você poderá tratar fora


# -----------------------------
# Função para recuperar histórico de conversa
# -----------------------------
def get_conversation_history(session_id: str) -> List[Dict]:
    """
    Recupera o histórico de conversa do Redis para uma determinada sessão.
    
    Args:
        session_id (str): identificador único da sessão
    
    Returns:
        List[Dict]: lista de mensagens armazenadas (ou vazia)
    """
    try:
        data = redis_client.get(f"conversation:{session_id}")  # Chave única por sessão
        return json.loads(data) if data else []  # Retorna lista de mensagens, ou vazia
    except Exception as e:
        logger.error(f"Erro ao recuperar histórico: {e}")
        return []


# -----------------------------
# Função para armazenar histórico de conversa
# -----------------------------
def store_conversation_history(session_id: str, history: List[Dict], expire_seconds: int = 1800):
    """
    Armazena o histórico de conversa no Redis.
    
    Args:
        session_id (str): identificador da sessão
        history (List[Dict]): lista de mensagens
        expire_seconds (int): tempo de expiração em segundos (default 30 min)
    """
    try:
        redis_client.set(f"conversation:{session_id}", json.dumps(history), ex=expire_seconds)
    except Exception as e:
        logger.error(f"Erro ao armazenar histórico: {e}")


# -----------------------------
# Adiciona métodos ao cliente Redis
# -----------------------------
redis_client.get_conversation_history = get_conversation_history
redis_client.store_conversation_history = store_conversation_history

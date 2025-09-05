import os  # Biblioteca para interagir com o sistema operacional (variáveis de ambiente, caminhos, etc.)
from typing import List  # Para indicar tipos de listas
import logging  # Para registrar logs do sistema

# Cria um logger específico para este módulo
logger = logging.getLogger(__name__)

class Settings:
    """
    Classe de configurações que lê variáveis de ambiente e mantém tudo organizado.
    """

    def __init__(self):
        # Loga que estamos carregando as configurações
        logger.info("🔧 Carregando configurações...")

        # -----------------------------
        # Configuração de CORS
        # -----------------------------
        # Pega a variável CORS_ORIGINS do .env ou usa valor padrão
        cors_origins_str = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000"
        )
        # Converte a string separada por vírgula em uma lista e remove espaços extras
        self.cors_origins: List[str] = [origin.strip() for origin in cors_origins_str.split(',')]

        # -----------------------------
        # Configurações do JWT
        # -----------------------------
        # Chave secreta para assinar tokens JWT
        self.jwt_secret_key: str = os.getenv(
            "JWT_SECRET_KEY", 
            "a_very_secret_key_that_should_be_in_env"
        )
        # Algoritmo usado para assinar os tokens
        self.jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
        # Tempo de expiração dos tokens JWT em minutos
        self.jwt_access_token_expire_minutes: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30))

        # -----------------------------
        # Senha do admin
        # -----------------------------
        # Pega a senha do admin do .env e remove espaços extras
        self.admin_password: str = os.getenv("ADMIN_PASSWORD", "change_this_password").strip()



# -----------------------------
# Singleton para configurações
# -----------------------------
# Mantém uma instância única de Settings para o sistema inteiro
_settings = None

def get_settings() -> Settings:
    """
    Retorna a instância singleton das configurações.

    - Se já existir, retorna a mesma instância.
    - Se não existir, cria uma nova instância de Settings.
    """
    global _settings
    if _settings is None:
        _settings = Settings()  # Cria a instância pela primeira vez
    return _settings  # Retorna a instância existente

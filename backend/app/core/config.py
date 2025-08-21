import os
from typing import List
import logging

logger = logging.getLogger(__name__)

class Settings:
    """
    Classe de configurações que lê variáveis de ambiente.
    """
    def __init__(self):
        logger.info("🔧 Carregando configurações...")
        
        # CORS Origins
        cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
        self.cors_origins: List[str] = [origin.strip() for origin in cors_origins_str.split(',')]

        # JWT Settings
        self.jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "a_very_secret_key_that_should_be_in_env")
        self.jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_access_token_expire_minutes: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30))

        # Admin password
        # Adicione .strip() para remover espaços em branco no início ou fim
        self.admin_password: str = os.getenv("ADMIN_PASSWORD", "change_this_password").strip()
        
        # Log das configurações (sem mostrar senhas completas)
        logger.info(f"🔧 JWT_SECRET_KEY: {self.jwt_secret_key[:10]}***")
        logger.info(f"🔧 JWT_ALGORITHM: {self.jwt_algorithm}")
        logger.info(f"🔧 JWT_ACCESS_TOKEN_EXPIRE_MINUTES: {self.jwt_access_token_expire_minutes}")
        logger.info(f"🔧 ADMIN_PASSWORD: {self.admin_password[:3]}***")
        logger.info(f"🔧 CORS_ORIGINS: {self.cors_origins}")

# Instância global das configurações
_settings = None

def get_settings() -> Settings:
    """Retorna a instância singleton das configurações."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
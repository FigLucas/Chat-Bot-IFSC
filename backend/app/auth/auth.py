import os
from datetime import datetime, timedelta
from typing import Optional, Dict
import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from ..core.config import get_settings
from ..schemas.user import UserInDB, TokenData

# Configuração
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
settings = get_settings()

logger = logging.getLogger(__name__)

def get_users_from_env() -> Dict[str, dict]:
    """Carrega o usuário admin a partir das variáveis de ambiente."""
    admin_password = settings.admin_password
    hashed = pwd_context.hash(admin_password)
    return {
        "admin": {
            "username": "admin",
            "hashed_password": hashed,
            "role": "admin",
            "name": "Administrador",
            "email": "admin@ifsc.local"
        }
    }

# Simulação de banco de dados
FAKE_USERS_DB = get_users_from_env()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha fornecida corresponde à senha com hash."""
    result = pwd_context.verify(plain_password, hashed_password)
    logger.info(f"🔐 Verificação de senha: {plain_password[:3]}*** -> {result}")
    return result

def get_user(db: dict, username: str) -> Optional[UserInDB]:
    """Busca um usuário no 'banco de dados'."""
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None

def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """Autentica um usuário, retornando o usuário se as credenciais forem válidas."""
    # REMOVER log de senha em produção
    # logger.warning(f"DEBUG: Senha recebida do formulário: '{password}'")
    user = get_user(FAKE_USERS_DB, username)
    if not user:
        logger.warning(f"🔐 Usuário '{username}' não encontrado")
        return None
    if not verify_password(password, user.hashed_password):
        logger.warning(f"🔐 Senha incorreta para usuário '{username}'")
        return None
    logger.info(f"🔐 Login bem-sucedido para usuário '{username}'")
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria um novo token de acesso JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Dependência para obter o usuário atual a partir do token JWT."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação ausente"
        )
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        # Aqui pode buscar usuário no banco/fake_db se quiser
        return {"username": username, "role": payload.get("role", "user")}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
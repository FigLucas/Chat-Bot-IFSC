import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt


from ..core.config import get_settings
from ..schemas.user import UserInDB, TokenData

# Inicializa configurações globais (lê .env via get_settings)
settings = get_settings()

# Esquema OAuth2 para extrair token das requisições (usado por Depends)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Autentica um usuário comparando as credenciais fornecidas com as
    variáveis de ambiente (ADMIN_USERNAME e ADMIN_PASSWORD).

    Comportamento:
    - Recupera ADMIN_USERNAME (padrão 'admin') e ADMIN_PASSWORD via settings.
    - Se o username não bater com ADMIN_USERNAME, retorna None.
    - Se a senha não bater com ADMIN_PASSWORD (comparação direta), retorna None.
    - Em caso de sucesso, retorna um dict simples com informações do usuário.

    Observações de segurança:
    - A comparação é direta com o valor em .env. Em produção recomenda‑se
      armazenar hash em vez de texto claro.
    - Não há persistência em banco; é apenas verificação pontual contra .env.
    """
    admin_user = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = settings.admin_password

    if username != admin_user:
        # usuário não encontrado / inválido
        return None

    # comparação direta da senha com o valor em .env
    if password != admin_password:
        # senha inválida
        return None

    # retorno simples com os dados mínimos do usuário autenticado
    return {"username": admin_user, "role": "admin"}


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Gera um JWT de acesso.

    - 'data' deve conter as claims iniciais (ex.: {'sub': username, 'role': role}).
    - 'expires_delta' permite sobrescrever o tempo de expiração padrão.
    - Usa as configurações em settings para chave, algoritmo e duração.
    - Retorna o token JWT codificado em string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # tempo padrão obtido das configurações (em minutos)
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)

    # adiciona claim de expiração
    to_encode.update({"exp": expire})
    # assina e codifica o JWT
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dependência FastAPI para recuperar o usuário atual a partir do token JWT.

    Fluxo:
    - Recebe o token via OAuth2PasswordBearer (header Authorization: Bearer <token>).
    - Decodifica o JWT usando a chave e algoritmo das configurações.
    - Lê a claim 'sub' como username; se ausente, retorna 401.
    - Retorna um dict com username e role (padrão 'user' se não houver role no payload).
    - Em caso de erro de decodificação/assinatura, lança 401.

    Observações:
    - Esta função não consulta um banco; apenas retorna os dados contidos no token.
    - Use esta dependência em rotas que exigem autenticação.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação ausente"
        )
    try:
        # decodifica e valida o token
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        username: str = payload.get("sub")
        if username is None:
            # token não contém usuário válido
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        # retorno simples com informações mínimas do usuário
        return {"username": username, "role": payload.get("role", "user")}
    except JWTError:
        # token inválido, expirado ou assinatura incorreta
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
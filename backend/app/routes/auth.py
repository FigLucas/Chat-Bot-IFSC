from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
import logging

from ..auth.auth import authenticate_user, create_access_token
from ..core.config import get_settings
from ..schemas.auth import TokenWithUser, User

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)

@router.post("/login", response_model=TokenWithUser)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Autentica o usuário e retorna um token de acesso junto com os dados do usuário.
    """
    logger.info(f"Tentativa de login para o usuário: '{form_data.username}'")

    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "role": getattr(user, "role", "admin")
        },
        expires_delta=access_token_expires
    )

    user_data_for_response = User(
        username=user.username,
        name=getattr(user, 'name', None),
        email=getattr(user, 'email', None),
        role=getattr(user, 'role', 'admin')
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data_for_response
    }
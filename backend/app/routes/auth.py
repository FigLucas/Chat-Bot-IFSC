# -----------------------------
# Importações necessárias
# -----------------------------
from fastapi import APIRouter, Depends, HTTPException, status  # FastAPI para rotas, dependências e exceções
from fastapi.security import OAuth2PasswordRequestForm         # Formulário padrão OAuth2 para login
from datetime import timedelta                                 # Para calcular tempo de expiração do token
import logging                                                 # Para registrar logs

# Importa funções e classes do seu projeto
from ..auth.auth import authenticate_user, create_access_token  # Funções de autenticação e criação de JWT
from ..core.config import get_settings                          # Configurações da aplicação
from ..schemas.auth import TokenWithUser, User                  # Schemas de resposta e usuário

# -----------------------------
# Configuração do router e logger
# -----------------------------
router = APIRouter()                # Cria um roteador FastAPI para endpoints relacionados a auth
settings = get_settings()           # Obtém instância global de configurações
logger = logging.getLogger(__name__)  # Logger específico para este módulo

# -----------------------------
# Endpoint de login
# -----------------------------
@router.post("/login", response_model=TokenWithUser)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Autentica o usuário e retorna um token de acesso junto com os dados do usuário.

    Args:
        form_data (OAuth2PasswordRequestForm): contém username e password enviados pelo cliente

    Returns:
        dict: token JWT, tipo do token e dados do usuário
    """
    logger.info(f"Tentativa de login para o usuário: '{form_data.username}'")  # Log de tentativa de login

    # -----------------------------
    # Autenticação do usuário
    # -----------------------------
    user = authenticate_user(form_data.username, form_data.password)  # Verifica credenciais
    if not user:
        # Se usuário não existe ou senha incorreta, retorna 401
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},  # Cabeçalho exigido pelo OAuth2
        )
    
    # -----------------------------
    # Criação do token JWT
    # -----------------------------
    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)  # Expiração do token
    access_token = create_access_token(
        data={
            "sub": user["username"],                  # Identificador do usuário (dict access)
            "role": user.get("role", "admin")        # Papel do usuário, default "admin"
        },
        expires_delta=access_token_expires
    )

    # -----------------------------
    # Preparando dados do usuário para resposta
    # -----------------------------
    user_data_for_response = User(
        username=user["username"],
        name=user.get('name', None),
        email=user.get('email', None),
        role=user.get('role', 'admin')
    )

    # -----------------------------
    # Retorna token e dados do usuário
    # -----------------------------
    return {
        "access_token": access_token,
        "token_type": "bearer",  # Padrão OAuth2
        "user": user_data_for_response
    }

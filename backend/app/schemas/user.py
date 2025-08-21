from typing import Optional
from pydantic import BaseModel

class LoginRequest(BaseModel):
    """Schema para a requisição de login."""
    username: str
    password: str

class User(BaseModel):
    """Schema base para o usuário."""
    username: str
    name: Optional[str] = None

class UserInDB(BaseModel):
    """Schema do usuário como armazenado no 'banco'."""
    username: str
    hashed_password: str
    role: str = "admin"
    name: Optional[str] = None
    email: Optional[str] = None

class Token(BaseModel):
    """Schema para o token de acesso."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Schema para os dados contidos no token."""
    username: Optional[str] = None
from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    """Schema para os dados do usuário na resposta."""
    username: str
    name: Optional[str] = None
    email: Optional[str] = None
    role: str

class Token(BaseModel):
    """Schema base do token."""
    access_token: str
    token_type: str

class TokenWithUser(Token):
    """Schema completo da resposta de login, incluindo o token e os dados do usuário."""
    user: User
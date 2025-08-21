from pydantic import BaseModel, model_validator
from typing import Optional
from datetime import datetime

class ChatRequest(BaseModel):
    message: Optional[str] = None
    content: Optional[str] = None
    conversation_id: Optional[str] = None

    @model_validator(mode="after")
    def unify_message(self):
        if not self.message and self.content:
            self.message = self.content
        if not self.message:
            raise ValueError("Campo 'message' é obrigatório (ou envie 'content').")
        return self

class ChatResponse(BaseModel):
    response: str
    content: Optional[str] = None
    conversation_id: str
    timestamp: datetime

    @model_validator(mode="after")
    def fill_content(self):
        if not self.content:
            self.content = self.response
        return self
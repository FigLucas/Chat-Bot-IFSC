"""
Modelos Pydantic para o sistema de chat
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChatMessage(BaseModel):
    content: str
    role: str = "user"

class ChatResponse(BaseModel):
    content: str
    role: str
    confidence: float = 0.0
    response_type: str = "default"
    processing_time: float = 0.0
    sources: List[str] = []
    metadata: Optional[Dict[str, Any]] = None

class SystemStats(BaseModel):
    session_duration_minutes: float
    total_requests: int
    total_cost_usd: float
    tokens_input: int
    tokens_output: int
    tokens_total: int
    response_types: Dict[str, int]
    avg_response_time_seconds: float
    cost_per_request: float

class ConfigUpdate(BaseModel):
    temperature: Optional[float] = None
    max_response_tokens: Optional[int] = None
    retriever_k: Optional[int] = None

class HealthStatus(BaseModel):
    status: str
    system: str
    version: str
    initialized: bool
    service_available: bool
import logging
import uvicorn
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Importações diretas das rotas
from app.routes import auth, chat
from app.core.config import get_settings

# Configuração do logging
logging.basicConfig(level="INFO", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Inicialização da aplicação
app = FastAPI(
    title="IFSC Chat API",
    description="API para o sistema de Chat Inteligente do IFSC.",
    version="2.0.0"
)

# Configuração do CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusão das rotas
app.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
app.include_router(chat.router, tags=["Chat"]) # Rota do chat agora é incluída diretamente

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Bem-vindo à API do IFSC Chat"}

logger = logging.getLogger("uvicorn.error")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    logger.error(f"⚠️ Erro de validação em {request.url}: {exc.errors()} | body={await request.body()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

# -----------------------------
# Importações
# -----------------------------
import logging 
import uvicorn  # Servidor ASGI para rodar FastAPI
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Para permitir requisições cross-origin
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse  # Para customizar respostas de erro

# Importação das rotas da aplicação
from app.routes import auth, chat
from app.core.config import get_settings  # Configurações da aplicação (.env, etc)

# -----------------------------
# Configuração do logging
# -----------------------------
logging.basicConfig(
    level="INFO", 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # Formato de log
)

# -----------------------------
# Inicialização da aplicação
# -----------------------------
app = FastAPI(
    title="IFSC Chat API",  # Título da documentação Swagger
    description="API para o sistema de Chat Inteligente do IFSC.",
    version="2.0.0"
)

# -----------------------------
# Configuração do CORS
# -----------------------------
settings = get_settings()  # Carrega variáveis de ambiente
origins = getattr(settings, "cors_origins", ["http://localhost:3000", "http://127.0.0.1:3000"])
'''
# Middleware CORS para permitir requisições de front-end // 
 Para produção
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://meusite.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],   # só os que realmente usa
    allow_headers=["Content-Type", "Authorization"],  # só os necessários
)
'''
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # Origem permitida
    allow_credentials=True,         # Permitir cookies
    allow_methods=["*"],            # Todos os métodos HTTP
    allow_headers=["*"],            # Todos os headers
)

# -----------------------------
# Inclusão das rotas
# -----------------------------
app.include_router(auth.router, prefix="/auth", tags=["Autenticação"])  # Endpoints de login
app.include_router(chat.router, tags=["Chat"])  # Endpoints do chat

# -----------------------------
# Endpoint raiz
# -----------------------------
@app.get("/", tags=["Root"])
async def root():
    return {"message": "Bem-vindo à API do IFSC Chat"}

# Logger do uvicorn
logger = logging.getLogger("uvicorn.error")

# -----------------------------
# Handler de erros de validação
# -----------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    # Loga o erro e o corpo da requisição
    logger.error(f"⚠️ Erro de validação em {request.url}: {exc.errors()} | body={await request.body()}")
    # Retorna JSON com detalhes do erro
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )

# -----------------------------
# Inicialização via Uvicorn
# -----------------------------
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",  # caminho do app FastAPI
        host="0.0.0.0",  # expõe em todas interfaces de rede
        port=8000,       # porta padrão
        reload=True      # reload automático para desenvolvimento
    )

# producao
'''

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,     # sem reload
        workers=4         # múltiplos workers (se não usar Gunicorn)
    )
'''
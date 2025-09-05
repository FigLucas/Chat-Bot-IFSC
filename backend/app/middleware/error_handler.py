"""
Middleware para tratamento de erros na aplicação FastAPI.
Fornece respostas JSON padronizadas para diferentes tipos de exceções.
"""

# -----------------------------
# Importações necessárias
# -----------------------------
from fastapi import FastAPI, Request, HTTPException  # Classes do FastAPI
from fastapi.responses import JSONResponse           # Para retornar respostas JSON
from fastapi.exceptions import RequestValidationError  # Para tratar erros de validação
import logging        # Para registrar logs
import traceback      # Para capturar stack trace de erros
from datetime import datetime  # Para registrar timestamps nos logs/respostas

# -----------------------------
# Logger do módulo
# -----------------------------
logger = logging.getLogger(__name__)  # Cria logger específico para este módulo


# -----------------------------
# Função principal para adicionar handlers de erro
# -----------------------------
def add_error_handlers(app: FastAPI):
    """
    Adiciona handlers personalizados de exceção à aplicação FastAPI.

    Args:
        app (FastAPI): instância da aplicação FastAPI
    """

    # -----------------------------
    # Handler para HTTPException
    # -----------------------------
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """
        Trata exceções do tipo HTTPException.

        Retorna um JSON com:
            - error: descrição do erro
            - status_code: código HTTP
            - timestamp: hora do erro
            - path: URL requisitada
        """
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "status_code": exc.status_code,
                "timestamp": datetime.now().isoformat(),
                "path": str(request.url.path)
            }
        )

    # -----------------------------
    # Handler para RequestValidationError
    # -----------------------------
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Trata erros de validação (por exemplo, campos obrigatórios faltando ou tipos incorretos).

        Retorna um JSON com:
            - error: mensagem genérica de validação
            - details: lista detalhada dos erros
            - timestamp: hora do erro
            - path: URL requisitada
        """
        return JSONResponse(
            status_code=422,  # Status code padrão para erro de validação
            content={
                "error": "Erro de validação",
                "details": exc.errors(),  # Lista detalhada dos erros
                "timestamp": datetime.now().isoformat(),
                "path": str(request.url.path)
            }
        )

    # -----------------------------
    # Handler para qualquer outra exceção
    # -----------------------------
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """
        Trata erros gerais não capturados pelos handlers anteriores.

        - Loga o erro no logger, incluindo stack trace
        - Retorna JSON padronizado com status 500
        """
        logger.error(f"Erro não tratado: {exc}")
        logger.error(traceback.format_exc())  # Stack trace completo

        return JSONResponse(
            status_code=500,  # Erro interno do servidor
            content={
                "error": "Erro interno do servidor",
                # Se a aplicação estiver em modo debug, mostra detalhes; caso contrário, mostra mensagem genérica
                "detail": str(exc) if app.debug else "Erro interno",
                "timestamp": datetime.now().isoformat(),
                "path": str(request.url.path)
            }
        )

"""
Middleware para tratamento de erros
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import traceback
from datetime import datetime

logger = logging.getLogger(__name__)

def add_error_handlers(app: FastAPI):
    """Adiciona handlers de erro à aplicação FastAPI"""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handler para HTTPException"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "status_code": exc.status_code,
                "timestamp": datetime.now().isoformat(),
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handler para erros de validação"""
        return JSONResponse(
            status_code=422,
            content={
                "error": "Erro de validação",
                "details": exc.errors(),
                "timestamp": datetime.now().isoformat(),
                "path": str(request.url.path)
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handler para erros gerais"""
        logger.error(f"Erro não tratado: {exc}")
        logger.error(traceback.format_exc())
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Erro interno do servidor",
                "detail": str(exc) if app.debug else "Erro interno",
                "timestamp": datetime.now().isoformat(),
                "path": str(request.url.path)
            }
        )
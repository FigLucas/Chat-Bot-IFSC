"""
Script para executar o servidor FastAPI
"""
import os
import uvicorn
from pathlib import Path
import sys

# Adicionar o diretório backend ao path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Função principal para executar o servidor"""
    
    # Configurações do servidor
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    reload = os.getenv("API_RELOAD", "true").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    print("🚀 Iniciando servidor IFSC Chat API...")
    print(f"🌐 Host: {host}:{port}")
    print(f"🔄 Reload: {reload}")
    print(f"📝 Log Level: {log_level}")
    
    # Verificar se as chaves de API estão definidas
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ ATENÇÃO: OPENAI_API_KEY não está definida!")
    if not os.getenv("MARITACA_API_KEY"):
        print("⚠️ ATENÇÃO: MARITACA_API_KEY não está definida!")
    
    # Executar servidor
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level
    )

if __name__ == "__main__":
    main()
# Estágio 1: Base com Python
FROM python:3.11-slim as base

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Impede o Python de gerar arquivos .pyc e garante que o output não seja bufferizado
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Estágio 2: Instalação de dependências
FROM base as builder

# Copia apenas o arquivo de dependências para aproveitar o cache do Docker
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Estágio 3: Imagem final de produção
FROM base as final

# Copia as dependências instaladas do estágio anterior
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copia o código da sua aplicação para dentro do container
COPY ./app ./app

# Expõe a porta que a aplicação vai rodar
EXPOSE 8000

# Comando para iniciar a aplicação FastAPI quando o container for executado
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# Assistente Virtual IFSC-USP

Assistente virtual para dúvidas sobre o IFSC-USP, utilizando IA, RAG (Retrieval-Augmented Generation) e integração com modelos OpenAI e Maritaca. O sistema possui frontend em Next.js/React e backend em FastAPI, com autenticação JWT e suporte a Docker.

## Estrutura do Projeto

```
.
├── backend/         # Backend FastAPI (Python)
├── frontend/        # Frontend Next.js (React/TypeScript)
├── pdfs/            # PDFs indexados pelo sistema
├── vectorstore/     # Base vetorial FAISS
├── cache/           # Cache de respostas
├── docker-compose.yml
├── .env
├── .gitignore
└── ...
```

## Pré-requisitos

- Docker e Docker Compose instalados
- Chaves de API válidas para OpenAI e Maritaca (definidas em `.env`)

## Configuração

1. **Clone o repositório:**
   ```sh
   git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
   cd SEU_REPOSITORIO
   ```

2. **Configure as variáveis de ambiente:**
   - Edite o arquivo `.env` na raiz com suas chaves e configurações.

3. **(Opcional) Adicione PDFs em `pdfs/` para indexação.**

## Como rodar com Docker

```sh
docker-compose up --build
```

- O frontend estará disponível em [http://localhost:3000](http://localhost:3000)
- O backend estará disponível em [http://localhost:8000](http://localhost:8000)

## Tecnologias

- **Frontend:** Next.js, React, TailwindCSS, TypeScript
- **Backend:** FastAPI, LangChain, FAISS, OpenAI, Maritaca
- **Autenticação:** JWT
- **Infraestrutura:** Docker, Docker Compose

## Funcionalidades

- Login de usuário com autenticação JWT
- Chat inteligente com respostas baseadas em documentos do IFSC
- Upload e indexação de PDFs
- Busca semântica e reranking de respostas
- Interface moderna e responsiva

## Estrutura dos principais diretórios

- `frontend/`: Código do frontend (Next.js)
- `backend/`: Código do backend (FastAPI)
- `pdfs/`: PDFs para indexação
- `vectorstore/`: Base vetorial FAISS
- `cache/`: Cache de respostas

## Variáveis de ambiente principais

Veja o arquivo `.env.example` para exemplos e instruções.

```markdown
// filepath: README.md
# 🤖 Assistente Virtual IFSC-USP

Sistema de chat inteligente com IA para responder dúvidas sobre o IFSC-USP, utilizando RAG (Retrieval-Augmented Generation) e integração com modelos OpenAI e Maritaca.

## 📋 Índice

- [Características](#-características)
- [Arquitetura](#-arquitetura)
- [Tecnologias](#-tecnologias)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação e Configuração](#-instalação-e-configuração)
- [Deploy](#-deploy)
- [Uso](#-uso)
- [API Endpoints](#-api-endpoints)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Contribuição](#-contribuição)

## ✨ Características

- 🔐 **Autenticação JWT** com middleware de segurança
- 🧠 **Chat inteligente** usando RAG com busca semântica
- 📄 **Processamento de PDFs** com indexação automática no FAISS
- 🔍 **Reranking de respostas** para melhor relevância
- 💾 **Cache Redis** para histórico de conversas com TTL
- 🌐 **Interface moderna** responsiva com Next.js e TailwindCSS
- 🐳 **Containerização** completa com Docker
- 📊 **Logs estruturados** para monitoramento


## 🛠️ Tecnologias

### Frontend
- **Next.js 14** - Framework React com App Router
- **TypeScript** - Tipagem estática
- **TailwindCSS** - Framework CSS utilitário
- **React Hooks** - Gerenciamento de estado
- **Fetch API** - Comunicação com backend

### Backend
- **FastAPI** - Framework web async Python
- **LangChain** - Framework para aplicações com LLM
- **FAISS** - Vector database para busca semântica
- **Redis** - Cache e sessões
- **PyPDF2** - Processamento de PDFs
- **JWT** - Autenticação stateless
- **Uvicorn** - Servidor ASGI

### IA e ML
- **OpenAI GPT** - Modelo principal de linguagem
- **Maritaca AI** - Modelo alternativo brasileiro
- **OpenAI Embeddings** - Geração de vetores semânticos
- **Sentence Transformers** - Reranking de documentos

### Infraestrutura
- **Docker & Docker Compose** - Containerização
- **Redis** - Cache distribuído

## 📋 Pré-requisitos

- **Docker** 20.10+ e **Docker Compose** 2.0+
- **Node.js** 18+ (para desenvolvimento local)
- **Python** 3.11+ (para desenvolvimento local)
- **Chaves de API**:
  - OpenAI API Key
  - Maritaca API Key (opcional)

## 🚀 Instalação e Configuração

### 1. Clone o repositório
```bash
git clone https://github.com/SEU_USUARIO/chat-bot-ifsc.git
cd chat-bot-ifsc
```

### 2. Configure as variáveis de ambiente
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite com suas chaves
nano .env
```



### 3. (Opcional) Adicione documentos
```bash
# Coloque PDFs na pasta para indexação automática
cp seus_pdfs/* ./pdfs/
```

### 4. Execute com Docker
```bash
# Desenvolvimento
docker-compose up --build

# Produção
docker-compose -f docker-compose.prod.yml up --build -d
```


## 📖 Uso

### Interface Web
1. Acesse: `http://localhost:3000`
2. Faça login com credenciais admin
3. Digite suas perguntas sobre o IFSC-USP
4. O sistema buscará informações nos documentos indexados

### Exemplo de Conversa
```
Usuário: "Quais são os cursos oferecidos no IFSC?"
Bot: "Com base nos documentos do IFSC, os principais cursos oferecidos são..."

Usuário: "Como faço para me inscrever?"
Bot: "Para se inscrever nos cursos do IFSC, você deve..."
```

## 📡 API Endpoints

### Autenticação
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=sua_senha
```

### Chat
```http
POST /chat
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "message": "Sua pergunta aqui",
  "conversation_id": "optional-session-id",
  "history": [
    {"role": "user", "content": "pergunta anterior"},
    {"role": "assistant", "content": "resposta anterior"}
  ]
}
```

### Status
```http
GET /
# Retorna: {"message": "Bem-vindo à API do IFSC Chat"}
```

## 📁 Estrutura do Projeto

```
chat-bot-ifsc/
├── 🌐 frontend/              # Interface Next.js
│   ├── app/                  # App Router (Next.js 14)
│   ├── components/           # Componentes React
│   ├── lib/                  # Utilitários e API client
│   └── Dockerfile           # Container frontend
├── 🔧 backend/              # API FastAPI
│   ├── app/
│   │   ├── auth/            # Autenticação JWT
│   │   ├── core/            # Configurações e Redis
│   │   ├── middleware/      # Error handlers
│   │   ├── routes/          # Endpoints da API
│   │   ├── schemas/         # Modelos Pydantic
│   │   └── services/        # RAG System e chat
│   ├── cache/               # Cache local
│   ├── pdfs/                # Documentos fonte
│   ├── vectorstore/         # Base FAISS
│   └── Dockerfile          # Container backend
├── 📄 pdfs/                 # PDFs para indexação
├── 🗃️ vectorstore/          # Dados FAISS persistidos
├── 💾 cache/                # Cache de respostas
├── 🐳 docker-compose.yml    # Orquestração dev
├── 🚀 docker-compose.prod.yml # Orquestração produção
└── 📋 .env.example          # Variáveis de ambiente
```

### Principais Módulos

#### Backend (`/backend/app/`)
- **`routes/chat.py`** - Endpoint principal do chat
- **`services/chat_system.py`** - RAG System com FAISS
- **`auth/auth.py`** - Autenticação JWT
- **`core/redis_client.py`** - Cliente Redis para sessões
- **`middleware/error_handler.py`** - Tratamento de erros

#### Frontend (`/frontend/`)
- **`components/ChatInterface.tsx`** - Interface principal do chat
- **`lib/api.ts`** - Cliente da API
- **`app/login/page.tsx`** - Página de autenticação

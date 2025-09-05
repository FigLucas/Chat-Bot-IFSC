import os
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import numpy as np
import uuid

# Cliente Redis personalizado para armazenar histórico de conversa
from ..core.redis_client import redis_client

# Bibliotecas do LangChain para RAG (Retrieval-Augmented Generation)
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------
# Configurações do sistema RAG
# -----------------------------
@dataclass
class IFSCConfig:
    """Configurações gerais do sistema RAG do IFSC"""
    chunk_size: int = 1000                     # Tamanho máximo de cada chunk de texto
    chunk_overlap: int = 200                   # Sobreposição entre chunks
    retriever_candidates_k: int = 20           # Número de candidatos retornados pelo retriever
    final_docs_k: int = 5                      # Número final de documentos enviados ao LLM
    temperature: float = 0.1                   # Temperatura do LLM para controlar aleatoriedade
    model: str = 'sabia-3.1'                   # Modelo LLM Maritaca
    max_response_tokens: int = 800             # Máximo de tokens na resposta
    embeddings_model: str = "text-embedding-3-small"  # Modelo para embeddings
    debug_mode: bool = True                    # Ativa modo debug

config = IFSCConfig()

PDF_PATH = Path("pdfs/")                       # Pasta onde os PDFs e TXTs estão
VECTOR_DB_PATH = Path("vectorstore/ifsc_geral")# Pasta para armazenar vectorstore

# -----------------------------
# Prompt padrão para LLM
# -----------------------------
SYSTEM_PROMPT = """
Você é um assistente especializado do IFSC-USP. Responda sempre em português brasileiro.
- Gere respostas diretas com enfoque no que foi perguntado
CONTEXTO:
{context}

PERGUNTA: {question}

RESPOSTA:
"""

PROMPT_TEMPLATE = PromptTemplate.from_template(SYSTEM_PROMPT)

# -----------------------------
# Sistema RAG (Singleton)
# -----------------------------
class RAGSystem:
    _instance = None

    def __init__(self):
        # Previne instanciamento direto
        raise RuntimeError("Use RAGSystem.get_instance() para obter o sistema.")

    @classmethod
    def get_instance(cls):
        """Retorna a instância singleton do RAGSystem"""
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance._init_system()
        return cls._instance

    def _init_system(self):
        """Inicializa embeddings, vectorstore e LLM"""
        logger.info("🚀 Inicializando RAGSystem (com técnicas avançadas)...")

        # Verifica chaves de API
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY não configurada")
        if not os.getenv("MARITACA_API_KEY"):
            raise RuntimeError("MARITACA_API_KEY não configurada")

        # Configura embeddings
        self.embeddings = OpenAIEmbeddings(
            model=config.embeddings_model,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

        # Cria ou carrega vectorstore
        self.vectorstore = self._create_or_load_vectorstore(self.embeddings)
        if not self.vectorstore:
            raise RuntimeError("⚠️ Não foi possível criar/carregar vectorstore.")

        # Inicializa LLM
        self.llm = ChatOpenAI(
            model=config.model,
            temperature=config.temperature,
            api_key=os.getenv("MARITACA_API_KEY"),
            base_url="https://chat.maritaca.ai/api",
            max_tokens=config.max_response_tokens,
        )

        # Cache interno para QA
      #  self._qa_cache: Dict[str, Dict[str, Any]] = {}
        logger.info("✅ RAGSystem inicializado.")

    # -----------------------------
    # Carregamento ou criação de vectorstore
    # -----------------------------
    def _create_or_load_vectorstore(self, embeddings_model) -> Optional[FAISS]:
        """Carrega um vectorstore existente ou cria um novo a partir dos documentos"""
        if VECTOR_DB_PATH.exists() and any(VECTOR_DB_PATH.iterdir()):
            logger.info("🔁 Carregando vectorstore existente...")
            try:
                return FAISS.load_local(str(VECTOR_DB_PATH), embeddings_model, allow_dangerous_deserialization=True)
            except Exception as e:
                logger.warning(f"Falha ao carregar vectorstore: {e}. Recriando...")

        # Criando novo vectorstore
        logger.info("🔧 Criando novo vectorstore a partir de documentos...")
        all_pages = []

        # Carrega arquivos TXT
        for txt_file in PDF_PATH.glob("*.txt"):
            logger.info(f"  📝 Processando TXT: {txt_file.name}")
            loader = TextLoader(str(txt_file), encoding='utf-8')
            all_pages.extend(loader.load())

        # Carrega arquivos PDF
        for pdf_file in PDF_PATH.glob("*.pdf"):
            logger.info(f"  📖 Processando PDF: {pdf_file.name}")
            loader = PyPDFLoader(str(pdf_file))
            all_pages.extend(loader.load())

        if not all_pages:
            logger.warning("Nenhum documento encontrado para processar.")
            return None

        # Divide documentos em chunks para embeddings
        separators = ["\nP: ", "P: ", "\n\n", "\n", ". ", " ", ""]
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=separators,
            keep_separator=True
        )
        documents = text_splitter.split_documents(all_pages)
        logger.info(f"  → Documentos divididos em {len(documents)} chunks")

        # Cria vectorstore FAISS
        db = FAISS.from_documents(documents, embeddings_model)
        VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)
        db.save_local(str(VECTOR_DB_PATH))
        logger.info("💾 Vectorstore salvo com sucesso.")
        return db

    # -----------------------------
    # Expansão de query para melhorar resultados
    # -----------------------------
    def _expand_query(self, query: str) -> str:
        """Expande termos da query para incluir sinônimos e termos relacionados"""
        query_lower = query.lower()
        expansions = {
            'ic': 'iniciação científica pibic pibit pub', 
            'bolsa': 'auxílio financiamento',
            'pibic': 'programa institucional bolsas iniciação científica',
            'pibit': 'programa institucional bolsas iniciação tecnológica',
            'pub': 'programa unificado bolsas usp',
            'fapesp': 'fundação amparo pesquisa estado são paulo',
            'mestrado': 'pós-graduação', 
            'doutorado': 'pós-graduação phd',
        }
        expanded_terms = [exp for term, exp in expansions.items() if term in query_lower]
        if expanded_terms:
            return f"{query} {' '.join(expanded_terms)}"
        return query

    # -----------------------------
    # Reranking simplificado
    # -----------------------------
    def _rerank_docs(self, query: str, documents: List[Any], top_n: int) -> List[Any]:
        """Reordena documentos com base na similaridade com a query"""
        if not documents:
            return []

        try:
            query_embedding = self.embeddings.embed_query(query)
            doc_embeddings = self.embeddings.embed_documents([doc.page_content for doc in documents])
            
            similarities = [np.dot(query_embedding, doc_emb) / (np.linalg.norm(query_embedding) * np.linalg.norm(doc_emb)) for doc_emb in doc_embeddings]
            scored_docs = list(zip(documents, similarities))
            scored_docs.sort(key=lambda x: x[1], reverse=True)

            return [doc for doc, score in scored_docs[:top_n]]
        except Exception as e:
            logger.warning(f"Falha no reranking: {e}. Retornando ordem original.")
            return documents[:top_n]

    # -----------------------------
    # Otimiza contexto para prompt
    # -----------------------------
    def _optimize_context(self, docs: List[Any]) -> str:
        """Concatena conteúdo dos documentos para formar o contexto do prompt"""
        if not docs:
            return "Nenhum documento relevante foi encontrado."
        parts = [f"[{doc.metadata.get('source', 'N/A')}]\n{doc.page_content.strip()}" for doc in docs]
        return "\n\n---\n\n".join(parts)

    # -----------------------------
    # Resposta principal
    # -----------------------------
    def answer_query(self, query: str, session_id: Optional[str] = None, history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Processa a query e retorna resposta, contexto, histórico e tempo de processamento"""
        start = time.time()
        if not session_id:
            session_id = str(uuid.uuid4())

        # Recupera histórico do Redis se não fornecido
        if history is None:
            history = redis_client.get_conversation_history(session_id) if session_id else []

        # Prepara contexto com histórico
        history_context = ""
        if history:
            for msg in history[-5:]:  # últimas 5 mensagens
                role = "Usuário" if msg.get("role") == "user" else "Assistente"
                history_context += f"{role}: {msg.get('content', '')}\n"

        # Busca e reranking
        expanded_query = self._expand_query(query)
        if expanded_query != query:
            logger.info(f"Query expandida para: '{expanded_query}'")

        candidate_docs = self.vectorstore.similarity_search(expanded_query, k=config.retriever_candidates_k)
        final_docs = self._rerank_docs(query, candidate_docs, top_n=config.final_docs_k)

        context = self._optimize_context(final_docs)

        # Cria prompt final incluindo histórico
        if history_context:
            prompt_with_history = f"HISTÓRICO DA CONVERSA:\n{history_context}\n\n{SYSTEM_PROMPT}"
            prompt_template = PromptTemplate.from_template(prompt_with_history)
        else:
            prompt_template = PROMPT_TEMPLATE
            
        prompt = prompt_template.format(context=context, question=query)

        # Chama LLM para gerar resposta
        try:
            response = self.llm.invoke(prompt)
            answer_text = response.content
        except Exception as e:
            logger.error(f"Erro ao chamar LLM:) {e}")
            answer_text = "Desculpe, não consegui processar sua solicitação no momento."

        # Armazena nova interação no histórico
        new_history = {"role": "user", "content": query}
        if session_id:
            redis_client.store_conversation_history(session_id, new_history, expire_seconds=1800)

        return {
            "response": answer_text,
            "context": context,
            "session_id": session_id,
            "processing_time": time.time() - start,
            "confidence": 0.8  # placeholder
        }

# -----------------------------
# Função principal para processar mensagens (interface pública)
# -----------------------------
def process_message(message: str, conversation_id: Optional[str] = None, user: Optional[str] = None, history: Optional[List[Dict]] = None) -> Dict[str, Any]:
    """
    Função principal que processa uma mensagem do usuário usando o RAGSystem.
    
    Args:
        message: Mensagem/pergunta do usuário
        conversation_id: ID da conversa (opcional)
        user: Nome do usuário (opcional, para logs)
        history: Histórico de mensagens (opcional)
    
    Returns:
        Dict com response, session_id, context, etc.
    """
    try:
        # Obtém instância singleton do RAGSystem
        rag_system = RAGSystem.get_instance()
        
        # Log de início do processamento
        logger.info(f"🔄 Processando mensagem de {user or 'usuário anônimo'}: '{message[:50]}...'")
        
        # Chama o método answer_query do RAGSystem
        result = rag_system.answer_query(
            query=message,
            session_id=conversation_id,
            history=history
        )
        
        logger.info(f"✅ Mensagem processada com sucesso em {result.get('processing_time', 0):.2f}s")
        return result
        
    except Exception as e:
        logger.exception(f"❌ Erro ao processar mensagem: {e}")
        return {
            "response": f"Desculpe, ocorreu um erro ao processar sua mensagem: {str(e)}",
            "session_id": conversation_id or str(uuid.uuid4()),
            "context": "",
            "processing_time": 0,
            "confidence": 0
        }

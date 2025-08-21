import os
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import numpy as np # Necessário para o reranking

# LangChain / wrappers
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configurações ---
@dataclass
class IFSCConfig:
    chunk_size: int = 1000
    chunk_overlap: int = 200
    # Aumentamos os candidatos para dar mais material ao reranker
    retriever_candidates_k: int = 20
    # O número final de documentos a serem enviados ao LLM
    final_docs_k: int = 5
    temperature: float = 0.1
    model: str = 'sabia-3.1' # Modelo da Maritaca
    max_response_tokens: int = 800
    embeddings_model: str = "text-embedding-3-small"
    debug_mode: bool = True

config = IFSCConfig()

PDF_PATH = Path("pdfs/")
VECTOR_DB_PATH = Path("vectorstore/ifsc_geral")

# --- Prompt ---
SYSTEM_PROMPT = """
Você é um assistente especializado do IFSC-USP. Responda sempre em português brasileiro.
- Gere respostas diretas com enfoque no que foi perguntado
CONTEXTO:
{context}

PERGUNTA: {question}

RESPOSTA:
"""

PROMPT_TEMPLATE = PromptTemplate.from_template(SYSTEM_PROMPT)

# -------------------------
# RAG System (com técnicas avançadas)
# -------------------------
class RAGSystem:
    _instance = None

    def __init__(self):
        raise RuntimeError("Use RAGSystem.get_instance() para obter o sistema.")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance._init_system()
        return cls._instance

    def _init_system(self):
        logger.info("🚀 Inicializando RAGSystem (com técnicas avançadas)...")
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY não configurada")
        if not os.getenv("MARITACA_API_KEY"):
            raise RuntimeError("MARITACA_API_KEY não configurada")

        self.embeddings = OpenAIEmbeddings(
            model=config.embeddings_model,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

        self.vectorstore = self._create_or_load_vectorstore(self.embeddings)
        if not self.vectorstore:
            raise RuntimeError("⚠️ Não foi possível criar/carregar vectorstore.")

        self.llm = ChatOpenAI(
            model=config.model,
            temperature=config.temperature,
            api_key=os.getenv("MARITACA_API_KEY"),
            base_url="https://chat.maritaca.ai/api",
            max_tokens=config.max_response_tokens,
        )
        self._qa_cache: Dict[str, Dict[str, Any]] = {}
        logger.info("✅ RAGSystem inicializado.")

    def _create_or_load_vectorstore(self, embeddings_model) -> Optional[FAISS]:
        if VECTOR_DB_PATH.exists() and any(VECTOR_DB_PATH.iterdir()):
            logger.info("🔁 Carregando vectorstore existente...")
            try:
                return FAISS.load_local(str(VECTOR_DB_PATH), embeddings_model, allow_dangerous_deserialization=True)
            except Exception as e:
                logger.warning(f"Falha ao carregar vectorstore: {e}. Recriando...")

        logger.info("🔧 Criando novo vectorstore a partir de documentos...")
        all_pages = []
        # Processa TXTs (ideal para FAQs)
        for txt_file in PDF_PATH.glob("*.txt"):
            logger.info(f"  📝 Processando TXT: {txt_file.name}")
            loader = TextLoader(str(txt_file), encoding='utf-8')
            all_pages.extend(loader.load())
        
        # Processa PDFs
        for pdf_file in PDF_PATH.glob("*.pdf"):
            logger.info(f"  📖 Processando PDF: {pdf_file.name}")
            loader = PyPDFLoader(str(pdf_file))
            all_pages.extend(loader.load())

        if not all_pages:
            logger.warning("Nenhum documento encontrado para processar.")
            return None

        # Otimizado para formato P:/R:
        separators = ["\nP: ", "P: ", "\n\n", "\n", ". ", " ", ""]
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=separators,
            keep_separator=True
        )
        documents = text_splitter.split_documents(all_pages)
        logger.info(f"  → Documentos divididos em {len(documents)} chunks")

        db = FAISS.from_documents(documents, embeddings_model)
        VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)
        db.save_local(str(VECTOR_DB_PATH))
        logger.info("💾 Vectorstore salvo com sucesso.")
        return db
    
    # INTEGRADO: Lógica de expansão de query do seu código antigo
    def _expand_query(self, query: str) -> str:
        query_lower = query.lower()
        expansions = {
            'ic': 'iniciação científica pibic pibit pub', 'bolsa': 'auxílio financiamento',
            'pibic': 'programa institucional bolsas iniciação científica',
            'pibit': 'programa institucional bolsas iniciação tecnológica',
            'pub': 'programa unificado bolsas usp',
            'fapesp': 'fundação amparo pesquisa estado são paulo',
            'mestrado': 'pós-graduação', 'doutorado': 'pós-graduação phd',
        }
        expanded_terms = [exp for term, exp in expansions.items() if term in query_lower]
        if expanded_terms:
            return f"{query} {' '.join(expanded_terms)}"
        return query

    # INTEGRADO: Lógica de reranking simplificada
    def _rerank_docs(self, query: str, documents: List[Any], top_n: int) -> List[Any]:
        if not documents:
            return []
        
        try:
            query_embedding = self.embeddings.embed_query(query)
            doc_embeddings = self.embeddings.embed_documents([doc.page_content for doc in documents])
            
            # Calcula a similaridade de cosseno
            similarities = [np.dot(query_embedding, doc_emb) / (np.linalg.norm(query_embedding) * np.linalg.norm(doc_emb)) for doc_emb in doc_embeddings]

            # Combina o documento com sua pontuação de similaridade
            scored_docs = list(zip(documents, similarities))

            # Ordena os documentos pela pontuação, do maior para o menor
            scored_docs.sort(key=lambda x: x[1], reverse=True)

            # Retorna os N melhores documentos
            return [doc for doc, score in scored_docs[:top_n]]
        except Exception as e:
            logger.warning(f"Falha no reranking: {e}. Retornando ordem original.")
            return documents[:top_n]

    def _optimize_context(self, docs: List[Any]) -> str:
        if not docs:
            return "Nenhum documento relevante foi encontrado."
        parts = [f"[{doc.metadata.get('source', 'N/A')}]\n{doc.page_content.strip()}" for doc in docs]
        return "\n\n---\n\n".join(parts)

    def answer_query(self, query: str) -> Dict[str, Any]:
        start = time.time()
        
        # --- NOVA PIPELINE DE BUSCA ---
        # 1. Expansão da Query
        expanded_query = self._expand_query(query)
        if expanded_query != query:
            logger.info(f"Query expandida para: '{expanded_query}'")

        # 2. Busca Inicial (Recupera mais candidatos)
        logger.info(f"Buscando {config.retriever_candidates_k} candidatos...")
        candidate_docs = self.vectorstore.similarity_search(expanded_query, k=config.retriever_candidates_k)
        
        # 3. Reclassificação (Reranking)
        logger.info("Reclassificando documentos...")
        final_docs = self._rerank_docs(query, candidate_docs, top_n=config.final_docs_k)
        
        # --- FIM DA NOVA PIPELINE ---

        context = self._optimize_context(final_docs)

        if config.debug_mode:
            print("\n========== CONTEXTO ENVIADO AO LLM ==========\n")
            print(context)
            print("\n=============================================\n")

        prompt = PROMPT_TEMPLATE.format(context=context, question=query)

        try:
            response = self.llm.invoke(prompt)
            answer_text = response.content
        except Exception as e:
            logger.error(f"Erro ao chamar LLM: {e}")
            answer_text = "Erro ao gerar resposta."

        total_time = time.time() - start
        return {
            'result': answer_text,
            'source_documents': final_docs,
            'processing_time': total_time
        }

# --- Funções de interface ---
def get_system_components() -> RAGSystem:
    return RAGSystem.get_instance()

def process_message(message: str, conversation_id: Optional[str] = None, user: Optional[str] = None) -> str:
    """
    Processa a mensagem, aceitando parâmetros opcionais para compatibilidade com a API.
    """
    system = get_system_components()
    result = system.answer_query(message) # A lógica principal não muda
    return result.get("result", "Não foi possível gerar uma resposta.")
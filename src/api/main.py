import os

from fastapi import FastAPI
from pathlib import Path

from src.retrieval.bm25_index import PersistentBM25Index
from .routes.chat import router as chat_router
from .routes.retrievals import router as retrieval_router
from src.core.container import create_rag_pipeline, create_rag_pipeline_v2
from src.db.dao.SQLAlchemyChunkStore import SQLAlchemyChunkStore
from src.db.database import SessionLocal
from src.embeddings.SimpleEmbedding import SimpleEmbedding
from src.retrieval.faiss_store import FaissVectorStore
from ..retrieval.bm25_index import PersistentBM25Index
from ..retrieval.HybridRetriever import HybridRetriever
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
INDEX_PATH = DATA_DIR / "bm25_index.pkl"


def create_app() -> FastAPI:
    embedder = SimpleEmbedding()
    vector_store = FaissVectorStore.load(os.environ.get("VECTOR_DIR_FAISS"))
    chunk_store = SQLAlchemyChunkStore(SessionLocal)
    bm25_index = PersistentBM25Index.load(INDEX_PATH)

    app = FastAPI(
        title="Personal Journal Assistant",
    )

    app.state.embedder=embedder
    app.state.bm25_index=bm25_index
    app.state.vector_store = vector_store
    app.state.chunk_store = chunk_store
    app.state.hybrid_retriever = HybridRetriever(
        embedder=embedder,
        vector_store=vector_store,
        chunk_store=chunk_store,
        bm25_index=bm25_index,
        rrf_k=60,
    )

    app.state.rag_pipeline = create_rag_pipeline()
    app.state.rag_pipeline_v2 = create_rag_pipeline_v2()


    app.include_router(chat_router)
    app.include_router(retrieval_router)

    return app


app = create_app()

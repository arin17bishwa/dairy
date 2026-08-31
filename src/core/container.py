import os

from dotenv import load_dotenv

from src.context.SimpleContextBuilder import SimpleContextBuilder
from src.db.dao.SQLAlchemyChunkStore import SQLAlchemyChunkStore
from src.db.database import SessionLocal
from src.embeddings.SimpleEmbedding import SimpleEmbedding
from src.llm.ollama import OllamaLLM
from src.retrieval.PersistentRetriever import PersistentRetriever
from src.retrieval.RagPipeline import RagPipeline
from src.retrieval.faiss_store import FaissVectorStore

load_dotenv()


def create_rag_pipeline() -> RagPipeline:

    embedder = SimpleEmbedding()
    vector_store = FaissVectorStore.load(os.environ.get("VECTOR_DIR_FAISS"))
    chunk_store = SQLAlchemyChunkStore(SessionLocal)

    retriever = PersistentRetriever(
        embedder=embedder,
        vector_store=vector_store,
        chunk_store=chunk_store,
    )

    context_builder = SimpleContextBuilder()

    # llm = OllamaLLM(model="gemma4:31b-mlx")
    llm = OllamaLLM(model="qwen3:4b")

    return RagPipeline(retriever=retriever, context_builder=context_builder, llm=llm)

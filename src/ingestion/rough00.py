import os

from dotenv import load_dotenv

from src.db.dao.SQLAlchemyChunkStore import SQLAlchemyChunkStore
from src.db.database import get_db, SessionLocal
from src.embeddings.SimpleEmbedding import SimpleEmbedding
from src.ingestion.chunker.JournalChunker import JournalChunker
from src.ingestion.chunker.JournalChunkerV2 import JournalChunkerV2
from src.ingestion.ingestion_service import IngestionService
from src.ingestion.parser import JournalParser
from src.retrieval.faiss_store import FaissVectorStore

load_dotenv()


def main():
    parser = JournalParser()
    embedder = SimpleEmbedding()

    chunker = JournalChunkerV2(embedder)

    chunk_store = SQLAlchemyChunkStore(SessionLocal)
    # vector_store = FaissVectorStore.load(os.environ.get("VECTOR_DIR_FAISS"))

    vector_store=FaissVectorStore(embedder.get_model().get_embedding_dimension())

    ingestion_pipeline = IngestionService(
        parser=parser,
        chunker=chunker,
        embedder=embedder,
        chunk_store=chunk_store,
        vector_store=vector_store,
    )


    ingestion_pipeline.ingest()

    vector_store.save()



if __name__ == "__main__":
    main()

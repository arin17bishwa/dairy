from black import Sequence
from sentence_transformers import SentenceTransformer

from src.embeddings.SimpleEmbedding import SimpleEmbedding
from src.ingestion.models import Chunk
from src.retrieval.BaseRetriever import BaseRetriever
from src.retrieval.VectorStore import VectorStore


class SimpleRetriever(BaseRetriever):
    def __init__(
        self, embedder: SimpleEmbedding, vector_store: VectorStore, chunks: Sequence[Chunk]
    ):
        self.embedder = embedder
        self.vector_store = vector_store
        self.chunks = chunks

        self.chunk_mapping: dict[str, Chunk] = {chunk.id: chunk for chunk in chunks}

    def retrieve(self, query: str, k: int = 3) -> Sequence[dict]:
        q_embedding = self.embedder.get_embedding(query)

        results = self.vector_store.search([q_embedding], k=k)

        return [
            {"chunk": self.chunk_mapping.get(chunk_id), "score": score}
            for chunk_id, score in results
        ]

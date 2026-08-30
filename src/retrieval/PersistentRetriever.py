from typing import Sequence

from src.db.dao.interfaces.chunk_store import ChunkStore
from src.embeddings.SimpleEmbedding import SimpleEmbedding
from src.ingestion.models import Chunk
from src.retrieval.BaseRetriever import BaseRetriever
from src.retrieval.VectorStore import VectorStore


class PersistentRetriever(BaseRetriever):
    def __init__(
        self, embedder: SimpleEmbedding, vector_store: VectorStore, chunk_store:ChunkStore
    ):
        self.embedder=embedder
        self.vs=vector_store
        self.cs=chunk_store

    def retrieve(self, query: str, k: int = 3) -> Sequence[dict]:
        q_embedding=self.embedder.get_embeddings([query])

        results=self.vs.search(query_embeddings=q_embedding, k=k)

        chunk_ids=[chunk_id for chunk_id, _ in results]

        chunks=self.cs.get_many(chunk_ids)

        chunks_by_ids={chunk.id:chunk for chunk in chunks}

        return [
            {"chunk": chunks_by_ids.get(chunk_id), "score": score, 'chunk_id':chunk_id}
            for chunk_id, score in results
        ]

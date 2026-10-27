from collections import defaultdict
from typing import Sequence

from src.db.dao.interfaces.chunk_store import ChunkStore
from src.embeddings.SimpleEmbedding import SimpleEmbedding
from src.retrieval.BaseRetriever import BaseRetriever
from src.retrieval.VectorStore import VectorStore
from src.retrieval.bm25_index import PersistentBM25Index


class HybridRetriever(BaseRetriever):

    def __init__(
        self,
        embedder: SimpleEmbedding,
        vector_store: VectorStore,
        chunk_store: ChunkStore,
        bm25_index: PersistentBM25Index ,
        rrf_k: int = 60,
    ):
        self.embedder=embedder
        self.bm25_index = bm25_index
        self.vector_store = vector_store
        self.chunk_store=chunk_store
        self.rrf_k = rrf_k

    def search(
        self,
        query: str,
        top_k: int = 20,
        candidate_k: int = 50,
    ):

        # Retrieve candidates independently.
        keyword_results = self.bm25_index.search(
            query,
            top_k=candidate_k,
        )

        vector_results = self.vector_store.search(
            self.embedder.get_embeddings([query]),
            k=candidate_k,
        )

        # Each result is assumed to be:
        # (chunk_id, original_score)
        fused_scores = defaultdict(float)
        sources = defaultdict(set)

        for result_list, source in [
            (keyword_results, "bm25"),
            (vector_results, "vector"),
        ]:
            for rank, (chunk_id, _) in enumerate(
                result_list, start=1
            ):
                fused_scores[chunk_id] += (
                    1.0 / (self.rrf_k + rank)
                )
                sources[chunk_id].add(source)

        ranked = sorted(
            fused_scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        return [
            {
                "chunk_id": chunk_id,
                "score": score,
                "sources": sorted(sources[chunk_id]),
            }
            for chunk_id, score in ranked[:top_k]
        ]

    def retrieve(self, query: str, k: int = 3) -> Sequence[dict]:
        matches=self.search(query, top_k=k, candidate_k=20)
        chunk_ids=[match['chunk_id'] for match in matches]
        chunks=self.chunk_store.get_many(chunk_ids)
        chunks_by_ids={chunk.id:chunk for chunk in chunks}


        for match in matches:
            match['chunk']=chunks_by_ids.get(match['chunk_id'])

        print(matches)
        return matches
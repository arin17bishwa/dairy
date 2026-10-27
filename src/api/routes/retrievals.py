from typing import Optional

from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from src.db.models import ChunkModel
from src.retrieval.bm25_index import PersistentBM25Index
from src.db.database import get_db

router = APIRouter(prefix="/retrieval", tags=["Retrieval"])


@router.post('/bm25-search')
def keyword_search(request:Request, query: str, top_k: int = 100, populate_chunk:bool=False):
    index:PersistentBM25Index=request.app.state.bm25_index
    if not populate_chunk:
        return index.search(query, top_k=top_k)
    return [
        [i[0], i[1]]
        for i in index.search(query, top_k=top_k)
    ]


class HybridSearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=10, ge=1, le=100)
    candidate_k: int = Field(default=50, ge=1, le=500)


class HybridSearchResult(BaseModel):
    chunk_id: str | int
    score: float
    sources: list[str]
    text: Optional[str]


class HybridSearchResponse(BaseModel):
    query: str
    results: list[HybridSearchResult]


@router.post("/hybrid-search", response_model=HybridSearchResponse)
def hybrid_search(
    payload: HybridSearchRequest,
    request: Request,
):
    hybrid_retriever = request.app.state.hybrid_retriever
    chunk_store = request.app.state.chunk_store

    try:
        ranked_results = hybrid_retriever.search(
            query=payload.query,
            top_k=payload.top_k,
            candidate_k=payload.candidate_k,
        )

        chunk_ids = [result["chunk_id"] for result in ranked_results]
        chunks = chunk_store.get_many(chunk_ids)
        chunks_by_id = {chunk.id: chunk for chunk in chunks}

        results = [
            {
                **result,
                "text": chunks_by_id[result["chunk_id"]].text,
            }
            for result in ranked_results
            if result["chunk_id"] in chunks_by_id
        ]

        return {
            "query": payload.query,
            "results": results,
        }

    except Exception as exc:
        raise exc


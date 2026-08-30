
from fastapi import Request

from src.retrieval.RagPipeline import RagPipeline


def get_rag_pipeline(request: Request) -> RagPipeline:
    return request.app.state.rag_pipeline
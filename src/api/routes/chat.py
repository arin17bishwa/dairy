from fastapi import APIRouter, Depends

from src.api.dependencies import get_rag_pipeline
from src.api.schemas import ChatRequest, ChatResponse
from src.retrieval.RagPipeline import RagPipeline

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(
    body: ChatRequest,
    rag_pipeline: RagPipeline = Depends(get_rag_pipeline),
):

    return rag_pipeline.detailed_answer(body.query)

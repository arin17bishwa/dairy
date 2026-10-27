from fastapi import APIRouter, Depends

from src.api.dependencies import get_rag_pipeline,get_rag_pipeline_v2
from src.api.schemas import ChatRequest, ChatResponse
from src.retrieval.RagPipeline import RagPipeline

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(
    body: ChatRequest,
    rag_pipeline: RagPipeline = Depends(get_rag_pipeline),
):

    return rag_pipeline.detailed_answer(body.query)


@router.post("/chat/v2", response_model=ChatResponse)
def chat_v2(
    body: ChatRequest,
    rag_pipeline: RagPipeline = Depends(get_rag_pipeline_v2),
):
    return rag_pipeline.detailed_answer(body.query)
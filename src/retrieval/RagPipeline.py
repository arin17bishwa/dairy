from src.api.schemas import ChatResponse, Source
from src.context.SimpleContextBuilder import SimpleContextBuilder
from src.db.dao.interfaces.chunk_store import ChunkStore
from src.embeddings.SimpleEmbedding import SimpleEmbedding
from src.llm.llm import LLM
from src.retrieval.BaseRetriever import BaseRetriever
from src.retrieval.VectorStore import VectorStore


class RagPipeline:
    def __init__(
        self,
        llm: LLM,
        retriever: BaseRetriever,
        context_builder: SimpleContextBuilder,
    ):
        self.retriever = retriever
        self.context_builder = context_builder
        self.llm = llm


    def answer(self, query: str, k: int = 4) -> str:
        retrieval = self.retriever.retrieve(query, k)

        user_prompt = self.context_builder.get_user_prompt(
            retrievals=retrieval, query=query
        )
        system_prompt = self.context_builder.get_system_prompt()

        response = self.llm.generate(
            user_prompt=user_prompt, system_prompt=system_prompt
        )

        return response

    def detailed_answer(self, query: str, k: int = 4) -> ChatResponse:
        retrieval = self.retriever.retrieve(query, k)

        user_prompt = self.context_builder.get_user_prompt(
            retrievals=retrieval, query=query
        )
        system_prompt = self.context_builder.get_system_prompt()

        response = self.llm.generate(
            user_prompt=user_prompt, system_prompt=system_prompt
        )

        return ChatResponse(
            answer=response,
            sources=[
                Source(
                    chunk_id=chunk["chunk_id"],
                    score=chunk["score"],
                    chunk=chunk["chunk"].text,
                )
                for chunk in retrieval
            ],
        )

from abc import ABC

from typing import Sequence
from abc import ABC, abstractmethod
from src.embeddings.SimpleEmbedding import SimpleEmbedding
from src.ingestion.models import Chunk
from src.retrieval.VectorStore import VectorStore


class BaseRetriever(ABC):

    @abstractmethod
    def retrieve(self, query: str, k: int = 3) -> Sequence[dict]:
        pass


import os
from pathlib import Path
from typing import Iterable, Sequence

from src.ingestion.models import Chunk
from dotenv import load_dotenv
from abc import ABC, abstractmethod


import faiss

load_dotenv()

INDEX_FILE_PATH=''

class VectorStore(ABC):

    @abstractmethod
    def add(self, ids:Sequence[str], embeddings:Sequence[Sequence[float]], *args, **kwargs)->None:
        """Add vectors to the store."""
        pass

    @abstractmethod
    def search(self, query_embeddings:Sequence[float], k:int=5)->list[tuple[str,float]]:
        """Return (id, similarity_score) pairs."""
        pass

    @abstractmethod
    def save(self, path:str|Path|None=None)->None:
        """Persist the vector store."""
        pass

    @classmethod
    @abstractmethod
    def load(cls, path: str) -> "VectorStore":
        """Load a persisted vector store."""
        pass



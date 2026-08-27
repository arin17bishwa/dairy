import os
from typing import Any

from numpy import dtype, ndarray
import numpy as np
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from src.ingestion.utils.chunker_utils import get_journal_data
from src.ingestion.models import Chunk, Journal
import json

load_dotenv()

# model = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")
model = SentenceTransformer("BAAI/bge-small-en-v1.5")


def get_embeddings(entries: list[str]):
    return model.encode(entries)


def get_embedding(entry: str):
    return model.encode(entry)


def similarity(
    v1: ndarray[tuple[Any, ...], dtype[Any]], v2: ndarray[tuple[Any, ...], dtype[Any]]
) -> float:
    return v1.dot(v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


class SimpleEmbedding:
    def __init__(self, embedding_model_name:str=os.environ.get("EMBEDDING_MODEL_NAME")):
        if not embedding_model_name:
            raise ValueError(f"No valid embedding model name provided. Default value = \'{os.environ.get('EMBEDDING_MODEL_NAME')}/'")
        self.embedding_model_name:str=embedding_model_name
        self.model:SentenceTransformer=SentenceTransformer(self.embedding_model_name)

    def get_embeddings(self,entries: list[str]):
        return self.model.encode(entries)

    def get_embedding(self,entry: str):
        return self.model.encode(entry)

    def get_model(self):
        return self.model

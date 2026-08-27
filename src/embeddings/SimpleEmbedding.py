import os

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()


class SimpleEmbedding:
    def __init__(
        self, embedding_model_name: str = os.environ.get("EMBEDDING_MODEL_NAME")
    ):
        if not embedding_model_name:
            raise ValueError(
                f"No valid embedding model name provided. Default value = '{os.environ.get('EMBEDDING_MODEL_NAME')}/'"
            )
        self.embedding_model_name: str = embedding_model_name
        self.model: SentenceTransformer = SentenceTransformer(self.embedding_model_name)

    def get_embeddings(self, entries: list[str]):
        return self.model.encode(entries)

    def get_embedding(self, entry: str):
        return self.model.encode(entry)

    def get_model(self):
        return self.model

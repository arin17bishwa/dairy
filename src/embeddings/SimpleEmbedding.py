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

    def count_tokens(self, text: str) -> int:
        tokenizer = self.model.tokenizer
        return len(
            tokenizer(
                text,
                add_special_tokens=True,
                truncation=False,
                return_attention_mask=False,
                return_token_type_ids=False,
            )["input_ids"]
        )

    def get_embeddings(self, entries: list[str]):
        return self.model.encode(entries)

    def get_embedding(self, entry: str):
        return self.model.encode(entry)

    def get_model(self):
        return self.model

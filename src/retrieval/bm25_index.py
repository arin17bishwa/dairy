import os
import pickle
import re
import tempfile
from pathlib import Path
from typing import Any, Optional

import numpy as np
from rank_bm25 import BM25Okapi
from sqlalchemy import select

from src.db.models import ChunkModel

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"

DATA_DIR.mkdir(parents=True, exist_ok=True)

INDEX_VERSION = 1


def tokenize(text: str) -> list[str]:
    """Simple tokenizer."""
    return re.findall(r"\w+", text.lower(), flags=re.UNICODE)


class PersistentBM25Index:
    def __init__(self, bm25: BM25Okapi, chunk_ids: list[str]):
        self.bm25: BM25Okapi = bm25
        self.chunk_ids: list[str] = chunk_ids

    @classmethod
    def build(
        cls,
        session_factory: Any,
        chunk_model: Any,
        index_path: str | Path,
        batch_size: int = 1000,
    ):
        chunk_ids: list[str] = []
        tokenized_corpus: list[list[str]] = []

        stmt = select(chunk_model.id, chunk_model.text).execution_options(
            yield_per=batch_size
        )

        with session_factory() as session:
            result = session.execute(stmt)

            for chunk_id, text in result:
                chunk_ids.append(str(chunk_id))
                tokenized_corpus.append(tokenize(text or ""))

        if not tokenized_corpus:
            raise ValueError("Cannot build a BM25 index: no chunks found.")

        bm25 = BM25Okapi(tokenized_corpus)
        index = cls(bm25, chunk_ids)
        index.save(index_path)

        return index

    def save(self, index_path: Optional[str | Path] = None) -> None:
        if not index_path:
            index_path = DATA_DIR / "bm25_index.pkl"
        path = Path(index_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "version": INDEX_VERSION,
            "chunk_ids": self.chunk_ids,
            "bm25": self.bm25,
        }

        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=path.parent,
                prefix=f".{path.name}.",
                suffix=".tmp",
                delete=False,
            ) as file:
                temp_path = Path(file.name)
                pickle.dump(
                    payload,
                    file,
                    protocol=pickle.HIGHEST_PROTOCOL,
                )
            # write atomically, so an interrupted build won't corrupt the old file
            os.replace(temp_path, path)

        finally:
            if temp_path is not None and temp_path.exists():
                temp_path.unlink()

    @classmethod
    def load(
        cls,
        index_path: str | Path,
    ) -> "PersistentBM25Index":
        """Load an index previously built by this class."""
        with open(index_path, "rb") as file:
            payload = pickle.load(file)

        if payload.get("version") != INDEX_VERSION:
            raise ValueError("Unsupported BM25 index version. Rebuild the index.")

        return cls(
            bm25=payload["bm25"],
            chunk_ids=payload["chunk_ids"],
        )

    def search(
        self,
        query: str,
        top_k: int = 100,
    ) -> list[tuple[str, float]]:
        """Return (chunk_id, BM25 score), highest score first."""
        query_tokens = tokenize(query)

        if not query_tokens or top_k <= 0:
            return []

        scores = self.bm25.get_scores(query_tokens)

        k = min(top_k, len(self.chunk_ids))
        candidate_indices = np.argpartition(scores, -k)[-k:]
        ranked_indices = sorted(
            candidate_indices,
            key=lambda i: scores[i],
            reverse=True,
        )

        return [(self.chunk_ids[i], float(scores[i])) for i in ranked_indices]

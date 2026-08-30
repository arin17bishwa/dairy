import json
import os
from pathlib import Path

import faiss
import numpy as np
from black import Sequence

from .VectorStore import VectorStore


class FaissVectorStore(VectorStore):
    ID_FILE = "ids.json"
    INDEX_FILE = "journal.faiss"

    def __init__(self, dim: int):
        self.dimension: int = dim
        self.index = faiss.IndexFlatIP(dim)
        self.ids: list[str] = []

    def add(
        self, ids: Sequence[str], embeddings: Sequence[Sequence[float]], *args, **kwargs
    ) -> None:
        vectors = np.asarray(embeddings, dtype=np.float32)

        faiss.normalize_L2(vectors)

        self.index.add(vectors)

        self.ids.extend(ids)

    def search(
        self, query_embeddings: Sequence[float], k: int = 5
    ) -> list[tuple[str, float]]:
        query_vector = np.asarray(query_embeddings)

        faiss.normalize_L2(query_vector)

        scores, indices = self.index.search(x=query_vector, k=k)

        return [(self.ids[i], score) for score, i in zip(scores[0], indices[0]) if i != -1]

    def save(self, path: str=os.environ.get("VECTOR_DIR_FAISS")) -> None:
        if not isinstance(path, Path):
            path = Path(path)

        id_path = path / self.ID_FILE
        index_path = path / self.INDEX_FILE

        faiss.write_index(self.index, index_path.as_posix())

        with open(id_path, "w") as fp:
            json.dump(self.ids, fp, indent=4)

    @classmethod
    def load(cls, path: str) -> "VectorStore":

        path = Path(path)

        id_path = path / cls.ID_FILE
        index_path = path / cls.INDEX_FILE

        if id_path.exists():
            with open(id_path, "r") as fp:
                ids = json.load(fp)

        index = faiss.read_index(index_path.as_posix())

        store = cls(index.d)
        store.index = index
        store.ids = ids
        return store

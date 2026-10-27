from pathlib import Path

from src.db.database import SessionLocal
from src.db.models import ChunkModel
from src.retrieval.bm25_index import PersistentBM25Index

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
INDEX_PATH = DATA_DIR / "bm25_index.pkl"


if __name__ == "__main__":
    index = PersistentBM25Index.build(
        session_factory=SessionLocal,
        chunk_model=ChunkModel,
        index_path=INDEX_PATH,
        batch_size=1000,
    )

    print(f"Indexed {len(index.chunk_ids):,} existing chunks.")
    print(f"Saved index to: {INDEX_PATH}")

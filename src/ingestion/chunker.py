from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

from src.ingestion.chunker.JournalChunker import JournalChunker
from src.ingestion.utils.chunker_utils import get_journal_data
from src.ingestion.models import Chunk, Journal
import json

load_dotenv()

# model = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")
model = SentenceTransformer("BAAI/bge-small-en-v1.5")


def get_chunks(journal: Journal) -> list[Chunk]:
    journal_chunker=JournalChunker()
    chunks = [journal_chunker.chunk(entry) for entry in journal.entries]

    return chunks


def func():
    journal_chunker=JournalChunker()
    doc_chunks = [
        journal_chunker.chunk(entry) for entry in get_journal_data().entries
    ]
    docs = [entry.entry for entry in get_journal_data().entries]
    queries = ["how happy am i?"]

    doc_em = model.encode(docs)
    query_em = model.encode(queries)

    print(doc_em.shape)
    print(doc_chunks)


if __name__ == "__main__":
    func()
    del model

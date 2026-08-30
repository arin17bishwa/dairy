from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

from src.embeddings.SimpleEmbedding import SimpleEmbedding
from src.ingestion.chunker.JournalChunker import JournalChunker
from src.ingestion.chunker.JournalChunkerV2 import JournalChunkerV2
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
    embedder=SimpleEmbedding()
    journal_chunker=JournalChunkerV2(embedder)
    doc_chunks = [
        journal_chunker.chunk(entry) for entry in get_journal_data().entries
    ]
    docs = [entry.entry for entry in get_journal_data().entries]
    queries = ["how happy am i?"]

    doc_em = model.encode(docs)
    query_em = model.encode(queries)

    print(doc_em.shape)
    print(doc_chunks)


def func_v2():
    embedder = SimpleEmbedding()
    journal_chunker = JournalChunkerV2(embedder)

    chunks=journal_chunker.get_chunks(get_journal_data().entries)
    for chunk in chunks:
        if embedder.count_tokens(chunk.text)>500:
            print(embedder.count_tokens(chunk.text), chunk.text)

    # print(*chunks, sep='\n')

if __name__ == "__main__":
    func_v2()

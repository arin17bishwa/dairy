import os

import fastapi
from dotenv import load_dotenv
from src.embeddings.embedding_service import get_embeddings, get_embedding, similarity
from src.ingestion.chunker import get_chunks
from src.ingestion.models import Journal, JournalEntry, Chunk, ChunkMetadata
from src.ingestion.utils.chunker_utils import get_journal_data
from src.retrieval.faiss_store import FaissVectorStore
from src.embeddings.SimpleEmbedding import SimpleEmbedding

load_dotenv()

def main():
    query: str = "how horny am i?"
    docs = get_journal_data().entries

    query_em = get_embedding(query)

    mx_idx = 0
    mx_score = 0

    for idx, doc in enumerate(docs):
        v1 = get_embedding(doc.entry)

        score = similarity(v1, query_em)

        if score > mx_score:
            mx_score = score
            mx_idx = idx

        print(score, doc.date, doc.entry[:120])
        print("-" * 60)

    print("Question:", query)
    print("Top answer ->", docs[mx_idx].date)
    print(docs[mx_idx].entry.splitlines()[14:])


def faiss_init():
    docs = get_journal_data().entries
    docs_content=[doc.entry for doc in docs]

    embedder=SimpleEmbedding(embedding_model_name=os.environ.get('EMBEDDING_MODEL_NAME'))

    embeddings=embedder.get_embeddings(docs_content)

    vs=FaissVectorStore(embedder.get_model().get_embedding_dimension())

    vs.add(ids=[str(doc.date) for doc in docs], embeddings=embeddings)

    vs.save(os.environ.get('VECTOR_DIR_FAISS'))









def faiss_main():
    embedder=SimpleEmbedding(embedding_model_name=os.environ.get('EMBEDDING_MODEL_NAME'))
    vs=FaissVectorStore.load(os.environ.get('VECTOR_DIR_FAISS'))

    query: str = "how horny am i?"

    q_embedding=embedder.get_embedding(query)

    matches=vs.search([q_embedding], k=2)

    print(matches)

def ret_main():

    embedder=SimpleEmbedding(embedding_model_name=os.environ.get('EMBEDDING_MODEL_NAME'))
    vs=FaissVectorStore.load(os.environ.get('VECTOR_DIR_FAISS'))
    chunks=get_chunks()







if __name__ == "__main__":
    faiss_main()

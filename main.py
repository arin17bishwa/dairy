import json
import os

import fastapi
from dotenv import load_dotenv

from src.context.SimpleContextBuilder import SimpleContextBuilder
from src.db.dao.SQLAlchemyChunkStore import SQLAlchemyChunkStore
from src.db.database import SessionLocal
from src.embeddings.embedding_service import get_embeddings, get_embedding, similarity
from src.ingestion.chunker.JournalChunker import JournalChunker
from src.ingestion.models import Journal, JournalEntry, Chunk, ChunkMetadata
from src.ingestion.utils.chunker_utils import get_journal_data
from src.llm.ollama import OllamaLLM
from src.retrieval.PersistentRetriever import PersistentRetriever
from src.retrieval.SimpleRetrieverStore import SimpleRetriever
from src.retrieval.faiss_store import FaissVectorStore
from src.embeddings.SimpleEmbedding import SimpleEmbedding
from src.retrieval.SimpleRetrieverStore import SimpleRetriever

load_dotenv()

def main():
    query: str = "give me a happy memory in 100 words"
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
    chunker=JournalChunker()
    chunks=chunker.get_chunks(get_journal_data().entries)

    embedder=SimpleEmbedding(embedding_model_name=os.environ.get('EMBEDDING_MODEL_NAME'))

    embeddings=embedder.get_embeddings([chunk.text for chunk in chunks])

    vs=FaissVectorStore(embedder.get_model().get_embedding_dimension())

    vs.add(ids=[str(chunk.id) for chunk in chunks], embeddings=embeddings)

    vs.save(os.environ.get('VECTOR_DIR_FAISS'))


def faiss_main():
    embedder=SimpleEmbedding(embedding_model_name=os.environ.get('EMBEDDING_MODEL_NAME'))
    vs=FaissVectorStore.load(os.environ.get('VECTOR_DIR_FAISS'))

    query: str = "give me a happy memory in 100 words"

    q_embedding=embedder.get_embedding(query)

    matches=vs.search([q_embedding], k=2)

    print(matches)


def ret_main():
    chunker=JournalChunker()

    embedder=SimpleEmbedding(embedding_model_name=os.environ.get('EMBEDDING_MODEL_NAME'))
    vs=FaissVectorStore.load(os.environ.get('VECTOR_DIR_FAISS'))
    chunks=chunker.get_chunks(journal_entries=get_journal_data().entries)

    data_store=SimpleRetriever(embedder=embedder, vector_store=vs, chunks=chunks)

    query: str = "give me a happy memory in 100 words"

    res=data_store.retrieve(query=query)

def llm_00():

    chunker=JournalChunker()

    embedder=SimpleEmbedding(embedding_model_name=os.environ.get('EMBEDDING_MODEL_NAME'))
    vs=FaissVectorStore.load(os.environ.get('VECTOR_DIR_FAISS'))
    chunks=chunker.get_chunks(journal_entries=get_journal_data().entries)

    data_store=SimpleRetriever(embedder=embedder, vector_store=vs, chunks=chunks)

    query: str = "give me a happy memory in 100 words"

    res=data_store.retrieve(query=query, k=5)
    # print(res)


    context_builder=SimpleContextBuilder()
    user_prompt=context_builder.get_user_prompt(retrievals=res, query=query)

    print(user_prompt)

    llm=OllamaLLM(model='qwen3:4b')
    response=llm.generate(user_prompt=user_prompt, system_prompt=context_builder.get_system_prompt())

    print(response)


def llm_01():
    chunker=JournalChunker()
    embedder=SimpleEmbedding(embedding_model_name=os.environ.get('EMBEDDING_MODEL_NAME'))
    vs=FaissVectorStore.load(os.environ.get('VECTOR_DIR_FAISS'))
    cs=SQLAlchemyChunkStore(SessionLocal)

    query="tell me about the trekking dream"
    query="what do you think about my food habits?"

    retriever=PersistentRetriever(embedder, vs,cs)

    res=retriever.retrieve(query, k=5)

    context_builder=SimpleContextBuilder()
    user_prompt=context_builder.get_user_prompt(retrievals=res, query=query)

    # llm = OllamaLLM(model="qwen3:4b")
    # llm = OllamaLLM(model="gemma4:e2b-mlx")
    llm = OllamaLLM(model="gemma4:31b-mlx")

    response = llm.generate(
        user_prompt=user_prompt, system_prompt=context_builder.get_system_prompt()
    )

    print(response)

if __name__ == "__main__":
    llm_01()

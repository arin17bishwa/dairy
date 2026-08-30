import os

from src.db.dao.interfaces.chunk_store import ChunkStore
from src.embeddings.embedding_service import SimpleEmbedding
from src.ingestion.chunker.BaseChunker import Chunker
from src.ingestion.models import Chunk
from src.ingestion.parser import JournalParser
from src.retrieval.VectorStore import VectorStore


class IngestionService:
    def __init__(self,
                 parser:JournalParser, chunker:Chunker, embedder:SimpleEmbedding, chunk_store:ChunkStore, vector_store:VectorStore):
        self.parser=parser
        self.chunker=chunker
        self.embedder=embedder
        self.chunk_store=chunk_store
        self.vector_store=vector_store

    def ingest(self, source_content=None):
        if source_content is None:
            source_content=self.parser.get_content()

        entries=self.parser.parse(source_content).entries

        chunks=self.chunker.chunk_multiple(entries)

        embeddings=self.embedder.get_embeddings([chunk.text for chunk in chunks])

        new_chunks:list[Chunk]=[]

        for chunk, embedding in zip(chunks,embeddings):
            existing:Chunk|None=self.chunk_store.get(chunk.id)

            if existing is None:
                self.chunk_store.add(chunk)
                new_chunks.append(chunk)

            elif chunk.content_hash!=existing.content_hash:
                self.chunk_store.upsert(chunk)

            else:
                # nothing to do
                pass

        # rebuild vector store

        for chunks in self.chunk_store.iter_all():
            embeddings=self.embedder.get_embeddings([chunk.text for chunk in chunks])
            self.vector_store.add(
                ids=[chunk.id for chunk in chunks],
                embeddings=embeddings
            )

        self.vector_store.save()
import os
from typing import Iterator

from src.db.dao.WhatsAppChatStore import WhatsAppChatStore
from src.db.dao.WhatsAppMessageStore import WhatsAppMessageStore
from src.db.dao.interfaces.chunk_store import ChunkStore
from src.embeddings.SimpleEmbedding import SimpleEmbedding
from src.ingestion.chunker.BaseChunker import Chunker
from src.ingestion.chunker.WhatsAppChunker import WhatsAppChunker
from src.ingestion.models import Chunk, WhatsAppMessage
from src.ingestion.parser import JournalParser
from src.retrieval.VectorStore import VectorStore


class WhatsAppIngestionService:
    def __init__(self,
                 chunker:WhatsAppChunker, embedder:SimpleEmbedding, chunk_store:ChunkStore, vector_store:VectorStore, wp_chat_store:WhatsAppChatStore, wp_msg_store:WhatsAppMessageStore):
        self.chunker=chunker
        self.embedder=embedder
        self.chunk_store=chunk_store
        self.vector_store=vector_store
        self.wp_chat_store=wp_chat_store
        self.wp_msg_store=wp_msg_store

    def _ingest(self, messages:Iterator[WhatsAppMessage]):
        chat_chunks = self.chunker.chunk(messages)
        for chat_chunk in chat_chunks:
            existing: Chunk | None = self.chunk_store.get(chat_chunk.id)

            if existing is None:
                self.chunk_store.add(chat_chunk)

            elif chat_chunk.content_hash != existing.content_hash:
                self.chunk_store.upsert(chat_chunk)

            else:
                # nothing to do
                pass

    def ingest(self):
        self.chunk_store.delete_by_source('whatsapp')

        for wp_chat in self.wp_chat_store.iter_all():
            wp_chat_msgs=self.wp_msg_store.iter_by_chat(wp_chat.id)
            self._ingest(wp_chat_msgs)

        # rebuild vector store

        for chunks in self.chunk_store.iter_all(1000):
            embeddings=self.embedder.get_embeddings([chunk.text for chunk in chunks])
            self.vector_store.add(
                ids=[chunk.id for chunk in chunks],
                embeddings=embeddings
            )

        self.vector_store.save()

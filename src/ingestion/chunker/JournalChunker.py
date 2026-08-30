"""A class for creating chunks out of journal entries"""

from datetime import datetime, time

from black import Sequence
from sympy import jordan_cell

from src.ingestion.chunker.BaseChunker import Chunker
from src.ingestion.models import JournalEntry, Chunk, ChunkMetadata


class JournalChunker(Chunker):
    ID_PREFIX = "journal"
    SOURCE = "journal"

    # todo: make it return sequence of chunks
    def chunk(self, journal_entry: JournalEntry) -> Chunk:
        return Chunk.create(
            _id=self.create_id(journal_entry),
            source=self.SOURCE,
            start_timestamp=datetime.combine(journal_entry.date, time.min),
            end_timestamp=datetime.combine(journal_entry.date, time.max),
            text=journal_entry.entry,
            metadata={},
        )

    def get_chunks(self, journal_entries:Sequence[JournalEntry])->Sequence[Chunk]:
        chunks:list[Chunk]=[]

        for entry in journal_entries:
            entry_chunks=self.chunk(entry)
            chunks.extend([entry_chunks])

        return chunks

    @staticmethod
    def create_id( journal_entry: JournalEntry) -> str:
        return f"{JournalChunker.ID_PREFIX}_{str(journal_entry.date)}"

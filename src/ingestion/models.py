import datetime

from pydantic import BaseModel
from datetime import date


class JournalEntry(BaseModel):
    entry: str
    date: date


class Journal(BaseModel):
    processed_time: datetime.datetime = datetime.datetime.now()
    entries: list[JournalEntry]


class ChunkMetadata(BaseModel):
    date: date


class Chunk(BaseModel):
    id: str
    entry: str
    metadata: ChunkMetadata

    @classmethod
    def from_journal_entry(cls, journal_entry: JournalEntry) -> "Chunk":
        return cls(
            id=str(journal_entry.date),
            entry=journal_entry.entry,
            metadata=ChunkMetadata(date=journal_entry.date),
        )

import datetime
from datetime import date

from pydantic import BaseModel


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
    source: str
    start_timestamp: datetime.datetime
    end_timestamp: datetime.datetime
    text: str
    metadata: dict

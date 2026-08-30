import datetime
from dataclasses import field
from datetime import date
import hashlib

from pydantic import BaseModel, Field

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
    content_hash:str
    metadata: dict

    @classmethod
    def create(
        cls,
        *,
        _id: str,
        source: str,
        start_timestamp: datetime.datetime,
        end_timestamp: datetime.datetime,
        text: str,
        metadata: dict=None,
    ) -> "Chunk":
        if metadata is None:
            metadata=dict()
        return cls(
            id=_id,
            source=source,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            text=text,
            content_hash=hashlib.sha256(text.encode("utf-8")).hexdigest(),
            metadata=metadata,
        )


    def update_text(self, text:str):
        self.text=text
        self.content_hash = hashlib.sha256(self.text.encode("utf-8")).hexdigest()

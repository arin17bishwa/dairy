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
    entry_id: str
    chunk_index: int
    text: str
    start_timestamp: datetime.datetime
    end_timestamp: datetime.datetime
    content_hash: str
    metadata: dict

    @classmethod
    def create(
        cls,
        *,
        _id: str,
        source: str,
        entry_id: str,
        chunk_index: int,
        text: str,
        start_timestamp: datetime.datetime,
        end_timestamp: datetime.datetime,
        metadata: dict = None,
    ) -> "Chunk":
        if metadata is None:
            metadata = dict()
        return cls(
            id=_id,
            source=source,
            text=text,
            entry_id=entry_id,
            chunk_index=chunk_index,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            content_hash=hashlib.sha256(text.encode("utf-8")).hexdigest(),
            metadata=metadata,
        )

    def update_text(self, text: str):
        self.text = text
        self.content_hash = hashlib.sha256(self.text.encode("utf-8")).hexdigest()

class WhatsAppChat(BaseModel):
    id: str
    name: str| None # null for unsaved contacts
    is_group: bool
    participants: list[str]=Field(default_factory=list)


class WhatsAppMessage(BaseModel):
    id:str
    chat_id:str
    sender_id:str
    timestamp:float
    text:str|None=Field(default="<<message not available>>")
    from_me:bool
    reply_to:str|None
    quoted_text:str|None
    whatsapp_key_id:str

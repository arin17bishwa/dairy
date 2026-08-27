from abc import ABC, abstractmethod

from src.ingestion.models import JournalEntry, Chunk


class Chunker(ABC):
    @abstractmethod
    def chunk(self, entry:JournalEntry)->Chunk:
        pass

    def chunk_multiple(self, entries:list[JournalEntry])->list[Chunk]:
        return [self.chunk(entry) for entry in entries]
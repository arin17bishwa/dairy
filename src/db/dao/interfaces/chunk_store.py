from abc import ABC, abstractmethod

from sqlalchemy.orm import sessionmaker, Session


class ChunkStore(ABC):

    def __init__(self, session_factory: sessionmaker[Session]):
        self.session_factory = session_factory

    @abstractmethod
    def add(self, chunk):
        pass

    @abstractmethod
    def get(self, chunk_id: str):
        pass

    @abstractmethod
    def get_many(self, chunk_ids: list[str]):
        pass

    @abstractmethod
    def update(self, chunk):
        pass

    @abstractmethod
    def delete(self, chunk_id: str):
        pass

    @abstractmethod
    def upsert(self, chunk):
        pass

    @abstractmethod
    def iter_all(self, batch_size:int=10):
        pass

    @abstractmethod
    def delete_by_source(self, source:str):
        pass



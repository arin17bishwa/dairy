from sqlalchemy import delete

from src.db.dao.interfaces.chunk_store import ChunkStore
from src.db.models import ChunkModel
from src.ingestion.models import Chunk


class SQLAlchemyChunkStore(ChunkStore):

    def add(self, chunk: Chunk):
        with self.session_factory() as session:
            try:
                chunk_model = self.to_chunk_model(chunk)
                session.add(chunk_model)
                session.commit()
            except (Exception, KeyboardInterrupt) as e:
                # session.rollback()
                raise e

    def add_many(self, chunks):
        with self.session_factory() as session:
            try:
                for chunk in chunks:
                    chunk_model = self.to_chunk_model(chunk)
                    session.add(chunk_model)
                session.commit()
            except (Exception, KeyboardInterrupt) as e:
                # session.rollback()
                raise e

    def get(self, chunk_id: str) -> Chunk | None:
        with self.session_factory() as session:
            model: ChunkModel | None = session.get(ChunkModel, chunk_id)
            if model is None:
                return None
            return self.to_chunk(model)

    def get_many(self, chunk_ids: list[str]) -> list[Chunk | None]:
        return [self.get(chunk_id) for chunk_id in chunk_ids]

    def update(self, chunk: Chunk):
        with self.session_factory() as session:
            model: ChunkModel | None = session.get(ChunkModel, chunk.id)
            if model is None:
                return

            _ = self._update(model, chunk)

            session.commit()

    def delete(self, chunk_id: str):
        with self.session_factory() as session:
            model: ChunkModel | None = session.get(ChunkModel, chunk_id)
            if model is not None:
                session.delete(model)
                session.commit()

    def upsert(self, chunk: Chunk) -> Chunk:
        with self.session_factory() as session:
            model = session.merge(self.to_chunk_model(chunk))
            session.commit()
            return self.to_chunk(model)

    def iter_all(self, batch_size: int = 10):
        with self.session_factory() as session:
            offset = 0

            while True:
                models: list[ChunkModel] = (
                    session.query(ChunkModel).offset(offset).limit(batch_size).all()
                )
                if not models:
                    break

                yield [self.to_chunk(model) for model in models]
                offset += batch_size

    def delete_by_source(self, source:str):
        with self.session_factory() as session:
            stmt = delete(ChunkModel).where(ChunkModel.source == source)

            _ = session.execute(stmt)
            session.commit()

        return 1

    @staticmethod
    def _update(chunk_model: ChunkModel, chunk: Chunk) -> ChunkModel:
        chunk_model.source = chunk.source
        chunk_model.text = chunk.text
        chunk_model.meta = chunk.metadata
        chunk_model.content_hash = chunk.content_hash

        return chunk_model

    @classmethod
    def to_chunk(cls, chunk_model: ChunkModel) -> Chunk:
        return Chunk(
            id=chunk_model.id,
            source=chunk_model.source,
            entry_id=chunk_model.entry_id,
            chunk_index=chunk_model.chunk_index,
            text=chunk_model.text,
            start_timestamp=chunk_model.start_timestamp,
            end_timestamp=chunk_model.end_timestamp,
            content_hash=chunk_model.content_hash,
            metadata=chunk_model.meta,
        )

    @classmethod
    def to_chunk_model(cls, chunk: Chunk) -> ChunkModel:
        return ChunkModel(
            id=chunk.id,
            source=chunk.source,
            entry_id=chunk.entry_id,
            chunk_index=chunk.chunk_index,
            text=chunk.text,
            start_timestamp=chunk.start_timestamp,
            end_timestamp=chunk.end_timestamp,
            content_hash=chunk.content_hash,
            meta=chunk.metadata,
        )

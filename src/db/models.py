from datetime import datetime, timezone

from sqlalchemy import String, DateTime, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ChunkModel(Base):
    __tablename__ = "chunks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    source: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    start_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    end_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    meta: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

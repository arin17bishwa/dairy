from datetime import datetime, timezone

from sqlalchemy import (
    String,
    DateTime,
    JSON,
    Text,
    UniqueConstraint,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ChunkModel(Base):
    __tablename__ = "chunks"

    __table_args__ = (
        UniqueConstraint(
            "source",
            "entry_id",
            "chunk_index",
            name="uq_chunk_position",
        ),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    source: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    entry_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    chunk_index: Mapped[int] = mapped_column(nullable=False)

    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    start_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    end_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

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


class WhatsAppChatModel(Base):
    __tablename__ = "whatsapp_chats"

    id: Mapped[str] = mapped_column(
        String(128),
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=True, # contacts I haven't saved have no name often
    )

    is_group: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

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

    messages: Mapped[list["WhatsAppMessageModel"]] = relationship(
        back_populates="chat",
        cascade="all, delete-orphan",
    )


class WhatsAppMessageModel(Base):
    __tablename__ = "whatsapp_messages"

    id: Mapped[str] = mapped_column(
        String(128),
        primary_key=True,
    )

    chat_id: Mapped[str] = mapped_column(
        ForeignKey("whatsapp_chats.id"),
        nullable=False,
        index=True,
    )

    sender_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        index=True,
    )

    timestamp: Mapped[float] = mapped_column(
        nullable=False,
        index=True,
    )

    datetime:Mapped[float]=mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )

    text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    from_me: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    reply_to: Mapped[str | None] = mapped_column(
        ForeignKey("whatsapp_messages.id"),
        nullable=True,
        index=True,
    )

    # Text quoted by WhatsApp in the reply.
    quoted_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # original WhatsApp KEY_ID; need to explore if we can replace the chat ID with this
    whatsapp_key_id: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

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

    chat: Mapped["WhatsAppChatModel"] = relationship(
        back_populates="messages",
    )

    reply_to_message: Mapped["WhatsAppMessageModel | None"] = relationship(
        remote_side="WhatsAppMessageModel.id",
        foreign_keys=[reply_to],
    )

    __table_args__ = (
        UniqueConstraint(
            "chat_id",
            "whatsapp_key_id",
            name="uq_whatsapp_message_chat_key",
        ),
    )

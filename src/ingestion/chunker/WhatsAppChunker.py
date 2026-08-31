from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import datetime

from typing_extensions import SupportsInt

from src.ingestion.chunker.BaseChunker import Chunker
from src.ingestion.models import Chunk, WhatsAppMessage, JournalEntry


class WhatsAppChunker(Chunker):
    """
    Groups WhatsApp messages into retrieval-friendly conversational chunks.

    A new chunk is started when:
      1. The inactivity gap exceeds max_gap_seconds, or
      2. Adding the next message would exceed max_tokens.

    Messages are expected to be ordered chronologically and to belong
    to the same WhatsApp chat.
    """

    def __init__(
        self,
        token_counter,
        max_tokens: int = 500,
        max_gap_seconds: int = 2 * 60 * 60,
    ):
        self.token_counter = token_counter
        self.max_tokens = max_tokens
        self.max_gap_seconds = max_gap_seconds
        self.chunk_idx:Iterator[int]=iter(range(10**9))

    def _get_chunk_index(self)->int:
        return next(self.chunk_idx)

    def chunk(
        self,
        messages: Iterable[WhatsAppMessage],
    ) -> Iterator[Chunk]:
        current_messages: list[WhatsAppMessage] = []
        current_tokens = 0
        self.chunk_idx=iter(range(10**9))

        previous_message: WhatsAppMessage | None = None

        for message in messages:
            if not self._is_chunk_compatible(
                current_messages,
                previous_message,
                message,
            ):
                if current_messages:
                    yield self._build_chunk(current_messages)

                current_messages = []
                current_tokens = 0

            message_text = self._format_message(message)
            message_tokens = self.token_counter(message_text)

            # A single oversized message gets its own chunk for now.
            if (
                current_messages
                and current_tokens + message_tokens > self.max_tokens
            ):
                yield self._build_chunk(current_messages)

                current_messages = []
                current_tokens = 0

            current_messages.append(message)
            current_tokens += message_tokens

            previous_message = message

        if current_messages:
            yield self._build_chunk(current_messages)

    def _is_chunk_compatible(
        self,
        current_messages: list[WhatsAppMessage],
        previous_message: WhatsAppMessage | None,
        message: WhatsAppMessage,
    ) -> bool:
        if not current_messages:
            return True

        if previous_message is None:
            return True

        gap = message.timestamp - previous_message.timestamp

        return gap <= self.max_gap_seconds

    def _format_message(self, message: WhatsAppMessage) -> str:
        timestamp = datetime.fromtimestamp(
            message.timestamp
        ).strftime("%Y-%m-%d %H:%M")

        sender = message.sender_id

        text = message.text or "[non-text message]"

        return f"[{timestamp}] {sender}: {text}"

    def _build_chunk(
        self,
        messages: list[WhatsAppMessage],
    ) -> Chunk:
        text = "\n".join(
            self._format_message(message)
            for message in messages
        )

        return Chunk.create(
            _id=self._build_chunk_id(messages),
            source="whatsapp",
            entry_id=self._build_chunk_id(messages),
            chunk_index=self._get_chunk_index(),
            text=text,
            start_timestamp=datetime.fromtimestamp(messages[0].timestamp),
            end_timestamp=datetime.fromtimestamp(messages[-1].timestamp),
            metadata={
                "chat_id": messages[0].chat_id,
                "message_ids": [message.id for message in messages],
                "message_count": len(messages),
            },
        )

    def _build_chunk_id(
        self,
        messages: list[WhatsAppMessage],
    ) -> str:
        return (
            f"whatsapp:"
            f"{messages[0].chat_id}:"
            f"{messages[0].id}:"
            f"{messages[-1].id}"
        )

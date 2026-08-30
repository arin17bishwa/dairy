import re
from datetime import datetime, time
from typing import Sequence

from src.embeddings.SimpleEmbedding import SimpleEmbedding
from src.ingestion.chunker.BaseChunker import Chunker
from src.ingestion.models import JournalEntry, Chunk


class JournalChunkerV2(Chunker):
    ID_PREFIX = "journal"
    SOURCE = "journal"

    MIN_CHUNK_TOKENS: int = 100
    TARGET_CHUNK_TOKENS: int = 350
    MAX_CHUNK_TOKENS: int = 500

    def __init__(self, embedder: SimpleEmbedding):
        super().__init__()
        self.embedder = embedder
        self.tokenizer = embedder.model.tokenizer

    def chunk(self, journal_entry: JournalEntry) -> Sequence[Chunk]:
        entry_id = self.create_id(journal_entry)

        pieces: list[str] = []

        for paragraph in self._split_paragraphs(journal_entry.entry):
            if self.embedder.count_tokens(paragraph) <= self.MAX_CHUNK_TOKENS:
                pieces.append(paragraph)
            else:
                pieces.extend(self._split_large_paragraph(paragraph))

        chunked_texts = self._pack_pieces(pieces)

        chunks: list[Chunk] = []

        for chunk_index, text in enumerate(chunked_texts):
            chunk_id = f"{entry_id}_{chunk_index:03d}"

            chunks.append(
                Chunk.create(
                    _id=chunk_id,
                    source=self.SOURCE,
                    entry_id=entry_id,
                    chunk_index=chunk_index,
                    text=text,
                    start_timestamp=datetime.combine(journal_entry.date, time.min),
                    end_timestamp=datetime.combine(journal_entry.date, time.max),
                    metadata={
                        "date": journal_entry.date.isoformat(),
                    },
                )
            )

        return chunks

    def get_chunks(self, journal_entries: Sequence[JournalEntry]) -> Sequence[Chunk]:
        chunks: list[Chunk] = []

        for entry in journal_entries:
            entry_chunks = self.chunk(entry)
            chunks.extend(entry_chunks)

        return chunks

    def chunk_multiple(self, entries: list[JournalEntry]) -> list[Chunk]:
        return list(self.get_chunks(entries))

    @staticmethod
    def create_id(journal_entry: JournalEntry) -> str:
        return f"{JournalChunkerV2.ID_PREFIX}_{str(journal_entry.date)}"

    @staticmethod
    def _split_paragraphs(text: str) -> list[str]:
        return [
            paragraph.strip()
            for paragraph in re.split(r"\n\s*\n", text)
            if paragraph.strip()
        ]

    def _split_large_paragraph(self, paragraph: str) -> list[str]:

        sentences = self._split_sentences(paragraph)

        if len(sentences) == 1:
            return self._hard_split(paragraph, self.MAX_CHUNK_TOKENS)

        pieces: list[str] = []
        current: list[str] = []
        current_tokens = 0

        for sentence in sentences:
            sentence_tokens = self.embedder.count_tokens(sentence)

            # single sentence is itself too large.
            if sentence_tokens > self.MAX_CHUNK_TOKENS:
                if current:
                    pieces.append(" ".join(current))
                    current = []
                    current_tokens = 0

                pieces.extend(
                    self._hard_split(
                        sentence,
                        self.MAX_CHUNK_TOKENS,
                    )
                )
                continue

            # adding this sentence would exceed max_tokens.
            if current and current_tokens + sentence_tokens > self.MAX_CHUNK_TOKENS:
                pieces.append(" ".join(current))
                current = []
                current_tokens = 0

            current.append(sentence)
            current_tokens += sentence_tokens

        if current:
            pieces.append(" ".join(current))

        return pieces

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        sentences = re.split(
            r"(?<=[.!?])\s+",
            text.strip(),
        )

        return [sentence.strip() for sentence in sentences if sentence.strip()]

    def _hard_split(self, text: str, max_tokens: int) -> list[str]:
        token_ids = self.tokenizer.encode(text, add_special_tokens=False)

        pieces: list[str] = []

        for i in range(0, len(token_ids), max_tokens):
            piece_ids = token_ids[i : i + max_tokens]

            piece = self.tokenizer.decode(piece_ids, skip_special_tokens=True).strip()

            if piece:
                pieces.append(piece)

        return pieces

    def _pack_pieces(self, pieces: list[str]) -> list[str]:

        chunks: list[str] = []

        current: list[str] = []
        current_tokens = 0

        for piece in pieces:
            piece_tokens = self.embedder.count_tokens(piece)

            if not current:
                current.append(piece)
                current_tokens = piece_tokens
                continue

            # If adding the piece stays within the maximum,
            # decide whether we should add it.
            combined_tokens = current_tokens + piece_tokens

            if combined_tokens <= self.MAX_CHUNK_TOKENS:
                current.append(piece)
                current_tokens = combined_tokens

                if current_tokens >= self.TARGET_CHUNK_TOKENS:
                    chunks.append("\n\n".join(current))
                    current = []
                    current_tokens = 0

            else:
                # Current chunk is full enough; start another.
                chunks.append("\n\n".join(current))

                current = [piece]
                current_tokens = piece_tokens

        if current:
            chunks.append("\n\n".join(current))

        return chunks

from collections.abc import Iterable, Iterator

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from src.db.models import WhatsAppChatModel
from src.ingestion.models import WhatsAppChat


class WhatsAppChatStore:

    def __init__(self, session_factory: sessionmaker[Session]):
        self.session_factory=session_factory

    def add(self, chat: WhatsAppChat) -> None:
        with self.session_factory() as session:
            session.add(
                self._to_model(chat)
            )

    def add_many(
        self,
        chats: Iterable[WhatsAppChat],
    ) -> None:
        with self.session_factory() as session:

            session.add_all(
                self._to_model(chat)
                for chat in chats
            )

    def get(
        self,
        chat_id: str,
    ) -> WhatsAppChat | None:
        with self.session_factory() as session:


            model:WhatsAppChatModel|None = session.get(
                WhatsAppChatModel,
                chat_id,
            )

            if model is None:
                return None

            return self._to_domain(model)

    def iter_all(self) -> Iterator[WhatsAppChat]:
        with self.session_factory() as session:

            stmt = (
                select(WhatsAppChatModel)
                .order_by(WhatsAppChatModel.id)
            )

            result = session.scalars(stmt)

            for model in result:
                yield self._to_domain(model)

    def delete(self, chat_id: str) -> None:
        with self.session_factory() as session:

            model = session.get(
                WhatsAppChatModel,
                chat_id,
            )

            if model is not None:
                session.delete(model)

    def _to_model(
        self,
        chat: WhatsAppChat,
    ) -> WhatsAppChatModel:

        return WhatsAppChatModel(
            id=chat.id,
            name=chat.name,
            is_group=chat.is_group,
            participants=chat.participants,
        )

    def _to_domain(
        self,
        model: WhatsAppChatModel,
    ) -> WhatsAppChat:

        return WhatsAppChat(
            id=model.id,
            name=model.name,
            is_group=model.is_group,
            participants=[],
        )
from collections.abc import Iterable, Iterator

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from src.db.models import WhatsAppMessageModel
from src.ingestion.models import WhatsAppMessage


class WhatsAppMessageStore:

    def __init__(self, session_factory:sessionmaker[Session]):
        self.session_factory=session_factory

    def add(self, message: WhatsAppMessage) -> None:
        with self.session_factory() as session:

            model = self._to_model(message)

            session.add(model)
            session.commit()

    def add_many(
        self,
        messages: Iterable[WhatsAppMessage],
    ) -> None:
        with self.session_factory() as session:

            models = [
                self._to_model(message)
                for message in messages
            ]

            session.add_all(models)
            session.commit()

    def get(self, message_id: str) -> WhatsAppMessage | None:
        with self.session_factory() as session:

            model:WhatsAppMessageModel|None = session.get(
                WhatsAppMessageModel,
                message_id,
            )

            if model is None:
                return None

            return self._to_domain(model)

    def iter_by_chat(
        self,
        chat_id: str,
    ) -> Iterator[WhatsAppMessage]:
        with self.session_factory() as session:

            stmt = (
                select(WhatsAppMessageModel)
                .where(
                    WhatsAppMessageModel.chat_id == chat_id
                )
                .order_by(
                    WhatsAppMessageModel.timestamp
                )
            )

            result = session.scalars(stmt)

            for model in result:
                yield self._to_domain(model)

    def delete_by_chat(self, chat_id: str) -> None:
        with self.session_factory() as session:

            stmt = (
                select(WhatsAppMessageModel)
                .where(
                    WhatsAppMessageModel.chat_id == chat_id
                )
            )

            models = session.scalars(stmt).all()

            for model in models:
                session.delete(model)

            session.commit()

    def _to_model(
        self,
        message: WhatsAppMessage,
    ) -> WhatsAppMessageModel:

        return WhatsAppMessageModel(
            id=message.id,
            chat_id=message.chat_id,
            sender_id=message.sender_id,
            timestamp=message.timestamp,
            text=message.text,
            from_me=message.from_me,
            reply_to=message.reply_to,
            quoted_text=message.quoted_text,
            whatsapp_key_id=message.whatsapp_key_id,
        )

    def _to_domain(
        self,
        model: WhatsAppMessageModel,
    ) -> WhatsAppMessage:

        return WhatsAppMessage(
            id=model.id,
            chat_id=model.chat_id,
            sender_id=model.sender_id or model.chat_id,
            timestamp=model.timestamp,
            text=model.text,
            from_me=model.from_me,
            reply_to=model.reply_to,
            quoted_text=model.quoted_text,
            whatsapp_key_id=model.whatsapp_key_id,
        )
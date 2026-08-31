import json
import os
from pathlib import Path
from datetime import datetime


from src.db.database import SessionLocal
from src.db.models import WhatsAppChatModel, WhatsAppMessageModel

STANDARD_PLACEHOLDER_MESSAGES: tuple[str, ...] = ("The media is missing",)


def process_chat(chat: dict[str, dict]) -> WhatsAppChatModel | None:
    def _get_final_chat_id(s: str) -> str:
        return s[: s.rindex("@")]

    def _is_group(s: str) -> bool:
        return s[s.rindex("@") + 1] == "g"

    _chat_id = list(chat.keys())[0]

    # filter out some chats
    if "@" not in _chat_id or _chat_id.endswith("broadcast"):
        return None

    chat_id = _get_final_chat_id(_chat_id)
    is_group = _is_group(_chat_id)

    chat_details: dict[str, str | dict] = chat[_chat_id]

    name: str = chat_details["name"]

    chat_model = WhatsAppChatModel(id=chat_id, name=name, is_group=is_group)
    return chat_model


def process_messages(
    chat: dict[str, dict], chat_model: WhatsAppChatModel
) -> list[WhatsAppMessageModel]:
    messages: dict[str, dict] = chat[list(chat.keys())[0]]["messages"]

    key_id_to_msg_id_mapping: dict[str, str] = {}
    msg_id_to_data_mapping: dict[str, str] = {}

    final_messages: list[WhatsAppMessageModel] = []

    for msg_id, msg in messages.items():
        if msg["message_type"] in (7,90):
            continue

        key_id = msg["key_id"]

        key_id_to_msg_id_mapping[key_id] = msg_id

        from_me = msg["from_me"]
        sender_id: str | None = "ME" if from_me else msg["sender"]
        msg_dttm: datetime = datetime.fromtimestamp(msg["timestamp"])

        msg_content = msg["data"]
        if msg_content in STANDARD_PLACEHOLDER_MESSAGES:
            msg_content = f"<<{msg_content}>>"

        msg_id_to_data_mapping[msg_id] = msg_content

        reply_to = key_id_to_msg_id_mapping[key_id]

        msg_model = WhatsAppMessageModel(
            id=msg_id,
            chat_id=chat_model.id,
            sender_id=sender_id,
            timestamp=msg["timestamp"],
            datetime=msg_dttm,
            text=msg_content,
            from_me=from_me,
            reply_to=reply_to,
            quoted_text=msg["quoted_data"],
            whatsapp_key_id=key_id,
        )

        final_messages.append(msg_model)

    return final_messages


def main():
    json_dir = Path("/Users/bishwajit/PycharmProjects/dairy/data/wp/jsons")

    session_factory = SessionLocal

    with session_factory() as session:
        for filename in list(os.walk(json_dir))[0][2]:
            path = json_dir / filename
            with open(path, encoding="utf-8") as fp:
                js = json.load(fp)
                chat = process_chat(js)
                if chat is None:
                    continue
                elif not session.get(WhatsAppChatModel, chat.id):
                    session.add(chat)
                messages = process_messages(js, chat)
                for msg in messages:
                    session.add(msg)
                session.commit()

        session.commit()


if __name__ == "__main__":
    main()

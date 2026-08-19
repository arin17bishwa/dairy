import datetime
import json
import os
from typing import Any

from dotenv import load_dotenv

from src.ingestion.models import Journal, JournalEntry

load_dotenv()


def get_parsed_data() -> dict:
    with open(os.path.join(os.environ.get("PARSED_DATA_DIR"), "journal00.json")) as fp:
        js = json.load(fp)
        return js


def get_journal_data() -> Journal:
    parsed_data = get_parsed_data()
    entries = [
        JournalEntry(
            entry=entry["entry"],
            date=datetime.datetime.strptime(entry["date"], "%Y-%m-%d").date(),
        )
        for entry in parsed_data["entries"]
    ]

    return Journal(entries=entries)

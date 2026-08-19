import json
import os

from dotenv import load_dotenv
from pathlib import Path
from utils.date_utils import get_extended_month_names, DATE_STRING_PATTERN
from models import JournalEntry, Journal
from datetime import date

load_dotenv()

JOURNAL_START_MARKER: str = "The beginnings…."


def get_file_path() -> Path:
    src_dir = Path(os.environ.get("SOURCE_TEXT_DATA_DIR"))
    src_filename = Path(os.environ.get("SOURCE_TEXT_DATA_FILENAME"))

    if not src_dir or not src_filename:
        raise ValueError("Source file path not provided.")

    src_file = src_dir.joinpath(src_filename)
    return src_file


def parse_input(entry: str) -> Journal:
    final_output: list[JournalEntry] = []
    current_lines: list[str] = []
    current_date: date | None = None

    # create an iterator over the lines
    line_iter = iter(entry.splitlines())
    line = next(line_iter)
    # skip over to the Journal start marker
    while line.strip() != JOURNAL_START_MARKER:
        line = next(line_iter)

    for line in entry.splitlines():
        # skip over month markers
        if line.strip().lower() in get_extended_month_names():
            continue

        # if found a new date,
        elif DATE_STRING_PATTERN.match(line):
            if current_date and current_lines:
                final_output.append(
                    JournalEntry(date=current_date, entry="\n".join(current_lines))
                )

            new_date_str: str = line.strip()
            current_date: date = date(
                year=int(new_date_str[:4]),
                month=int(new_date_str[4:6]),
                day=int(new_date_str[6:]),
            )
            current_lines.clear()
        else:
            current_lines.append(line)

    if current_lines:
        final_output.append(
            JournalEntry(date=current_date, entry="\n".join(current_lines))
        )

    return Journal(entries=final_output)


def read_input() -> str:
    src_file = get_file_path()

    try:
        with open(src_file) as fp:
            x = fp.read()
    except (FileExistsError, FileNotFoundError) as e:
        print("file not found")
        raise e

    return x


def func():
    inp = read_input()

    out = parse_input(inp)

    with open(
        os.path.join(os.environ.get("PARSED_DATA_DIR"), "journal00.json"), "w"
    ) as fp:
        fp.write(out.model_dump_json(indent=4))


if __name__ == "__main__":
    func()

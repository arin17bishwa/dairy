import datetime
import re

MONTH_NAMES: list[str] = [
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
]

DATE_STRING_PATTERN = re.compile(r"^20\d{2}\d{4}$")


def get_extended_month_names() -> list[str]:
    month_names = MONTH_NAMES
    return month_names + [i[:3] for i in month_names]

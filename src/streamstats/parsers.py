import csv
import json
import logging
from _collections_abc import Iterator
from os import PathLike

from streamstats.errors import IncorrectFormat, InvalidEvent, InvalidTimestamp
from streamstats.models import Event, validate_event

logger = logging.getLogger(__name__)


def parse_jsonl(doc: str | PathLike[str], skip_invalid: bool = False, counter=None) -> Iterator[Event]:
    """Reads the jsonl file and passes the value to line by line -> event
    and validation of broken strings, processing skip-invalid  """

    with open(doc, "r", encoding="utf-8") as file:
        for num, line in enumerate(file, start=1):
            try:
                data = json.loads(line)
                event = validate_event(data)
            except (json.JSONDecodeError, InvalidTimestamp, InvalidEvent) as exc:
                if not skip_invalid:
                    raise InvalidEvent(f"{doc} , line {num}: {exc}") from exc
                logger.warning("%s , line %s skipped", doc, num)
                if counter is not None:
                    counter["skipped"] += 1
                continue
            yield event


def parse_csv(doc: str | PathLike[str], skip_invalid: bool = False, counter=None):
    """Reads the csv file and passes the value to line by line -> event
        and validation of broken strings , processing skip-invalid """

    with open(doc, "r", newline="", encoding="utf-8") as file:
        files = csv.DictReader(file)
        for line in files:
            num = files.reader.line_num
            try:
                event = validate_event(line)
            except (InvalidTimestamp, InvalidEvent) as exc:
                if not skip_invalid:
                    raise InvalidEvent(f"{doc} , line {num}: {exc}") from exc
                logger.warning("%s , line %s skipped", doc, num)
                if counter is not None:
                    counter["skipped"] += 1
                continue
            yield event

def format_check(format: str):
    if format == "jsonl":
        return parse_jsonl
    if format == "csv":
        return parse_csv
    raise IncorrectFormat(f"file format is incorrect: {format}")

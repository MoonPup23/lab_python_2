from enum import Enum
from typing import Any

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, ValidationError

from streamstats.errors import InvalidEvent, InvalidTimestamp


class Level(Enum):
    """acceptable levels"""

    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    ERROR = "ERROR"
    INFO = "INFO"
    DEBUG = "DEBUG"

class Event(BaseModel):
    """Set data types"""

    model_config = ConfigDict(str_strip_whitespace=True)

    timestamp: AwareDatetime
    level: Level
    source: str = Field(min_length=1)
    message: str


def validate_event(event: dict[str, Any]) -> Event:
    """Validates data by pydantic, create Event ,
    raise IncorrectTimestamp/IncorrectEvent """

    try:
        return Event.model_validate(event)
    except ValidationError as exc:
        loc = [error["loc"] for error in exc.errors()]
        if ("timestamp",) in loc:
            raise InvalidTimestamp(f"Incorrect timestamp: {exc}") from exc
        raise InvalidEvent(f"Incorrect event: {exc}") from exc

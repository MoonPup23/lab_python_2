import itertools
from _collections_abc import Iterator
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime

from streamstats.models import Event, Level


@dataclass
class Stats:
    """File statistics and their types"""

    total: int = 0
    levels: Counter = field(default_factory=Counter)
    source: Counter = field(default_factory=Counter)
    errors_source: Counter = field(default_factory=Counter)
    first_time: datetime | None = None
    last_time: datetime | None = None
    counter: int = 0


def analyze(*events: Iterator[Event]) -> Stats:
    """Event analytics, time and level counting, create Event statistic"""

    stats = Stats()
    combined = itertools.chain(*events)
    for event in combined:
        stats.total += 1
        stats.levels[event.level.value] += 1
        stats.source[event.source] += 1

        if event.level in (Level.CRITICAL , Level.ERROR):
            stats.errors_source[event.source] += 1

        if stats.first_time is None or event.timestamp < stats.first_time:
            stats.first_time = event.timestamp

        if stats.last_time is None or event.timestamp > stats.last_time:
            stats.last_time = event.timestamp

    return stats

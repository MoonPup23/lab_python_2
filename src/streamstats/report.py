import json
from pathlib import Path
from typing import Any

from streamstats.analysis import Stats


def final_construction(stats:Stats) -> dict[str,Any]:
    """Compiles a dictionary from statistics for a JSON report.
    Error sources are limited to the top 5, and time convert to string"""

    pairing = []
    for name, value in stats.errors_source.most_common(5):
        pairing.append({"source": name, "value": value})

    new_first_time = stats.first_time.isoformat() if stats.first_time else None
    new_last_time = stats.last_time.isoformat() if stats.last_time else None

    return {"total": stats.total,
            "levels": stats.levels,
            "source": stats.source,
            "errors_source": pairing,
            "first_time": new_first_time,
            "last_time": new_last_time,
            "counter": stats.counter
            }


def write_json(stats: Stats, path: Path) -> None:
    """Creating a JSON file from the received event"""

    file = final_construction(stats)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(file, f, ensure_ascii=False, indent=2)

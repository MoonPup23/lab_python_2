import json
from pathlib import Path
from typing import Annotated

import typer

from streamstats import analysis, parsers, report
from streamstats.errors import StreamStatsError

app = typer.Typer()


@app.callback()
def main() -> None:
    """file analyze"""


@app.command()
def analyze(
        inputs: Annotated[list[Path], typer.Argument(exists=True, dir_okay=False, readable=True)],
        formats: Annotated[str, typer.Option("--format", help="format file: jsonl or csv")],
        output: Annotated[Path | None, typer.Option("--output", help="The place to write the report")] = None,
        skip_invalid: Annotated[
            bool, typer.Option("--skip-invalid", help="hard or soft check for broken lines")] = False,

) -> None:
    """Analyzes event files and create a report"""

    counter = {"skipped": 0}

    try:

        parser = parsers.format_check(formats)
        stream = [parser(path, skip_invalid, counter) for path in inputs]
        stats = analysis.analyze(*stream)
    except StreamStatsError as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(code=2)

    stats.counter = counter["skipped"]

    if output is not None:
        report.write_json(stats, output)
    else:
        value = report.final_construction(stats)
        typer.echo(json.dumps(value, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    app()

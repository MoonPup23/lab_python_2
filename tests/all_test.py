import json

import pytest
from typer.testing import CliRunner

from streamstats.__main__ import app
from streamstats.analysis import analyze
from streamstats.errors import InvalidEvent
from streamstats.models import Level
from streamstats.parsers import parse_csv, parse_jsonl


def test_parser_jsonl(tmp_path):
    """Checking for correct JSONL"""


    file = tmp_path / "good.jsonl"
    file.write_text('{"timestamp": "2026-10-24T08:00:00Z", "level": "INFO", "source": "api", "message": "Good"}\n',
                    encoding="utf-8",
                    )

    event = list(parse_jsonl(file))
    assert len(event) == 1
    assert event[0].source == "api"
    assert event[0].level == Level.INFO


def test_parser_empty_jsonl(tmp_path):
    """Checking empty JSONl file"""

    file = tmp_path / "empty.jsonl"
    file.write_text("", encoding="utf-8", )

    event = list(parse_jsonl(file))
    assert event == []


def test_bad_line_jsonl(tmp_path):
    """Checking broken lines and raise error"""

    file = tmp_path / "bad_line.jsonl"
    file.write_text(
        '{"timestamp": "2026-10-24T08:00:00Z", "level": "INFO", "source": "api", "message": "Good!"}\n'
        '\n'
        '{"timestamp": "2026-10-24T08:01:12Z", "level": "DEBUG", "source": "worker", "message": "Good"}\n',
        encoding="utf-8"
    )
    with pytest.raises(InvalidEvent, match="line 2"):
        list(parse_jsonl(file))


def test_bad_line_jsonl_skip(tmp_path):
    """Checking broken lines with --skip-invalid"""

    file = tmp_path / "bad_line.jsonl"
    file.write_text(
        '{"timestamp": "2026-10-24T08:00:00Z", "level": "INFO", "source": "api", "message": "Good!"}\n'
        '\n'
        '{"timestamp": "2026-10-24T08:01:12Z", "level": "DEBUG", "source": "worker", "message": "Good"}\n',
        encoding="utf-8"
    )
    counter = {"skipped": 0}

    event = list(parse_jsonl(file, skip_invalid=True, counter=counter))
    assert len(event) == 2
    assert counter["skipped"] == 1


def test_parser_csv(tmp_path):
    """Checking for correct CSV"""

    file = tmp_path / "good.csv"
    file.write_text(
        'timestamp,level,source,message\n'
        '2026-10-25T08:00:00Z,INFO,api,Good\n',
        encoding="utf-8"

    )
    event = list(parse_csv(file))
    assert len(event) == 1
    assert event[0].source == "api"
    assert event[0].level == Level.INFO


def test_parser_empty_csv(tmp_path):
    """Checking empty CSV file"""

    file = tmp_path / "empty.csv"
    file.write_text('', encoding="utf-8")

    event = list(parse_csv(file))

    assert event == []


def test_bad_line_csv(tmp_path):
    """Checking broken lines and raise error"""

    file = tmp_path / "bad.csv"
    file.write_text(
        'timestamp,level,source,message\n'
        '2026-10-24T08:00:00Z,INFO,api,Good\n'
        '\n'
        '2026-10-24T08:00:00Z,INFA,api,Good\n',
        encoding="utf-8",
    )

    with pytest.raises(InvalidEvent, match="line 3"):
        list(parse_csv(file))


def test_bad_line_csv_skip(tmp_path):
    """Checking broken lines with --skip-invalid"""

    file = tmp_path / "bad.csv"
    file.write_text(
        'timestamp,level,source,message\n'
        '2026-10-24T08:00:00Z,INFO,api,Good\n'
        '\n'
        '2026-10-24T08:00:00Z,INFA,api,Good\n',
        encoding="utf-8",
    )
    counter = {"skipped": 0}
    event = list(parse_csv(file, skip_invalid=True, counter=counter))

    assert len(event) == 1
    assert counter["skipped"] == 1


def test_unicode_jsonl(tmp_path):
    """Unicode test for JSONL"""

    file = tmp_path / "unicode.jsonl"
    file.write_text(
        '{"timestamp": "2026-10-24T08:00:00Z", "level": "INFO", "source": "api", "message": "все на красное!"}\n'
        '{"timestamp": "2026-10-24T08:00:01Z", "level": "ERROR", "source": "api", "message": "ДЕНЬГИ КОНЧИЛИСЬ!"}\n',
        encoding="utf-8"
    )
    event = list(parse_jsonl(file))
    assert event[0].message == "все на красное!"
    assert event[1].message == "ДЕНЬГИ КОНЧИЛИСЬ!"


def test_unicode_csv(tmp_path):
    """Unicode test for CSV"""

    file = tmp_path / "unicode.csv"
    file.write_text(
        "timestamp,level,source,message\n"
        '2026-10-24T08:00:00Z,INFO,api,"Дота👎👎👎👎, ПИТОН❤️❤️❤️❤️"\n',
        encoding="utf-8"
    )
    event = list(parse_csv(file))
    assert event[0].message == "Дота👎👎👎👎, ПИТОН❤️❤️❤️❤️"

def test_2_file(tmp_path):
    """Test for analyzing two files and generating statistics for them."""

    file1= tmp_path / "good.jsonl"
    file2 = tmp_path / "goood.jsonl"

    file1.write_text(
        '{"timestamp": "2026-10-24T08:00:00Z", "level": "INFO", "source": "api", "message": "Good!"}\n',
        encoding="utf-8"
    )

    file2.write_text(
        '{"timestamp": "2026-10-24T08:00:52Z", "level": "ERROR", "source": "api", "message": "super GOOD!"}\n',
        encoding="utf-8"
    )

    report = analyze(parse_jsonl(file1), parse_jsonl(file2))

    assert report.total == 2
    assert report.levels["ERROR"] == 1
    assert report.levels["INFO"] == 1
    assert report.first_time.second == 0
    assert report.last_time.second == 52

run = CliRunner()

def test_cli_with_typer(tmp_path):
    """Testing the correct operation of Cli with the correct event"""

    inputs = tmp_path / "good.jsonl"
    inputs.write_text(
        '{"timestamp": "2026-10-24T08:00:00Z", "level": "INFO", "source": "api", "message": "Good!"}\n',
        encoding="utf-8"
    )

    output = tmp_path / "report.json"
    result = run.invoke(
        app, ["analyze" , str(inputs), "--format" , "jsonl", "--output", str(output)]
    )

    assert result.exit_code == 0
    stats = json.loads(output.read_text(encoding="utf-8"))
    assert stats["total"] == 1

def test_cli_bad_line(tmp_path):
    """Testing the correct operation of CLI with broken lines in Event"""

    inputs = tmp_path/ "bad.line"
    inputs.write_text(
        '{"timestamp": "2026-10-24T08:00:00Z", "level": "INFO", "source": "api", "message": "Good!"}\n'
        '\n'
        '{"timestamp": "2026-10-24T08:01:12Z", "level": "DEBUG", "source": "worker", "message": "Good"}\n',
        encoding="utf-8"
    )

    result = run.invoke(app, ["analyze" , str(inputs) , "--format", "jsonl"])

    assert result.exit_code == 2
    assert "line 2" in result.output


def test_cli_bad_line_skip(tmp_path):
    """Test of correct operation of Cli with skip-invalid"""

    inputs = tmp_path / "bad.line.jsonl"
    inputs.write_text(
        '{"timestamp": "2026-10-24T08:00:00Z", "level": "INFO", "source": "api", "message": "Good!"}\n'
        '\n'
        '{"timestamp": "2026-10-24T08:01:12Z", "level": "DEBUG", "source": "worker", "message": "Good"}\n',
        encoding="utf-8"
    )
    output = tmp_path / "report.json"
    result = run.invoke(
        app, ["analyze", str(inputs), "--format", "jsonl", "--output", str(output), "--skip-invalid"]
    )

    assert result.exit_code == 0
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["total"] == 2
    assert report["counter"] == 1

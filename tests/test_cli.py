import subprocess
import sys
import json
import pytest


def run_cli(args):
    result = subprocess.run(
        [sys.executable, "-m", "streamstats"] + args,
        capture_output=True,
        text=True,
        cwd="."
    )
    return result


def test_cli_help():
    result = run_cli(["--help"])
    assert result.returncode == 0
    assert "analyze" in result.stdout


def test_cli_analyze_no_args():
    result = run_cli(["analyze"])
    assert result.returncode != 0


def test_cli_analyze_csv(tmp_path):
    file = tmp_path / "test.csv"
    file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-12T10:00:00,INFO,auth,OK\n"
        "2026-10-12T10:05:00,ERROR,db,Fail\n",
        encoding='utf-8'
    )
    output = tmp_path / "report.json"

    result = run_cli([
        "analyze", str(file),
        "--format", "csv",
        "--output", str(output)
    ])

    assert result.returncode == 0
    assert output.exists()

    report = json.loads(output.read_text(encoding='utf-8'))
    assert report["total_events"] == 2


def test_cli_analyze_jsonl(tmp_path):
    file = tmp_path / "test.jsonl"
    file.write_text(
        '{"timestamp": "2026-10-12T10:00:00", "level": "INFO", "source": "auth", "message": "OK"}\n',
        encoding='utf-8'
    )
    output = tmp_path / "report.json"

    result = run_cli([
        "analyze", str(file),
        "--format", "jsonl",
        "--output", str(output)
    ])

    assert result.returncode == 0
    assert output.exists()


def test_cli_invalid_file_no_skip(tmp_path):
    file = tmp_path / "invalid.jsonl"
    file.write_text(
        '{"timestamp": "2026-10-12T10:00:00", "level": "INFO", "source": "auth", "message": "OK"}\n'
        'broken line\n',
        encoding='utf-8'
    )
    output = tmp_path / "report.json"

    result = run_cli([
        "analyze", str(file),
        "--format", "jsonl",
        "--output", str(output)
    ])

    assert result.returncode == 2


def test_cli_invalid_file_with_skip(tmp_path):
    file = tmp_path / "invalid.jsonl"
    file.write_text(
        '{"timestamp": "2026-10-12T10:00:00", "level": "INFO", "source": "auth", "message": "OK"}\n'
        'broken line\n'
        '{"timestamp": "2026-10-12T10:05:00", "level": "ERROR", "source": "db", "message": "Fail"}\n',
        encoding='utf-8'
    )
    output = tmp_path / "report.json"

    result = run_cli([
        "analyze", str(file),
        "--format", "jsonl",
        "--skip-invalid",
        "--output", str(output)
    ])

    assert result.returncode == 0
    assert output.exists()

    report = json.loads(output.read_text(encoding='utf-8'))
    assert report["total_events"] == 2
    assert report["skipped_lines"] == 1


def test_cli_multiple_files(tmp_path):
    file1 = tmp_path / "file1.jsonl"
    file1.write_text(
        '{"timestamp": "2026-10-12T10:00:00", "level": "INFO", "source": "auth", "message": "OK"}\n',
        encoding='utf-8'
    )
    file2 = tmp_path / "file2.jsonl"
    file2.write_text(
        '{"timestamp": "2026-10-12T10:05:00", "level": "ERROR", "source": "db", "message": "Fail"}\n',
        encoding='utf-8'
    )
    output = tmp_path / "report.json"

    result = run_cli([
        "analyze", str(file1), str(file2),
        "--format", "jsonl",
        "--output", str(output)
    ])

    assert result.returncode == 0

    report = json.loads(output.read_text(encoding='utf-8'))
    assert report["total_events"] == 2


def test_cli_unicode(tmp_path):
    file = tmp_path / "unicode.jsonl"
    file.write_text(
        '{"timestamp": "2026-10-12T10:00:00", "level": "INFO", "source": "авторизация", "message": "Пользователь вошёл 🚀"}\n',
        encoding='utf-8'  # ← обязательно!
    )
    output = tmp_path / "report.json"

    result = run_cli([
        "analyze", str(file),
        "--format", "jsonl",
        "--output", str(output)
    ])

    assert result.returncode == 0

    report = json.loads(output.read_text(encoding='utf-8'))
    assert report["by_source"]["авторизация"] == 1


def test_cli_empty_file(tmp_path):
    file = tmp_path / "empty.jsonl"
    file.write_text("", encoding='utf-8')
    output = tmp_path / "report.json"

    result = run_cli([
        "analyze", str(file),
        "--format", "jsonl",
        "--output", str(output)
    ])

    assert result.returncode == 0

    report = json.loads(output.read_text(encoding='utf-8'))
    assert report["total_events"] == 0


def test_cli_invalid_format(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("some data\n", encoding='utf-8')
    output = tmp_path / "report.json"

    result = run_cli([
        "analyze", str(file),
        "--format", "xml",
        "--output", str(output)
    ])

    assert result.returncode != 0
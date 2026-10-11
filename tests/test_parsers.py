import pytest
from streamstats.parsers import parse_csv, parse_jsonl
from streamstats.errors import InvalidEventError, InvalidTimestampError


# Тесты для JSONL файлов

def test_parse_jsonl_valid(tmp_path):
    """Тест обычного валидного JSONL файла"""
    file = tmp_path / "test.jsonl"

    file.write_text(
        '{"timestamp": "2026-10-12T10:00:00", "level": "INFO", "source": "auth", "message": "OK"}\n'
        '{"timestamp": "2026-10-12T10:05:00", "level": "ERROR", "source": "db", "message": "Fail"}\n',
        encoding='utf-8'
    )

    events = list(parse_jsonl(str(file)))

    assert len(events) == 2
    assert events[0].level == "INFO"
    assert events[1].source == "db"


def test_parse_jsonl_empty_file(tmp_path):
    """Тест пустого JSONL файла"""
    file = tmp_path / "empty.jsonl"
    file.write_text("", encoding='utf-8')

    events = list(parse_jsonl(str(file)))

    assert len(events) == 0


def test_parse_jsonl_invalid_line(tmp_path):
    """Тест файла с повреждённой строкой"""
    file = tmp_path / "invalid.jsonl"

    file.write_text(
        '{"timestamp": "2026-10-12T10:00:00", "level": "INFO", "source": "auth", "message": "OK"}\n'
        'THIS LINE IS BROKEN\n',
        encoding='utf-8'
    )

    with pytest.raises(InvalidEventError):
        list(parse_jsonl(str(file)))


def test_parse_jsonl_invalid_timestamp(tmp_path):
    """Тест файла с неправильной датой"""
    file = tmp_path / "bad_ts.jsonl"

    file.write_text(
        '{"timestamp": "not-a-date", "level": "INFO", "source": "auth", "message": "OK"}\n',
        encoding='utf-8'
    )

    with pytest.raises(InvalidTimestampError):
        list(parse_jsonl(str(file)))


def test_parse_jsonl_skip_invalid(tmp_path):
    """Тест пропуска невалидных строк"""
    file = tmp_path / "skip.jsonl"

    file.write_text(
        '{"timestamp": "2026-10-12T10:00:00", "level": "INFO", "source": "auth", "message": "OK"}\n'
        'broken line\n'
        '{"timestamp": "2026-10-12T10:05:00", "level": "ERROR", "source": "db", "message": "Fail"}\n',
        encoding='utf-8'
    )

    parser = parse_jsonl(str(file), skip_invalid=True)
    events = list(parser)

    assert len(events) == 2
    assert parser.skipped_lines == 1


def test_parse_jsonl_missing_field(tmp_path):
    """Тест файла без обязательного поля"""
    file = tmp_path / "missing.jsonl"

    file.write_text(
        '{"timestamp": "2026-10-12T10:00:00", "level": "INFO"}\n',
        encoding='utf-8'
    )

    with pytest.raises(InvalidEventError):
        list(parse_jsonl(str(file)))


def test_parse_jsonl_invalid_level(tmp_path):
    file = tmp_path / "bad_level.jsonl"

    file.write_text(
        '{"timestamp": "2026-10-12T10:00:00", "level": "INVALID", "source": "auth", "message": "OK"}\n',
        encoding='utf-8'
    )

    with pytest.raises(InvalidEventError):
        list(parse_jsonl(str(file)))


def test_parse_jsonl_empty_source(tmp_path):
    file = tmp_path / "empty_src.jsonl"

    file.write_text(
        '{"timestamp": "2026-10-12T10:00:00", "level": "INFO", "source": "", "message": "OK"}\n',
        encoding='utf-8'
    )

    with pytest.raises(InvalidEventError):
        list(parse_jsonl(str(file)))


def test_parse_jsonl_unicode(tmp_path):
    file = tmp_path / "unicode.jsonl"

    file.write_text(
        '{"timestamp": "2026-10-12T10:00:00", "level": "INFO", "source": "авторизация", "message": "Пользователь вошёл"}\n',
        encoding='utf-8'
    )

    events = list(parse_jsonl(str(file)))

    assert len(events) == 1
    assert events[0].source == "авторизация"
    assert "вошёл" in events[0].message


# Тесты для CSV файлов

def test_parse_csv_valid(tmp_path):
    file = tmp_path / "test.csv"

    file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-12T10:00:00,INFO,auth,OK\n"
        "2026-10-12T10:05:00,ERROR,db,Fail\n",
        encoding='utf-8'
    )

    events = list(parse_csv(str(file)))

    assert len(events) == 2
    assert events[0].level == "INFO"
    assert events[1].source == "db"


def test_parse_csv_empty_file(tmp_path):
    file = tmp_path / "empty.csv"

    file.write_text("timestamp,level,source,message\n", encoding='utf-8')

    events = list(parse_csv(str(file)))

    assert len(events) == 0


def test_parse_csv_invalid_line(tmp_path):
    file = tmp_path / "invalid.csv"

    file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-12T10:00:00,INFO,auth,OK\n"
        "not-a-date,ERROR,db,Fail\n",
        encoding='utf-8'
    )

    with pytest.raises(InvalidTimestampError):
        list(parse_csv(str(file)))


def test_parse_csv_skip_invalid(tmp_path):
    file = tmp_path / "skip.csv"

    file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-12T10:00:00,INFO,auth,OK\n"
        "bad-date,ERROR,db,Fail\n"
        "2026-10-12T10:05:00,WARNING,api,Warn\n",
        encoding='utf-8'
    )

    parser = parse_csv(str(file), skip_invalid=True)
    events = list(parser)

    assert len(events) == 2
    assert parser.skipped_lines == 1


def test_parse_csv_missing_field(tmp_path):
    file = tmp_path / "missing.csv"

    file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-12T10:00:00,INFO,auth\n",
        encoding='utf-8'
    )

    with pytest.raises(InvalidEventError):
        list(parse_csv(str(file)))


def test_parse_csv_unicode(tmp_path):
    file = tmp_path / "unicode.csv"

    file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-12T10:00:00,INFO,авторизация,Пользователь вошёл\n",
        encoding='utf-8'
    )

    events = list(parse_csv(str(file)))

    assert len(events) == 1
    assert events[0].source == "авторизация"
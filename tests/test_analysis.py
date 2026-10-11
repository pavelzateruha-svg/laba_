import pytest
from streamstats.models import Statistics, Event
from streamstats.analysis import update_statistics, analyze_files


def test_update_statistics_basic():
    """Тест базового обновления статистики."""
    stats = Statistics()
    event = Event(
        timestamp="2026-10-12T10:00:00",
        level="INFO",
        source="auth",
        message="Test"
    )
    update_statistics(stats, event)

    assert stats.total_events == 1
    assert stats.by_level["INFO"] == 1
    assert stats.by_source["auth"] == 1
    assert stats.error_sources.get("auth") is None  # INFO не считается ошибкой


def test_update_statistics_error():
    """Тест подсчёта ошибок (ERROR/CRITICAL)."""
    stats = Statistics()
    event = Event(
        timestamp="2026-10-12T10:00:00",
        level="ERROR",
        source="db",
        message="Fail"
    )
    update_statistics(stats, event)

    assert stats.error_sources["db"] == 1


def test_update_statistics_critical():
    """Тест подсчёта CRITICAL как ошибки."""
    stats = Statistics()
    event = Event(
        timestamp="2026-10-12T10:00:00",
        level="CRITICAL",
        source="db",
        message="Critical fail"
    )
    update_statistics(stats, event)

    assert stats.error_sources["db"] == 1


def test_update_statistics_timestamps():
    """Тест обновления первой и последней метки времени."""
    stats = Statistics()

    event1 = Event(timestamp="2026-10-12T10:00:00", level="INFO", source="auth", message="1")
    event2 = Event(timestamp="2026-10-12T10:05:00", level="INFO", source="auth", message="2")
    event3 = Event(timestamp="2026-10-12T09:55:00", level="INFO", source="auth", message="3")

    update_statistics(stats, event1)
    update_statistics(stats, event2)
    update_statistics(stats, event3)

    assert stats.first_timestamp == "2026-10-12T09:55:00"
    assert stats.last_timestamp == "2026-10-12T10:05:00"


def test_update_statistics_multiple():
    """Тест множественных обновлений."""
    stats = Statistics()

    events = [
        Event(timestamp="2026-10-12T10:00:00", level="INFO", source="auth", message="1"),
        Event(timestamp="2026-10-12T10:01:00", level="ERROR", source="db", message="2"),
        Event(timestamp="2026-10-12T10:02:00", level="ERROR", source="db", message="3"),
        Event(timestamp="2026-10-12T10:03:00", level="WARNING", source="auth", message="4"),
    ]

    for event in events:
        update_statistics(stats, event)

    assert stats.total_events == 4
    assert stats.by_level["ERROR"] == 2
    assert stats.by_source["db"] == 2
    assert stats.error_sources["db"] == 2


def test_analyze_files_single_csv(tmp_path):
    """Integration-тест: анализ одного CSV файла."""
    file = tmp_path / "test.csv"
    file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-12T10:00:00,INFO,auth,OK\n"
        "2026-10-12T10:05:00,ERROR,db,Fail\n"
    )
    output = tmp_path / "report.json"

    analyze_files([str(file)], "csv", str(output), skip_invalid=False)

    assert output.exists()
    import json
    report = json.loads(output.read_text())
    assert report["total_events"] == 2
    assert report["by_level"]["ERROR"] == 1


def test_analyze_files_single_jsonl(tmp_path):
    """Integration-тест: анализ одного JSONL файла."""
    file = tmp_path / "test.jsonl"
    file.write_text(
        '{"timestamp": "2026-10-12T10:00:00", "level": "INFO", "source": "auth", "message": "OK"}\n'
        '{"timestamp": "2026-10-12T10:05:00", "level": "ERROR", "source": "db", "message": "Fail"}\n'
    )
    output = tmp_path / "report.json"

    analyze_files([str(file)], "jsonl", str(output), skip_invalid=False)

    assert output.exists()
    import json
    report = json.loads(output.read_text())
    assert report["total_events"] == 2


def test_analyze_files_multiple(tmp_path):
    """Тест анализа нескольких файлов."""
    file1 = tmp_path / "file1.jsonl"
    file1.write_text(
        '{"timestamp": "2026-10-12T10:00:00", "level": "INFO", "source": "auth", "message": "OK"}\n'
    )
    file2 = tmp_path / "file2.jsonl"
    file2.write_text(
        '{"timestamp": "2026-10-12T10:05:00", "level": "ERROR", "source": "db", "message": "Fail"}\n'
    )
    output = tmp_path / "report.json"

    analyze_files([str(file1), str(file2)], "jsonl", str(output), skip_invalid=False)

    import json
    report = json.loads(output.read_text())
    assert report["total_events"] == 2
    assert report["by_source"]["auth"] == 1
    assert report["by_source"]["db"] == 1


def test_analyze_files_skip_invalid(tmp_path):
    """Тест анализа с пропуском невалидных строк."""
    file = tmp_path / "skip.jsonl"
    file.write_text(
        '{"timestamp": "2026-10-12T10:00:00", "level": "INFO", "source": "auth", "message": "OK"}\n'
        'broken line\n'
        '{"timestamp": "2026-10-12T10:05:00", "level": "ERROR", "source": "db", "message": "Fail"}\n'
    )
    output = tmp_path / "report.json"

    analyze_files([str(file)], "jsonl", str(output), skip_invalid=True)

    import json
    report = json.loads(output.read_text())
    assert report["total_events"] == 2
    assert report["skipped_lines"] == 1
from typing import List

from streamstats.models import Statistics, Event
from streamstats.parsers import parse_csv, parse_jsonl
from streamstats.report import generate_report


def update_statistics(stats: Statistics, event: Event):
    stats.total_events += 1
    stats.by_level[event.level] += 1
    stats.by_source[event.source] += 1

    if event.level in ('ERROR', 'CRITICAL'):
        stats.error_sources[event.source] += 1

    if stats.first_timestamp is None or event.timestamp < stats.first_timestamp:
        stats.first_timestamp = event.timestamp
    if stats.last_timestamp is None or event.timestamp > stats.last_timestamp:
        stats.last_timestamp = event.timestamp


def analyze_files(inputs: List[str], fmt: str, output: str, skip_invalid: bool):
    stats = Statistics()

    if fmt == 'csv':
        parser_func = parse_csv
    elif fmt == 'jsonl':
        parser_func = parse_jsonl
    else:
        from streamstats.errors import UnsupportedFormatError
        raise UnsupportedFormatError(f"Неподдерживаемый формат: {fmt}")

    for filepath in inputs:
        parser = parser_func(filepath, skip_invalid=skip_invalid)

        for event in parser:
            update_statistics(stats, event)

        stats.skipped_lines += parser.skipped_lines

    generate_report(stats, output)
    print(f"Отчет успешно сохранен в {output}")
from typing import List

from streamstats.models import Statistics, Event
from streamstats.parsers import parse_csv, parse_jsonl
from streamstats.report import generate_report


def update_statistics(stats: Statistics, event: Event):
    """Обновляет статистику одним событием."""
    stats.total_events += 1
    stats.by_level[event.level] += 1
    stats.by_source[event.source] += 1

    # Считаем только ERROR и CRITICAL для топ-5 источников ошибок
    if event.level in ('ERROR', 'CRITICAL'):
        stats.error_sources[event.source] += 1

    # Обновляем первую и последнюю метки времени
    if stats.first_timestamp is None or event.timestamp < stats.first_timestamp:
        stats.first_timestamp = event.timestamp
    if stats.last_timestamp is None or event.timestamp > stats.last_timestamp:
        stats.last_timestamp = event.timestamp


def analyze_files(inputs: List[str], fmt: str, output: str, skip_invalid: bool):
    """Главная функция: читает файлы, парсит, считает, сохраняет отчёт."""
    stats = Statistics()

    # Выбираем нужный парсер
    if fmt == 'csv':
        parser_func = parse_csv
    elif fmt == 'jsonl':
        parser_func = parse_jsonl
    else:
        from streamstats.errors import UnsupportedFormatError
        raise UnsupportedFormatError(f"Неподдерживаемый формат: {fmt}")

    # Проходим по всем файлам
    for filepath in inputs:
        # Создаём парсер с флагом skip_invalid
        parser = parser_func(filepath, skip_invalid=skip_invalid)

        # Итерируемся по событиям
        for event in parser:
            update_statistics(stats, event)

        # После завершения итерации забираем количество пропусков
        stats.skipped_lines += parser.skipped_lines

    # Сохраняем отчёт (только если дошли до сюда без ошибок)
    generate_report(stats, output)
    print(f"Отчет успешно сохранен в {output}")
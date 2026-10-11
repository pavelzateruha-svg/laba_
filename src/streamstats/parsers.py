import csv
import json
import logging
from datetime import datetime
from typing import Iterator

from streamstats.models import Event
from streamstats.errors import InvalidEventError, InvalidTimestampError

ALLOWED_LEVELS = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}


def _validate_and_create_event(data: dict, filename: str, line_number: int) -> Event:
    """Проверяет словарь данных и возвращает объект Event."""
    required_fields = ['timestamp', 'level', 'source', 'message']
    for field in required_fields:
        if field not in data or data[field] is None:
            raise InvalidEventError(
                f"Отсутствует обязательное поле '{field}'",
                filename=filename,
                line_number=line_number
            )

    if data['level'] not in ALLOWED_LEVELS:
        raise InvalidEventError(
            f"Недопустимый уровень '{data['level']}'",
            filename=filename,
            line_number=line_number
        )

    if not str(data['source']).strip():
        raise InvalidEventError(
            "Поле 'source' не может быть пустым",
            filename=filename,
            line_number=line_number
        )

    try:
        datetime.fromisoformat(str(data['timestamp']))
    except ValueError:
        raise InvalidTimestampError(
            f"Неверный формат timestamp '{data['timestamp']}'",
            filename=filename,
            line_number=line_number
        )

    return Event(
        timestamp=str(data['timestamp']),
        level=str(data['level']),
        source=str(data['source']),
        message=str(data['message'])
    )


class JsonlParser:
    """Парсер для JSONL файлов."""

    def __init__(self, filepath: str, skip_invalid: bool = False):
        self.filepath = filepath
        self.skip_invalid = skip_invalid
        self.skipped_lines = 0

    def __iter__(self) -> Iterator[Event]:
        with open(self.filepath, 'r', encoding='utf-8') as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                except json.JSONDecodeError as e:
                    # ВАЖНО: превращаем ошибку JSON в нашу InvalidEventError
                    if self.skip_invalid:
                        logging.warning(f"Пропуск строки {line_number} в {self.filepath}: неверный JSON - {e}")
                        self.skipped_lines += 1
                        continue
                    else:
                        raise InvalidEventError(
                            f"Неверный JSON: {e}",
                            filename=self.filepath,
                            line_number=line_number
                        )

                try:
                    event = _validate_and_create_event(data, self.filepath, line_number)
                    yield event
                except (InvalidEventError, InvalidTimestampError) as e:
                    if self.skip_invalid:
                        logging.warning(f"Пропуск строки {line_number} в {self.filepath}: {e}")
                        self.skipped_lines += 1
                    else:
                        raise


class CsvParser:
    """Парсер для CSV файлов."""

    def __init__(self, filepath: str, skip_invalid: bool = False):
        self.filepath = filepath
        self.skip_invalid = skip_invalid
        self.skipped_lines = 0

    def __iter__(self) -> Iterator[Event]:
        with open(self.filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                line_number = reader.line_num
                try:
                    event = _validate_and_create_event(row, self.filepath, line_number)
                    yield event
                except (InvalidEventError, InvalidTimestampError) as e:
                    if self.skip_invalid:
                        logging.warning(f"Пропуск строки {line_number} в {self.filepath}: {e}")
                        self.skipped_lines += 1
                    else:
                        raise


# Функции-обёртки для обратной совместимости (если где-то использовались)
def parse_jsonl(filepath: str, skip_invalid: bool = False):
    return JsonlParser(filepath, skip_invalid)


def parse_csv(filepath: str, skip_invalid: bool = False):
    return CsvParser(filepath, skip_invalid)
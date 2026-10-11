class StreamStatsError(Exception):
    """Базовое исключение для всех ошибок пакета streamstats."""
    pass


class UnsupportedFormatError(StreamStatsError):
    """Ошибка неподдерживаемого формата файла."""
    pass


class InvalidEventError(StreamStatsError):
    """Ошибка невалидного события (отсутствуют поля, неверный level и т.д.)."""

    def __init__(self, message: str, filename: str = None, line_number: int = None):
        self.filename = filename
        self.line_number = line_number

        # Формируем понятное сообщение
        if filename and line_number is not None:
            full_message = f"Файл '{filename}', строка {line_number}: {message}"
        else:
            full_message = message

        super().__init__(full_message)


class InvalidTimestampError(StreamStatsError):
    """Ошибка невалидной временной метки."""

    def __init__(self, message: str, filename: str = None, line_number: int = None):
        self.filename = filename
        self.line_number = line_number

        if filename and line_number is not None:
            full_message = f"Файл '{filename}', строка {line_number}: {message}"
        else:
            full_message = message

        super().__init__(full_message)


class CLIConfigError(StreamStatsError):
    """Ошибка конфигурации CLI (неверные аргументы, пути и т.д.)."""
    pass
class StreamStatsError(Exception):
    pass


class UnsupportedFormatError(StreamStatsError):
    pass


class InvalidEventError(StreamStatsError):
    def __init__(self, message: str, filename: str = None, line_number: int = None):
        self.filename = filename
        self.line_number = line_number

        if filename and line_number is not None:
            full_message = f"Файл '{filename}', строка {line_number}: {message}"
        else:
            full_message = message

        super().__init__(full_message)


class InvalidTimestampError(StreamStatsError):
    def __init__(self, message: str, filename: str = None, line_number: int = None):
        self.filename = filename
        self.line_number = line_number

        if filename and line_number is not None:
            full_message = f"Файл '{filename}', строка {line_number}: {message}"
        else:
            full_message = message

        super().__init__(full_message)


class CLIConfigError(StreamStatsError):
    pass
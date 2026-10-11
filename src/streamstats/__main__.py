import argparse
import sys
import logging

from streamstats.errors import (
    StreamStatsError,
    InvalidEventError,
    InvalidTimestampError,
    CLIConfigError
)


def build_parser() -> argparse.ArgumentParser:
    """Настройка парсера аргументов командной строки."""
    parser = argparse.ArgumentParser(description="Потоковый анализатор файлов (Stream Stats)")

    # Добавляем подкоманды
    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")

    # Подкоманда analyze
    analyze_parser = subparsers.add_parser("analyze", help="Анализ входных файлов и генерация отчета")

    analyze_parser.add_argument("inputs", nargs="+", help="Пути к входным файлам")
    analyze_parser.add_argument("--format", choices=["csv", "jsonl"], required=True, help="Формат входных файлов")
    analyze_parser.add_argument("--output", required=True, help="Путь для сохранения JSON-отчета")
    analyze_parser.add_argument("--skip-invalid", action="store_true", help="Пропускать невалидные строки вместо остановки")

    return parser


def main():
    """Точка входа в приложение."""
    parser = build_parser()
    args = parser.parse_args()

    # Если команда не указана, выводим справку
    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Настраиваем логирование (для вывода WARNING при --skip-invalid)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    try:
        if args.command == "analyze":
            # Импортируем и запускаем основную логику.
            # ЗАМЕНИ 'analyze_files' на название функции, которую ты создашь
            # в analysis.py или parsers.py для запуска обработки!
            from streamstats.analysis import analyze_files

            analyze_files(
                inputs=args.inputs,
                fmt=args.format,
                output=args.output,
                skip_invalid=args.skip_invalid
            )

    except CLIConfigError as e:
        print(f"Ошибка конфигурации: {e}", file=sys.stderr)
        sys.exit(1)

    except (InvalidEventError, InvalidTimestampError) as e:
        # По заданию: остановить обработку и завершить CLI с кодом 2
        print(f"Ошибка валидации: {e}", file=sys.stderr)
        sys.exit(2)

    except StreamStatsError as e:
        # Другие кастомные ошибки (например, UnsupportedFormatError)
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        # На границе CLI преобразуем неизвестные ошибки в понятные,
        # либо просто выводим и падаем с кодом 1.
        print(f"Непредвиденная ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
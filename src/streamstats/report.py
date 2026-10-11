import json
from streamstats.models import Statistics


def generate_report(stats: Statistics, output_path: str):
    """Формирует и сохраняет JSON-отчёт."""
    # Формируем словарь для отчёта
    report_data = {
        "total_events": stats.total_events,
        "by_level": dict(stats.by_level),
        "by_source": dict(stats.by_source),
        "top_error_sources": [
            {"source": source, "count": count}
            for source, count in stats.error_sources.most_common(5)
        ],
        "first_timestamp": stats.first_timestamp,
        "last_timestamp": stats.last_timestamp,
        "skipped_lines": stats.skipped_lines
    }

    # Записываем в файл
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
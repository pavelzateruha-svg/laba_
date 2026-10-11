from dataclasses import dataclass, field
from collections import Counter

@dataclass
class Event:
    timestamp: str
    level: str
    source: str
    message: str

@dataclass
class Statistics:
    total_events: int = 0
    skipped_lines: int = 0

    first_timestamp: str | None = None
    last_timestamp: str | None = None

    by_level: Counter = field(default_factory=Counter)
    by_source: Counter = field(default_factory=Counter)
    error_sources: Counter = field(default_factory=Counter)
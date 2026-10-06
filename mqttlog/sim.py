from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from .record import Record

TOPICS = (
    ("sensors/lab/temp", lambda i: f"{20.0 + (i % 7) * 0.3:.1f}"),
    ("sensors/lab/rh", lambda i: f"{40 + (i % 5)}"),
    ("sensors/door/state", lambda i: "open" if i % 4 == 0 else "closed"),
)


def simulate(count: int, start: datetime | None = None, tz_name: str = "America/Los_Angeles") -> list[Record]:
    tz = ZoneInfo(tz_name)
    origin = start or datetime.now(timezone.utc).astimezone(tz)
    rows: list[Record] = []
    for i in range(count):
        topic, payload = TOPICS[i % len(TOPICS)]
        ts = (origin + timedelta(seconds=i * 15)).isoformat(timespec="seconds")
        rows.append(Record(ts, topic, payload(i)))
    return rows

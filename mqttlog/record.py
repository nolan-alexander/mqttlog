from __future__ import annotations

from dataclasses import dataclass
import re

LINE_RE = re.compile(r"^(\S+)\s+(\S+)\s+(.*)$")


@dataclass(frozen=True)
class Record:
    ts: str
    topic: str
    payload: str

    def line(self) -> str:
        return f"{self.ts} {self.topic} {self.payload}"


def parse_line(line: str) -> Record | None:
    text = line.strip()
    if not text or text.startswith("#"):
        return None
    match = LINE_RE.match(text)
    if not match:
        raise ValueError(f"bad record: {line!r}")
    return Record(match.group(1), match.group(2), match.group(3))

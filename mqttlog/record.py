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


def topic_match(topic: str, pattern: str) -> bool:
    if pattern == "#":
        return True
    t_parts = topic.split("/")
    p_parts = pattern.split("/")
    ti = 0
    for i, part in enumerate(p_parts):
        if part == "#":
            return i == len(p_parts) - 1
        if ti >= len(t_parts):
            return False
        if part == "+":
            ti += 1
            continue
        if part != t_parts[ti]:
            return False
        ti += 1
    return ti == len(t_parts)

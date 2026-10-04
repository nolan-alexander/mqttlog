from __future__ import annotations

from pathlib import Path

from .record import Record


class RotatingLog:
    def __init__(self, directory: Path, prefix: str = "mqttlog", max_bytes: int = 4096, max_files: int = 8) -> None:
        self.directory = directory
        self.prefix = prefix
        self.max_bytes = max_bytes
        self.max_files = max_files
        self.directory.mkdir(parents=True, exist_ok=True)
        self._index = self._next_index()
        self._written = 0
        self._fh = self._open()

    def _name(self, index: int) -> Path:
        return self.directory / f"{self.prefix}-{index:03d}.log"

    def _next_index(self) -> int:
        existing = sorted(self.directory.glob(f"{self.prefix}-*.log"))
        if not existing:
            return 0
        last = existing[-1].stem.split("-")[-1]
        try:
            return int(last)
        except ValueError:
            return len(existing)

    def _open(self):
        path = self._name(self._index)
        fh = path.open("a", encoding="utf-8")
        self._written = path.stat().st_size
        return fh

    def write(self, record: Record) -> Path:
        line = record.line() + "\n"
        encoded = line.encode("utf-8")
        if self._written and self._written + len(encoded) > self.max_bytes:
            self._fh.close()
            self._index += 1
            if self._index >= self.max_files:
                oldest = self._name(self._index - self.max_files)
                if oldest.exists():
                    oldest.unlink()
            self._fh = self._open()
            self._written = 0
        self._fh.write(line)
        self._fh.flush()
        self._written += len(encoded)
        return self._name(self._index)

    def close(self) -> None:
        self._fh.close()

import tempfile
import unittest
from pathlib import Path

from mqttlog.record import Record
from mqttlog.rotate import RotatingLog


class RotateTests(unittest.TestCase):
    def test_rotates_when_over_max_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            log = RotatingLog(Path(tmp), max_bytes=40, max_files=8)
            try:
                for i in range(6):
                    log.write(Record("t", "sensors/x", f"payload-{i}"))
            finally:
                log.close()
            files = sorted(Path(tmp).glob("mqttlog-*.log"))
            self.assertGreaterEqual(len(files), 2)
            blob = "\n".join(p.read_text(encoding="utf-8") for p in files)
            self.assertIn("payload-0", blob)
            self.assertIn("payload-5", blob)


if __name__ == "__main__":
    unittest.main()

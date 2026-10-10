import tempfile
import unittest
from pathlib import Path

from mqttlog.cli import main


class CliTests(unittest.TestCase):
    def test_sim_stdout(self) -> None:
        # main prints; just ensure it returns 0
        self.assertEqual(main(["sim", "--count", "3"]), 0)

    def test_replay_and_csv(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "in.log"
            src.write_text(
                "2026-10-01T20:11:03-07:00 sensors/lab/temp 21.4\n"
                "2026-10-01T20:11:18-07:00 actuators/fan on\n",
                encoding="utf-8",
            )
            out = Path(tmp) / "out"
            self.assertEqual(main(["replay", str(src), "--topic", "sensors/#", "--out", str(out)]), 0)
            logs = list(out.glob("*.log"))
            self.assertEqual(len(logs), 1)
            self.assertIn("sensors/lab/temp", logs[0].read_text(encoding="utf-8"))
            csv_path = Path(tmp) / "out.csv"
            self.assertEqual(main(["csv", str(src), "--topic", "#", "--out", str(csv_path)]), 0)
            text = csv_path.read_text(encoding="utf-8")
            self.assertIn("ts,topic,payload", text)
            self.assertIn("actuators/fan", text)


if __name__ == "__main__":
    unittest.main()

import unittest

from mqttlog.record import parse_line, parse_lines, topic_match


class RecordTests(unittest.TestCase):
    def test_parse_skips_comments(self) -> None:
        self.assertIsNone(parse_line("# ignore"))
        self.assertIsNone(parse_line("  "))

    def test_parse_line(self) -> None:
        rec = parse_line("2026-10-01T20:11:03-07:00 sensors/lab/temp 21.4")
        assert rec is not None
        self.assertEqual(rec.topic, "sensors/lab/temp")
        self.assertEqual(rec.payload, "21.4")

    def test_bad_line(self) -> None:
        with self.assertRaises(ValueError):
            parse_line("not-a-record")

    def test_hash_filter(self) -> None:
        self.assertTrue(topic_match("sensors/lab/temp", "sensors/#"))
        self.assertFalse(topic_match("actuators/fan", "sensors/#"))

    def test_plus_filter(self) -> None:
        self.assertTrue(topic_match("sensors/lab", "sensors/+"))
        self.assertFalse(topic_match("sensors/lab/temp", "sensors/+"))

    def test_parse_lines(self) -> None:
        rows = parse_lines("# c\n2026-10-01T20:11:03-07:00 sensors/lab/temp 21.4\n")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].payload, "21.4")


if __name__ == "__main__":
    unittest.main()

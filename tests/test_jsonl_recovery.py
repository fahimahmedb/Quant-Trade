"""Crash-safety regression for append-only persistent state."""

import json
import tempfile
import unittest
from pathlib import Path

from quant.state import append_jsonl, read_jsonl


class JsonlCrashRecoveryTests(unittest.TestCase):
    def test_torn_final_append_is_ignored_then_repaired_on_next_append(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            path.write_text(json.dumps({"id": 1}) + "\n" + '{"id":', encoding="utf-8")

            self.assertEqual(list(read_jsonl(path)), [{"id": 1}])
            append_jsonl(path, {"id": 2})
            self.assertEqual(list(read_jsonl(path)), [{"id": 1}, {"id": 2}])
            self.assertTrue(path.read_bytes().endswith(b"\n"))

    def test_malformed_committed_line_remains_loud(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            path.write_text('{"id": 1}\nnot-json\n', encoding="utf-8")
            with self.assertRaises(json.JSONDecodeError):
                list(read_jsonl(path))


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest
from datetime import timezone

from quant.dataplane.identity import parse_pit_instant


class StrictPitClockTests(unittest.TestCase):
    def test_naive_datetime_is_rejected_instead_of_assuming_utc(self) -> None:
        for value in (
            "2026-01-02T12:00:00",
            "2026-01-02T12:00:00.123456",
        ):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "explicit timezone offset"):
                    parse_pit_instant(value)

    def test_explicit_z_and_offset_are_admissible(self) -> None:
        zulu = parse_pit_instant("2026-01-02T12:00:00Z")
        offset = parse_pit_instant("2026-01-02T13:00:00+01:00")
        self.assertEqual(zulu.utcoffset(), timezone.utc.utcoffset(zulu))
        self.assertEqual(zulu.timestamp(), offset.timestamp())

    def test_civil_date_boundary_remains_explicit_midnight_utc(self) -> None:
        civil = parse_pit_instant("2026-01-02")
        self.assertEqual(civil.isoformat(), "2026-01-02T00:00:00+00:00")


if __name__ == "__main__":
    unittest.main()

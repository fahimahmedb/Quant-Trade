"""Additional adversarial Book integrity regression tests from the V1 red team."""

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from quant.book.ledger import Ledger


class BookRestatementTests(unittest.TestCase):
    def test_same_session_restatement_cannot_leave_a_phantom_peak(self):
        """A superseded high mark must not throttle future risk through peak_nav."""
        with tempfile.TemporaryDirectory() as directory:
            ledger = Ledger(Path(directory) / "book.json", initial_capital=100.0)
            ledger.apply_fill("AAA", 1.0, 10.0, 0.0, "2025-01-01", "S", "fill-1")

            ledger.mark_to_market("2025-01-01", {"AAA": 30.0})
            self.assertEqual(ledger.state.peak_nav, 120.0)

            ledger.mark_to_market("2025-01-01", {"AAA": 10.0})
            self.assertEqual(len(ledger.state.nav_history), 1)
            self.assertEqual(ledger.state.nav_history[0]["nav"], 100.0)
            self.assertEqual(ledger.state.peak_nav, 100.0)
            self.assertAlmostEqual(ledger.drawdown, 0.0)


if __name__ == "__main__":
    unittest.main()

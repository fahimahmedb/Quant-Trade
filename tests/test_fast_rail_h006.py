"""H-006 offline tests on invented, labelled fixtures (no network, no real market data)."""
import datetime as dt
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from research.fast_rail.h006 import analysis, build  # noqa: E402

UTC = dt.timezone.utc


def fixture(**over):
    """INVENTED match: pre-match fair H~0.50, Polymarket H at 0.40 -> one H bet."""
    m = {"slug": "invented-a-b", "league": "E0", "kickoff_ts": 10_000.0, "collection_ts": 1_000.0,
         "PS": [1.90, 3.60, 4.20], "PSC": [2.10, 3.40, 3.70], "FTR": "H", "fee_rate": 0.0,
         "volume": {"H": 1.0, "D": 1.0, "A": 1.0},
         "prices": {"H": [{"t": 1_000, "p": 0.40}], "D": [{"t": 1_000, "p": 0.40}],
                    "A": [{"t": 1_000, "p": 0.40}]}}
    m.update(over)
    return m


class SignalTests(unittest.TestCase):
    def test_signal_never_reads_closing_odds(self):
        base = analysis.decide(fixture())
        for psc in ([1.01, 50.0, 90.0], [99.0, 99.0, 1.02], None):
            self.assertEqual(analysis.decide(fixture(PSC=psc)), base)
        self.assertEqual([b["outcome"] for b in base], ["H"])

    def test_closing_odds_only_move_clv(self):
        bets = analysis.decide(fixture())
        a = analysis.score(fixture(), bets)["clv"]
        b = analysis.score(fixture(PSC=[1.5, 4.5, 7.0]), bets)["clv"]
        self.assertGreater(b, a)

    def test_devig_sums_to_one(self):
        for odds in ([1.90, 3.60, 4.20], [1.20, 7.5, 15.0], [3.1, 3.2, 2.4]):
            self.assertAlmostEqual(sum(analysis.fair(odds).values()), 1.0, places=9)


class EntryTimingTests(unittest.TestCase):
    def test_entry_never_before_collection_nor_at_or_after_kickoff(self):
        hist = [{"t": 999, "p": 0.1}, {"t": 10_000, "p": 0.1}, {"t": 10_500, "p": 0.1}]
        self.assertIsNone(analysis.entry_price(hist, 1_000, 10_000))
        hist.append({"t": 5_000, "p": 0.3})
        self.assertEqual(analysis.entry_price(hist, 1_000, 10_000)["t"], 5_000)
        m = fixture(prices={"H": [{"t": 999, "p": 0.10}, {"t": 10_000, "p": 0.10}], "D": [], "A": []})
        self.assertEqual(analysis.decide(m), [])

    def test_collection_time_rule(self):
        sat = dt.datetime(2025, 3, 15, 15, tzinfo=UTC)
        self.assertEqual(build.collection_time(sat), dt.datetime(2025, 3, 14, 18, tzinfo=UTC))
        mon = dt.datetime(2025, 3, 17, 20, tzinfo=UTC)
        self.assertEqual(build.collection_time(mon), dt.datetime(2025, 3, 14, 18, tzinfo=UTC))
        wed = dt.datetime(2025, 3, 12, 19, 30, tzinfo=UTC)
        self.assertEqual(build.collection_time(wed), dt.datetime(2025, 3, 11, 18, tzinfo=UTC))
        for k in (sat, mon, wed):
            self.assertLess(build.collection_time(k), k)

    def test_costs_raise_buy_price(self):
        self.assertAlmostEqual(analysis.buy_price(0.5, 0.03), 0.5 + 0.01 + 0.03 * 0.25)
        self.assertGreater(analysis.buy_price(0.5, 0.03, 2.0), analysis.buy_price(0.5, 0.03))


class SplitTests(unittest.TestCase):
    def test_last_15_percent_untouched_and_chronological(self):
        ms = [fixture(slug=f"m{i:03d}", kickoff_ts=float(1000 - i)) for i in range(100)]
        d, v, u = analysis.split(ms)
        self.assertEqual((len(d), len(v), len(u)), (55, 30, 15))
        self.assertLess(max(m["kickoff_ts"] for m in v), min(m["kickoff_ts"] for m in u))
        self.assertLess(max(m["kickoff_ts"] for m in d), min(m["kickoff_ts"] for m in v))

    def test_evaluate_never_sees_untouched(self):
        ms = [fixture(slug=f"m{i:03d}", kickoff_ts=float(i)) for i in range(20)]
        _, v, u = analysis.split(ms)
        self.assertEqual(analysis.evaluate(v)["matches"], len(v))
        self.assertTrue(set(m["slug"] for m in u).isdisjoint(m["slug"] for m in v))


if __name__ == "__main__":
    unittest.main()

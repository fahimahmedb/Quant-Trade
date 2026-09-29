"""H-001 forward evaluation, order 12 (engagements, FORWARD_PASS(PRICE)). Numbers INVENTED."""

from __future__ import annotations

import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "research" / "fast_rail" / "h001"))
import forward as f  # noqa: E402

T0 = "2026-10-01T12:00:00+00:00"
KICK = "2026-10-01T15:00:00+00:00"
LATE = datetime(2027, 1, 1, tzinfo=timezone.utc)
ACCEPT = lambda series: {"decision": "ACCEPT_EDGE", "observations": len(series)}  # noqa: E731


def pin(stamp, event="E1", kick=KICK):
    return {"event_id": event, "observed_at": stamp, "commence_time": kick,
            "prices": {"Home": 2.0, "Away": 2.0}}


def quote(stamp, venue, ask, event="E1", market="M", bid=None, book="OK", depth=150):
    q = {"odds_event_id": event, "observed_at": stamp, "venue": venue, "outcome": "Home",
         "best_ask": ask, "best_bid": bid, "fetched_at": stamp, "asks": [[ask, depth]],
         ("ticker" if venue == "KALSHI" else "market_id"): market,
         "token_id": None if venue == "KALSHI" else "tok"}
    if venue == "KALSHI":
        q.update(book_status=book, book_fetched_at=stamp)
    return q


def book(n, close_mid=0.48, settle=1.0, with_close=True):
    """n matches: entry ask 0.40 vs fair 0.5; optional later venue quote; settlement."""
    pins, quotes, settled, at = [], [], {}, {}
    for i in range(n):
        ev, day = f"E{i}", f"2026-{10 + i // 250:02d}-{1 + (i % 250) // 10:02d}"
        entry, later, kick = (f"{day}T0{i % 10}:00:00+00:00", f"{day}T19:{i % 4}0:00+00:00",
                              f"{day}T2{i % 4}:00:00+00:00")
        pins += [pin(entry, ev, kick), pin(later, ev, kick)]
        quotes.append(quote(entry, "KALSHI", 0.40, ev, f"K{i}"))
        if with_close:
            quotes.append(quote(later, "KALSHI", close_mid + 0.01, ev, f"K{i}",
                                bid=close_mid - 0.01))
        if settle is not None:
            settled[f"KALSHI|K{i}|None"] = settle
            at[f"KALSHI|K{i}|None"] = f"{day}T23:00:00+00:00"
    return pins, quotes, settled, at


class Order12Tests(unittest.TestCase):
    def test_fees(self):
        self.assertAlmostEqual(f.fee_per_contract("KALSHI", 0.5), 0.0175)
        self.assertAlmostEqual(f.fee_per_contract("KALSHI", 0.5, contracts=1), 0.02)
        self.assertAlmostEqual(f.fee_per_contract("POLYMARKET", 0.5), 0.0125)

    def test_bet_before_pristine_is_ignored(self):
        early = "2026-09-29T13:30:00+00:00"
        self.assertEqual(f.find_bets([pin(early)], [quote(early, "KALSHI", 0.40)]), [])

    def test_kalshi_without_book_takes_no_bet(self):
        for status in ("UNAVAILABLE: 401", "EMPTY", None):
            self.assertEqual(f.find_bets([pin(T0)], [quote(T0, "KALSHI", 0.40, book=status)]), [])
        self.assertEqual(f.find_bets([pin(T0)], [quote(T0, "KALSHI", 0.40, depth=50)]), [])
        self.assertEqual(len(f.find_bets([pin(T0)], [quote(T0, "KALSHI", 0.40)])), 1)

    def test_bet_without_close_stays_in_pnl(self):
        pins, quotes, settled, at = book(1, settle=0.0, with_close=False)
        report = f.evaluate(pins, quotes, settled, LATE, settled_at=at)
        self.assertEqual(report["engagements"], 1)
        self.assertEqual(report["matches_with_clv"], 0)
        self.assertEqual(report["economics"]["settled_engagements"], 1)
        self.assertLess(report["economics"]["net_pnl_total_usd"], 0)

    def test_rescheduled_match_stays_in_pnl(self):
        pins, quotes, settled, at = book(1, settle=0.0)
        pins.append(pin(pins[0]["observed_at"], "E0", "2026-10-09T20:00:00+00:00"))
        report = f.evaluate(pins, quotes, settled, LATE, settled_at=at)
        self.assertEqual(report["engagements"], 1)
        self.assertEqual(report["economics"]["settled_engagements"], 1)

    def test_no_pass_while_an_engagement_of_the_prefix_is_unsettled(self):
        pins, quotes, settled, at = book(60)
        del settled["KALSHI|K5|None"]
        report = f.evaluate(pins, quotes, settled, LATE, settled_at=at, decision_test=ACCEPT)
        self.assertEqual(report["status"], "ACCEPT_PENDING_SETTLEMENT")
        settled["KALSHI|K5|None"] = 1.0
        report = f.evaluate(pins, quotes, settled, LATE, settled_at=at, decision_test=ACCEPT)
        self.assertEqual(report["status"], "FORWARD_PASS(PRICE)")

    def test_pnl_far_below_clv_is_rejected(self):
        pins, quotes, settled, at = book(60, settle=0.0)
        report = f.evaluate(pins, quotes, settled, LATE, settled_at=at, decision_test=ACCEPT)
        self.assertEqual(report["status"], "REJECT(PNL_BELOW_CLV)")

    def test_more_than_ten_percent_missing_close_is_inconclusive(self):
        pins, quotes, settled, at = book(40)
        quotes = [q for q in quotes if not (q["best_bid"] is not None and q["market"] in
                                            {f"K{i}" for i in range(5)})] if False else \
            [q for q in quotes if q.get("best_bid") is None or int(q["ticker"][1:]) >= 5]
        report = f.evaluate(pins, quotes, settled, LATE, settled_at=at, decision_test=ACCEPT)
        self.assertEqual(report["status"], "INCONCLUSIVE(DATA)")

    def test_no_decision_without_the_12b_eprocess(self):
        pins, quotes, settled, at = book(300)
        report = f.evaluate(pins, quotes, settled, LATE, settled_at=at)
        self.assertEqual(report["status"], "SHADOW_DIRECT")
        self.assertIn("ACCEPT", report["t_sprt_indicator_only"]["decision"])

    def test_replay_identical_and_sticky(self):
        pins, quotes, settled, at = book(30)
        one = f.evaluate(pins, quotes, settled, LATE, settled_at=at)
        self.assertEqual(one, f.evaluate(list(pins), list(quotes), dict(settled), LATE,
                                         settled_at=dict(at)))
        frozen = {"status": "REJECT(FORWARD)"}
        self.assertTrue(f.evaluate(pins, quotes, settled, LATE, frozen, at)["sticky"])

    def test_prefix_includes_engagements_without_clv_and_n_ge_2(self):
        pins, quotes, settled, at = book(40)
        # match E3 loses its close quote: its engagement must still be in the prefix
        quotes = [q for q in quotes if not (q.get("best_bid") is not None and q["ticker"] == "K3")]
        del settled["KALSHI|K3|None"]
        report = f.evaluate(pins, quotes, settled, LATE, settled_at=at, decision_test=ACCEPT)
        self.assertEqual(report["status"], "ACCEPT_PENDING_SETTLEMENT")

    def test_ledger_engagements_cannot_be_dropped_later(self):
        pins, quotes, settled, at = book(5, settle=0.0)
        ledger = f.find_bets(pins, quotes)
        report = f.evaluate(pins, [], settled, LATE, settled_at=at, ledger=ledger)
        self.assertEqual(report["engagements"], 5)       # quotes gone, engagements kept

    def test_economics_reported(self):
        pins, quotes, settled, at = book(10)
        eco = f.evaluate(pins, quotes, settled, LATE, settled_at=at)["economics"]
        self.assertGreater(eco["net_pnl_total_usd"], 0)
        self.assertGreater(eco["annualised_return_on_locked_capital"], 0)
        self.assertEqual(len(eco["pnl_ci95_per_contract"]), 2)

    def test_settlement_resolution(self):
        bet = {"venue": "KALSHI", "market": "K1"}
        self.assertEqual(f._settlement(bet, lambda u: {"market": {"status": "settled",
                                                                  "result": "yes"}}), 1.0)
        self.assertIsNone(f._settlement(bet, lambda u: {"market": {"status": "active"}}))


class RelayTests(unittest.TestCase):
    def test_kalshi_live_book_format(self):
        from quant.dataplane.h001_relay import parse_kalshi_orderbook
        live = {"orderbook_fp": {"yes_dollars": [["0.40", "20"]], "no_dollars": [["0.58", "120"]]}}
        parsed = parse_kalshi_orderbook(live, "K")
        self.assertAlmostEqual(parsed["best_ask"], 0.42)
        self.assertEqual(parsed["ask_depth"], 120)
        legacy = {"orderbook": {"yes": [[40, 20]], "no": [[58, 120]]}}
        self.assertAlmostEqual(parse_kalshi_orderbook(legacy, "K")["best_ask"], 0.42)

    def test_unreachable_pinnacle_fetch_is_counted(self):
        from quant.dataplane.adapters import DataUnavailable
        from quant.dataplane.h001_relay import fetch_pinnacle
        def boom(url):
            raise DataUnavailable("timeout")
        records, meta = fetch_pinnacle("soccer_epl", "KEY-NOT-REAL", fetch=boom)
        self.assertEqual(records, [])
        self.assertTrue(meta.get("charged"))
        self.assertNotIn("KEY-NOT-REAL", json.dumps(meta))


if __name__ == "__main__":
    unittest.main()

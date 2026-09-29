"""H-001 corrected forward evaluation (SHADOW_DIRECT k=1). Fixture numbers are INVENTED."""

from __future__ import annotations

import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "research" / "fast_rail" / "h001"))
import forward as f  # noqa: E402

T0 = "2026-10-01T12:00:00+00:00"          # invented run time, after PRISTINE_AFTER
KICK = "2026-10-01T15:00:00+00:00"


def pin(stamp, home=2.0, away=2.0, event="E1"):
    return {"event_id": event, "observed_at": stamp, "commence_time": KICK,
            "prices": {"Home": home, "Away": away}}


def quote(stamp, venue, ask, outcome="Home", event="E1", market="M"):
    return {"odds_event_id": event, "observed_at": stamp, "venue": venue, "outcome": outcome,
            "best_ask": ask, "ticker" if venue == "KALSHI" else "market_id": market,
            "token_id": None if venue == "KALSHI" else "tok"}


class ForwardTests(unittest.TestCase):
    def test_exact_fees_with_rounding(self):
        # Kalshi: ceil_to_cent(0.07*100*0.5*0.5 = 1.75) = 1.75 -> 0.0175 per contract.
        self.assertAlmostEqual(f.fee_per_contract("KALSHI", 0.5), 0.0175)
        # 0.07*100*0.33*0.67 = 1.5477 -> ceil 1.55 -> 0.0155.
        self.assertAlmostEqual(f.fee_per_contract("KALSHI", 0.33), 0.0155)
        # One contract pays a whole cent: rounding is per order.
        self.assertAlmostEqual(f.fee_per_contract("KALSHI", 0.5, contracts=1), 0.02)
        # Polymarket sports: 0.05*100*0.25 = 1.25 -> 0.0125.
        self.assertAlmostEqual(f.fee_per_contract("POLYMARKET", 0.5), 0.0125)

    def test_quotes_before_pristine_never_count(self):
        early = "2026-09-29T11:00:00+00:00"
        bets = f.find_bets([pin(early)], [quote(early, "KALSHI", 0.40)])
        self.assertEqual(bets, [])

    def test_kalshi_priority_and_fee_below_gap(self):
        pins = [pin(T0)]                                   # fair 0.5 / 0.5
        bets = f.find_bets(pins, [quote(T0, "POLYMARKET", 0.44), quote(T0, "KALSHI", 0.45)])
        self.assertEqual([b["venue"] for b in bets], ["KALSHI"])
        # Gap 0.03 but net edge < 0.02 after the fee: no bet.
        self.assertEqual(f.find_bets(pins, [quote(T0, "KALSHI", 0.47)]), [])

    def test_no_quote_after_kickoff_and_same_run_only(self):
        late = "2026-10-01T15:30:00+00:00"
        self.assertEqual(f.find_bets([pin(T0)], [quote(late, "KALSHI", 0.40)]), [])

    def test_settlement_uses_venue_resolution_and_never_fills(self):
        bet = {"venue": "KALSHI", "market": "K1"}
        self.assertEqual(f._settlement(bet, lambda url: {"market": {"status": "settled",
                                                                    "result": "yes"}}), 1.0)
        self.assertIsNone(f._settlement(bet, lambda url: {"market": {"status": "active"}}))
        pm = {"venue": "POLYMARKET", "market": "0xabc", "token_id": "t2"}
        rows = [{"closed": True, "clobTokenIds": '["t1","t2"]', "outcomePrices": '["1","0"]'}]
        self.assertEqual(f._settlement(pm, lambda url: rows), 0.0)
        rows[0]["outcomePrices"] = '["0.5","0.5"]'
        self.assertEqual(f._settlement(pm, lambda url: rows), 0.5)      # void settles at 0.5
        rows[0]["outcomePrices"] = '["0.7","0.3"]'
        self.assertIsNone(f._settlement(pm, lambda url: rows))

    def _book(self, venue_close_mid, pnl_value, n=500):
        """Invented: n matches, entry ask 0.40 vs fair 0.5, later venue quote at mid."""
        pins, quotes, settled = [], [], {}
        for i in range(n):
            ev = f"E{i}"
            day = f"2026-{10 + i // 250:02d}-{1 + (i % 250) // 10:02d}"
            entry, later, kick = (f"{day}T0{i % 10}:00:00+00:00", f"{day}T1{i % 10}:00:00+00:00",
                                  f"{day}T2{i % 4}:00:00+00:00")
            for stamp in (entry, later):
                pins.append({"event_id": ev, "observed_at": stamp, "commence_time": kick,
                             "prices": {"Home": 2.0, "Away": 2.0}})
            quotes.append(quote(entry, "KALSHI", 0.40, event=ev, market=f"K{i}"))
            quotes.append({**quote(later, "KALSHI", venue_close_mid + 0.01, event=ev,
                                   market=f"K{i}"), "best_bid": venue_close_mid - 0.01})
            settled[f"KALSHI|K{i}|None"] = pnl_value
        return pins, quotes, settled

    def test_statistic_is_not_positive_by_construction(self):
        # Red-team HIGH: Pinnacle unchanged, venue price unchanged -> mean = -fee < 0.
        pins, quotes, settled = self._book(venue_close_mid=0.40, pnl_value=0.0, n=60)
        report = f.evaluate(pins, quotes, settled, datetime(2027, 1, 1, tzinfo=timezone.utc))
        self.assertLess(report["mean_net_clv"], 0)

    def test_proxy_rule_frozen_and_needs_positive_pnl(self):
        now = datetime(2027, 1, 1, tzinfo=timezone.utc)
        pins, quotes, settled = self._book(venue_close_mid=0.48, pnl_value=0.0)
        report = f.evaluate(pins, quotes, settled, now)
        self.assertEqual(report["t_sprt"]["decision"], "ACCEPT_EDGE")
        self.assertEqual(report["status"], "ACCEPT_PENDING_PNL")
        pins, quotes, settled = self._book(venue_close_mid=0.48, pnl_value=1.0)
        self.assertEqual(f.evaluate(pins, quotes, settled, now)["status"], "FORWARD_PASS")

    def test_terminal_decision_is_sticky(self):
        frozen = {"status": "REJECT(FORWARD)", "matches": 40}
        pins, quotes, settled = self._book(venue_close_mid=0.48, pnl_value=1.0)
        out = f.evaluate(pins, quotes, settled, datetime(2027, 1, 1, tzinfo=timezone.utc), frozen)
        self.assertEqual(out["status"], "REJECT(FORWARD)")
        self.assertTrue(out["sticky"])

    def test_rescheduled_match_is_dropped(self):
        pins, quotes, settled = self._book(venue_close_mid=0.48, pnl_value=1.0, n=1)
        pins.append({**pins[0], "observed_at": pins[0]["observed_at"],
                     "commence_time": "2026-10-09T20:00:00+00:00"})
        report = f.evaluate(pins, quotes, settled, datetime(2027, 1, 1, tzinfo=timezone.utc))
        self.assertEqual(report["matches"], 0)

    def test_polymarket_depth_and_staleness(self):
        base = {**quote(T0, "POLYMARKET", 0.40), "fetched_at": T0}
        thin = {**base, "asks": [[0.40, 5]]}
        deep = {**base, "asks": [[0.40, 150]]}
        stale = {**deep, "fetched_at": "2026-10-01T12:10:00+00:00"}
        self.assertEqual(f.find_bets([pin(T0)], [thin]), [])
        self.assertEqual(len(f.find_bets([pin(T0)], [deep])), 1)
        self.assertEqual(f.find_bets([pin(T0)], [stale]), [])

    def test_declaration_constants(self):
        self.assertAlmostEqual(f.ALPHA, 0.025)
        self.assertAlmostEqual(f.H1_EFFECT, 0.00475)
        self.assertGreaterEqual(f.PRISTINE_AFTER, "2026-09-29T14:00:00+00:00")


if __name__ == "__main__":
    unittest.main()


class BudgetLedgerTests(unittest.TestCase):
    def test_unreachable_pinnacle_fetch_is_still_counted(self):
        from quant.dataplane.adapters import DataUnavailable
        from quant.dataplane.h001_relay import fetch_pinnacle
        def boom(url):
            raise DataUnavailable("timeout")
        records, meta = fetch_pinnacle("soccer_epl", "KEY-NOT-REAL", fetch=boom)
        self.assertEqual(records, [])
        self.assertTrue(meta.get("charged"))
        self.assertNotIn("KEY-NOT-REAL", json.dumps(meta))

"""Fast-lane census: outcome blindness and PIT cluster semantics (synthetic events)."""

import unittest
from datetime import date, timedelta

from quant.fastlane import census as cs


def event(acc, issuer, day, owners, value=50_000.0, lag=2, ticker="SYNA"):
    return {
        "accession": acc, "issuer_cik": issuer, "filing_date": day.isoformat(),
        "value_usd": value, "filing_lag_days": lag, "ticker_as_filed": ticker,
        "owners": [{"owner_cik": cik, "role_class": role,
                    "officer_or_director": role in ("CEO_CFO", "OTHER_OFFICER", "DIRECTOR"),
                    "is_director": role == "DIRECTOR",
                    "is_ten_percent_owner": role == "TEN_PERCENT_OWNER"}
                   for cik, role in owners],
    }


def walk_keys(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from walk_keys(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk_keys(v)


class OutcomeBlindTests(unittest.TestCase):
    def sample(self):
        d = date(2010, 3, 1)
        return [event("a1", "I1", d, [("O1", "DIRECTOR")]),
                event("a2", "I1", d + timedelta(days=3), [("O2", "CEO_CFO")], value=2e6),
                event("a3", "I2", date(2020, 5, 4), [("O3", "TEN_PERCENT_OWNER")]),
                event("a4", "I3", date(2023, 1, 9), [("O4", "OTHER_OFFICER")], ticker="N/A")]

    def test_census_schema_has_no_price_or_return_fields(self):
        body = cs.census(self.sample())
        doc = {"schema": cs.CENSUS_SCHEMA, "definitions": cs.definitions(), **body}
        cs.assert_outcome_blind(doc)
        forbidden = ("price", "return", "market_cap", "mcap", "delist", "close", "volume",
                     "alpha", "sharpe", "pnl", "excess")
        for key in walk_keys(doc):
            for token in forbidden:
                self.assertNotIn(token, str(key).lower(), key)
        for field in cs.CENSUS_INPUT_FIELDS:
            for token in forbidden:
                self.assertNotIn(token, field)

    def test_guard_rejects_an_outcome_key_anywhere(self):
        with self.assertRaises(cs.OutcomeLeak):
            cs.assert_outcome_blind({"by_split": {"holdout": [{"fwd_return_20d": 0.1}]}})
        with self.assertRaises(cs.OutcomeLeak):
            cs.assert_outcome_blind({"x": {"Market_Cap": 1}})

    def test_census_counts_by_split_and_family(self):
        body = cs.census(self.sample())
        disc = body["by_split"]["discovery"]
        self.assertEqual(disc["ALL_P"]["issuer_days"], 2)
        self.assertEqual(disc["OD"]["unique_issuers"], 1)
        self.assertEqual(disc["CEO_CFO"]["issuer_days"], 1)
        self.assertEqual(disc["OD_CLUSTER_10CD"]["issuer_days"], 1)
        self.assertEqual(body["by_split"]["walk_forward"]["OD"]["issuer_days"], 0)
        self.assertEqual(body["by_split"]["walk_forward"]["ALL_P"]["issuer_days"], 1)
        self.assertEqual(body["by_split"]["holdout"]["OD"]
                         ["ticker_as_filed_nonstandard_issuer_days"], 1)
        self.assertEqual(disc["ALL_P"]["value_tiers_issuer_days"]["ge_1m"], 1)


class ClusterSemanticsTests(unittest.TestCase):
    def rows(self, family, events):
        evs = [cs.compact(e) for e in events]
        return cs.family_days(family, evs)

    def test_calendar_cluster_crossing_no_repeat_while_active_then_rearm(self):
        d0 = date(2012, 6, 4)
        days = lambda n: d0 + timedelta(days=n)  # noqa: E731
        events = [
            event("a1", "I1", days(0), [("O1", "DIRECTOR")]),
            event("a2", "I1", days(2), [("O2", "DIRECTOR")]),    # <2 -> 2: formation
            event("a3", "I1", days(4), [("O3", "DIRECTOR")]),    # window active: none
            event("a4", "I1", days(11), [("O4", "DIRECTOR")]),   # O1 expired, O2/O3 keep >=2
            event("a5", "I1", days(40), [("O5", "DIRECTOR")]),   # all expired: re-armed
            event("a6", "I1", days(41), [("O6", "DIRECTOR")]),   # formation again
        ]
        formed = self.rows("OD_CLUSTER_10CD", events)
        self.assertEqual([r.day for r in formed], [days(2), days(41)])

    def test_expiry_before_additions_rearms_within_the_same_day(self):
        # D07 WINDOW_EXPIRY_PRECEDES_SESSION_ADDITIONS: at day 11 the day-0 owner expires,
        # the count falls to 1 (re-arm), then the day-11 owner makes a genuine new crossing.
        d0 = date(2012, 6, 4)
        events = [event("a1", "I1", d0, [("O1", "DIRECTOR")]),
                  event("a2", "I1", d0 + timedelta(days=9), [("O2", "DIRECTOR")]),
                  event("a3", "I1", d0 + timedelta(days=11), [("O3", "DIRECTOR")])]
        formed = self.rows("OD_CLUSTER_10CD", events)
        self.assertEqual([r.day for r in formed],
                         [d0 + timedelta(days=9), d0 + timedelta(days=11)])

    def test_ten_calendar_day_window_excludes_day_ten(self):
        d0 = date(2012, 6, 4)
        events = [event("a1", "I1", d0, [("O1", "DIRECTOR")]),
                  event("a2", "I1", d0 + timedelta(days=10), [("O2", "DIRECTOR")])]
        self.assertEqual(self.rows("OD_CLUSTER_10CD", events), [])

    def test_same_owner_twice_is_not_a_cluster_and_ten_pct_does_not_qualify(self):
        d0 = date(2012, 6, 4)
        events = [event("a1", "I1", d0, [("O1", "DIRECTOR")]),
                  event("a2", "I1", d0 + timedelta(days=1), [("O1", "DIRECTOR")]),
                  event("a3", "I1", d0 + timedelta(days=2), [("O9", "TEN_PERCENT_OWNER")])]
        self.assertEqual(self.rows("OD_CLUSTER_10CD", events), [])

    def test_frozen_proxy_uses_ten_weekdays(self):
        monday = date(2012, 6, 4)
        # 11 calendar days later (next Friday) is the 10th weekday counting the Monday,
        # so the Monday is inside W(S) = S plus the 9 preceding weekdays.
        events = [event("a1", "I1", monday, [("O1", "OTHER_OFFICER")]),
                  event("a2", "I1", monday + timedelta(days=11), [("O2", "DIRECTOR")])]
        self.assertEqual(len(self.rows("FROZEN_FV_PROXY_10WD", events)), 1)
        self.assertEqual(self.rows("OD_CLUSTER_10CD", events), [])
        # 14 calendar days later (the 11th weekday) is outside the 10-session window.
        events[1] = event("a2", "I1", monday + timedelta(days=14), [("O2", "DIRECTOR")])
        self.assertEqual(self.rows("FROZEN_FV_PROXY_10WD", events), [])

    def test_weekday_index(self):
        fri, sat, mon = date(2012, 6, 8), date(2012, 6, 9), date(2012, 6, 11)
        self.assertEqual(cs.weekday_index(mon) - cs.weekday_index(fri), 1)
        self.assertEqual(cs.weekday_index(sat), cs.weekday_index(mon))

    def test_lag_distribution(self):
        dist = cs.lag_distribution([1, 2, 3, 40, None, -1])
        self.assertEqual(dist["n"], 5)
        self.assertEqual(dist["missing"], 1)
        self.assertEqual(dist["negative"], 1)
        self.assertEqual(dist["p50"], 2)
        self.assertEqual(dist["share_gt_30d"], 0.2)


if __name__ == "__main__":
    unittest.main()

"""Fast-lane price-vendor contract and friction functions (synthetic numbers only)."""

import math
import tempfile
import unittest
from datetime import date
from pathlib import Path

from quant.fastlane import frictions as fr
from quant.fastlane import prices as px
from quant.fastlane import preregistration as pr
from quant.fastlane.firewall import Firewall
from tests.test_fastlane_firewall_prereg import final_protocol

PARAMS = {
    "spread": {"variant": "two_day_corrected_mean", "min_pairs": 2,
               "adv20_bucket_floor_bps": [{"adv_below_usd": 1e6, "floor_bps": 150.0},
                                          {"adv_below_usd": 1e8, "floor_bps": 20.0},
                                          {"adv_below_usd": None, "floor_bps": 5.0}]},
    "commission": {"per_share_usd": 0.005, "minimum_usd": 1.0, "max_fraction_of_notional": 0.01},
    "impact": {"coefficient": 1.0},
    "participation_cap_adv20": 0.001,
    "missing_delisting_return": {"base": -0.30, "stress": -1.00},
}


class AttestationTests(unittest.TestCase):
    def test_vendor_without_delisted_names_can_never_yield_go(self):
        att = px.VendorAttestation("SYNTH_SURVIVOR_ONLY", includes_delisted=False,
                                   corporate_actions="RAW_PRICES_PLUS_ACTIONS_LEDGER",
                                   pit_security_mapping=True, license_note="synthetic",
                                   verified=True)
        self.assertEqual(att.evidence_label, px.LABEL_SURVIVORSHIP_BIASED)
        self.assertFalse(att.go_eligible)
        verdict = px.resolve_verdict(att, criteria_met=True)
        self.assertEqual(verdict["verdict"], px.VERDICT_NOT_GO_ELIGIBLE)
        self.assertEqual(verdict["evidence_label"], "DEVELOPMENT_SURVIVORSHIP_BIASED")

    def test_only_complete_verified_attestation_is_go_eligible(self):
        base = dict(vendor_id="SYNTH", includes_delisted=True,
                    corporate_actions="RAW_PRICES_PLUS_ACTIONS_LEDGER",
                    pit_security_mapping=True, license_note="synthetic")
        self.assertEqual(px.resolve_verdict(px.VendorAttestation(**base, verified=True), True)
                         ["verdict"], px.VERDICT_GO)
        self.assertEqual(px.resolve_verdict(px.VendorAttestation(**base, verified=True), False)
                         ["verdict"], px.VERDICT_NO_GO)
        for change in ({"verified": False}, {"pit_security_mapping": False, "verified": True},
                       {"corporate_actions": "ADJUSTED_ONLY", "verified": True}):
            att = px.VendorAttestation(**{**base, **change})
            self.assertEqual(att.evidence_label, px.LABEL_PIT_INCOMPLETE)
            self.assertNotEqual(px.resolve_verdict(att, True)["verdict"], px.VERDICT_GO)


class SharadarSkeletonTests(unittest.TestCase):
    def test_requires_api_key(self):
        with self.assertRaises(px.VendorUnavailable):
            px.SharadarVendor(env={})
        vendor = px.SharadarVendor(env={"NASDAQ_DATA_LINK_API_KEY": "synthetic-key"})
        self.assertIsInstance(vendor, px.PriceVendor)
        self.assertFalse(vendor.attestation().go_eligible)       # unverified claims

    def test_data_calls_need_a_grant_inside_the_split_window(self):
        vendor = px.SharadarVendor(env={"NASDAQ_DATA_LINK_API_KEY": "synthetic-key"})
        with self.assertRaises(pr.OutcomeAccessRefused):
            vendor.daily_bars("SYN", date(2010, 1, 4), date(2010, 2, 1), grant=None)
        with tempfile.TemporaryDirectory() as tmp:
            fw = Firewall(Path(tmp))
            sha = pr.seal_protocol(fw, final_protocol())["protocol_sha256"]
            grant = pr.require_outcome_access(fw, "discovery", sha)
            # forbidden interval: holdout-period prices under a discovery grant
            with self.assertRaises(pr.OutcomeAccessRefused):
                vendor.daily_bars("SYN", date(2021, 7, 1), date(2021, 8, 2), grant=grant)
            with self.assertRaises(pr.OutcomeAccessRefused):
                vendor.sessions(date(2018, 12, 1), date(2019, 1, 31), grant=grant)
            with self.assertRaises(px.VendorUnavailable):        # allowed, but no network
                vendor.daily_bars("SYN", date(2010, 1, 4), date(2010, 2, 1), grant=grant)


class EntrySessionTests(unittest.TestCase):
    SESSIONS = [date(2012, 6, 7), date(2012, 6, 8), date(2012, 6, 11), date(2012, 6, 13)]

    def test_entry_is_strictly_after_the_filing_date(self):
        f = px.first_session_strictly_after
        self.assertEqual(f(date(2012, 6, 7), self.SESSIONS), date(2012, 6, 8))   # never same day
        self.assertEqual(f(date(2012, 6, 8), self.SESSIONS), date(2012, 6, 11))  # Fri -> Mon
        self.assertEqual(f(date(2012, 6, 11), self.SESSIONS), date(2012, 6, 13))  # vendor gap
        self.assertIsNone(f(date(2012, 6, 13), self.SESSIONS))                   # unresolved
        with self.assertRaises(ValueError):
            f(date(2012, 6, 7), [date(2012, 6, 8), date(2012, 6, 8)])


class FrictionTests(unittest.TestCase):
    def setUp(self):
        self.p = fr.FrictionParams.from_protocol(PARAMS)

    def test_abdi_ranaldo_matches_hand_computation(self):
        high, low, close = [10.2, 10.4, 10.3], [9.8, 10.0, 9.9], [10.1, 10.0, 10.2]
        eta = [(math.log(h) + math.log(l)) / 2 for h, l in zip(high, low)]
        c = [math.log(x) for x in close]
        s2 = [4 * (c[t] - eta[t]) * (c[t] - eta[t + 1]) for t in range(2)]
        expected = sum(math.sqrt(max(v, 0)) for v in s2) / 2
        got = fr.abdi_ranaldo_spread(high, low, close, variant="two_day_corrected_mean",
                                     min_pairs=2)
        self.assertAlmostEqual(got, expected, places=12)
        pooled = fr.abdi_ranaldo_spread(high, low, close, variant="pooled", min_pairs=2)
        self.assertAlmostEqual(pooled, math.sqrt(max(sum(s2) / 2, 0)), places=12)
        self.assertIsNone(fr.abdi_ranaldo_spread(high[:2], low[:2], close[:2],
                                                 variant="pooled", min_pairs=2))
        with self.assertRaises(ValueError):
            fr.abdi_ranaldo_spread([10.0, float("nan")], [9.0, 9.0], [9.5, 9.5],
                                   variant="pooled", min_pairs=1)

    def test_floor_by_adv_bucket(self):
        self.assertEqual(fr.effective_spread(0.0001, 5e5, self.p), 0.015)
        self.assertEqual(fr.effective_spread(0.05, 5e5, self.p), 0.05)
        self.assertEqual(fr.effective_spread(None, 5e8, self.p), 0.0005)

    def test_commission_minimum_and_cap(self):
        self.assertEqual(fr.commission_usd(100, 1000.0, self.p), 1.0)          # minimum
        self.assertAlmostEqual(fr.commission_usd(10_000, 50_000.0, self.p), 50.0)
        self.assertAlmostEqual(fr.commission_usd(1000, 50.0, self.p), 0.5)     # 1% cap
        self.assertEqual(fr.commission_usd(0, 0.0, self.p), 0.0)

    def test_sqrt_impact_and_participation_cap(self):
        self.assertAlmostEqual(fr.sqrt_impact_fraction(10_000, 1e7, 0.02, 1.0),
                               0.02 * math.sqrt(0.001))
        self.assertEqual(fr.participation_capped_notional(5_000, 1e6, 0.001), 1_000.0)
        self.assertEqual(fr.participation_capped_notional(500, 1e6, 0.001), 500.0)
        with self.assertRaises(ValueError):
            fr.participation_capped_notional(500, float("inf"), 0.001)

    def test_delisting_and_parameters_come_from_protocol(self):
        self.assertEqual(fr.missing_delisting_return("base", self.p), -0.30)
        self.assertEqual(fr.missing_delisting_return("stress", self.p), -1.00)
        broken = {**PARAMS, "spread": {**PARAMS["spread"], "adv20_bucket_floor_bps": [
            {"adv_below_usd": 1e6, "floor_bps": 10.0}]}}
        with self.assertRaises(ValueError):
            fr.FrictionParams.from_protocol(broken)
        with self.assertRaises(KeyError):
            fr.FrictionParams.from_protocol({k: v for k, v in PARAMS.items() if k != "impact"})


if __name__ == "__main__":
    unittest.main()

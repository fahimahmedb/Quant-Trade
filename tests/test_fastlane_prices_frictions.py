"""Fast-lane price-vendor contract, verdict rules, frictions and slot tie-break.

Synthetic numbers only; nothing here is market evidence.
"""

import hashlib
import math
import statistics
import tempfile
import unittest
from datetime import date

from quant.fastlane import constructor as ct
from quant.fastlane import frictions as fr
from quant.fastlane import preregistration as pr
from quant.fastlane import prices as px
from quant.fastlane.firewall import LINEAGE_ID
from quant.fastlane.protocol_draft import FRICTIONS, portfolio_mde_annual
from tests.test_fastlane_firewall_prereg import World


class AttestationAndVerdictTests(unittest.TestCase):
    BASE = dict(vendor_id="SYNTH", includes_delisted=True,
                corporate_actions="RAW_PRICES_PLUS_ACTIONS_LEDGER",
                pit_security_mapping=True, license_note="synthetic")

    def test_vendor_without_delisted_names_can_never_yield_go(self):
        att = px.VendorAttestation(**{**self.BASE, "includes_delisted": False}, verified=True)
        self.assertEqual(att.evidence_label, px.LABEL_SURVIVORSHIP_BIASED)
        self.assertFalse(att.go_eligible)
        verdict = px.resolve_verdict(att, criteria_met=True)
        self.assertEqual(verdict["verdict"], px.VERDICT_NOT_GO_ELIGIBLE)
        self.assertEqual(verdict["evidence_label"], "DEVELOPMENT_SURVIVORSHIP_BIASED")
        self.assertFalse(verdict["sizing_authorized"])

    def test_only_complete_verified_attestation_is_go_eligible(self):
        ok = px.VendorAttestation(**self.BASE, verified=True)
        self.assertEqual(px.resolve_verdict(ok, True)["verdict"], px.VERDICT_GO)
        self.assertTrue(px.resolve_verdict(ok, True)["sizing_authorized"])
        for change in ({"verified": False}, {"pit_security_mapping": False, "verified": True},
                       {"corporate_actions": "ADJUSTED_ONLY", "verified": True}):
            att = px.VendorAttestation(**{**self.BASE, **change})
            self.assertEqual(att.evidence_label, px.LABEL_PIT_INCOMPLETE)
            self.assertNotEqual(px.resolve_verdict(att, True)["verdict"], px.VERDICT_GO)

    def test_inconclusive_is_distinct_from_no_go_and_never_sizes(self):
        ok = px.VendorAttestation(**self.BASE, verified=True)
        inc = px.resolve_verdict(ok, False, ci_upper_annual=0.05)
        self.assertEqual(inc["verdict"], px.VERDICT_INCONCLUSIVE)
        self.assertFalse(inc["sizing_authorized"])
        self.assertEqual(px.resolve_verdict(ok, False, ci_upper_annual=0.02)["verdict"],
                         px.VERDICT_NO_GO)
        self.assertEqual(px.resolve_verdict(ok, False, ci_upper_annual=0.03)["verdict"],
                         px.VERDICT_INCONCLUSIVE)

    def test_zero_finalists_is_no_go_with_holdout_unopened(self):
        ok = px.VendorAttestation(**self.BASE, verified=True)
        verdict = px.resolve_verdict(ok, True, n_finalists=0)
        self.assertEqual((verdict["verdict"], verdict["holdout"]), (px.VERDICT_NO_GO, "UNOPENED"))

    def test_vendor_manifests(self):
        good = {"lineage": LINEAGE_ID, "vendor_id": "SYNTH", "mapping": {"A": "STOCK_MERGER"},
                "derivation": "VENDOR_DOCUMENTATION_ONLY",
                "source": {"documentation_url": "https://example.invalid/doc",
                           "retrieved_on": "2026-09-24"}}
        self.assertEqual(px.validate_delisting_map(good), {"A": "STOCK_MERGER"})
        for bad in ({**good, "mapping": {"A": "LIQUIDATION"}}, {**good, "mapping": {}},
                    {**good, "lineage": "OTHER"}, {**good, "derivation": "FITTED_ON_RETURNS"},
                    {**good, "source": {"documentation_url": "https://x"}},
                    {**good, "source": {"retrieved_on": "2026-09-24"}}):
            with self.assertRaises(ValueError):
                px.validate_delisting_map(bad)
        bench = {"lineage": LINEAGE_ID, "series": "SPY", "return_type": "TOTAL_RETURN",
                 "vendor_id": "SYNTH", "dataset": "SYNTH/SEP", "fallback": "NONE"}
        px.validate_benchmark_manifest(bench)
        for bad in ({**bench, "fallback": "YAHOO"}, {**bench, "return_type": "PRICE"},
                    {**bench, "series": "IVV"}):
            with self.assertRaises(ValueError):
                px.validate_benchmark_manifest(bad)


class SharadarSkeletonTests(unittest.TestCase):
    def test_requires_api_key(self):
        with self.assertRaises(px.VendorUnavailable):
            px.SharadarVendor(env={})
        vendor = px.SharadarVendor(env={"NASDAQ_DATA_LINK_API_KEY": "synthetic-key"})
        self.assertIsInstance(vendor, px.PriceVendor)
        self.assertFalse(vendor.attestation().go_eligible)       # unverified claims

    def test_data_calls_need_a_real_grant_inside_the_window(self):
        vendor = px.SharadarVendor(env={"NASDAQ_DATA_LINK_API_KEY": "synthetic-key"})
        with self.assertRaises(pr.OutcomeAccessRefused):
            vendor.daily_bars("SYN", date(2010, 1, 4), date(2010, 2, 1), grant=None)
        with tempfile.TemporaryDirectory() as tmp:
            w = World(tmp)
            grant = pr.require_outcome_access(w.fw, "discovery", w.sha)
            with self.assertRaises(pr.OutcomeAccessRefused):
                vendor.daily_bars("SYN", date(2021, 7, 1), date(2021, 8, 2), grant=grant)
            with self.assertRaises(px.VendorUnavailable):        # allowed, but no network
                vendor.daily_bars("SYN", date(2010, 1, 4), date(2010, 2, 1), grant=grant)

    def test_security_mappings_are_clipped_to_the_grant_window(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = World(tmp)
            grant = pr.require_outcome_access(w.fw, "discovery", w.sha)
            maps = [px.SecurityMapping("1", "S1", "OLD", date(2001, 1, 2), date(2012, 5, 1)),
                    px.SecurityMapping("1", "S2", "NEW", date(2012, 5, 2), None),
                    px.SecurityMapping("1", "S3", "LATER", date(2022, 1, 3), None)]
            clipped = px.clip_mappings(maps, grant)
            self.assertEqual([m.security_id for m in clipped], ["S1", "S2"])
            self.assertEqual(clipped[1].valid_to, date(2018, 12, 31))
            self.assertEqual(clipped[0].valid_to, date(2012, 5, 1))


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
        self.p = fr.FrictionParams.from_protocol(FRICTIONS)

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

    def test_frozen_adv_bucket_floors(self):
        cases = [(300_000, 0.025), (500_000, 0.012), (1_999_999, 0.012), (2_000_000, 0.006),
                 (9_000_000, 0.006), (10_000_000, 0.003), (49_000_000, 0.003),
                 (50_000_000, 0.001), (5e9, 0.001)]
        for adv, floor in cases:
            self.assertAlmostEqual(fr.effective_spread(0.0, adv, self.p), floor, msg=str(adv))
        self.assertEqual(fr.effective_spread(0.05, 5e8, self.p), 0.05)
        self.assertEqual(fr.effective_spread(None, 5e8, self.p), 0.001)

    def test_untradeable_below_100k_adv(self):
        self.assertFalse(fr.is_tradeable(99_999.0, self.p))
        self.assertTrue(fr.is_tradeable(100_000.0, self.p))
        with self.assertRaises(ValueError):
            fr.one_side_cost_usd(500.0, 50, 99_000.0, 0.02, None, self.p)

    def test_commission_per_share_with_minimum(self):
        self.assertAlmostEqual(fr.commission_usd(50, 500.0, self.p), 0.35)      # minimum
        self.assertAlmostEqual(fr.commission_usd(1000, 10_000.0, self.p), 3.5)
        self.assertEqual(fr.commission_usd(0, 0.0, self.p), 0.0)

    def test_sqrt_impact_participation_and_stress(self):
        self.assertAlmostEqual(fr.sqrt_impact_fraction(10_000, 1e7, 0.02, 1.0),
                               0.02 * math.sqrt(0.001))
        self.assertEqual(fr.participation_capped_notional(5_000, 1e6, 0.001), 1_000.0)
        base = fr.one_side_cost_usd(1000.0, 100, 2e6, 0.02, 0.004, self.p)
        stress = fr.one_side_cost_usd(1000.0, 100, 2e6, 0.02, 0.004, self.p, stress=True)
        self.assertAlmostEqual(stress["total_usd"], 2.0 * base["total_usd"])
        with self.assertRaises(ValueError):
            fr.participation_capped_notional(500, float("inf"), 0.001)

    def test_delisting_classes_come_from_the_protocol(self):
        self.assertEqual(fr.delisting_extra_return("UNKNOWN", "base", self.p), -0.30)
        self.assertEqual(fr.delisting_extra_return("UNKNOWN", "stress", self.p), -1.00)
        self.assertEqual(fr.delisting_extra_return("BANKRUPTCY_OR_CAUSE", "base", self.p), -1.0)
        self.assertEqual(fr.delisting_extra_return("CASH_ACQUISITION", "stress", self.p), 0.0)
        self.assertEqual(fr.delisting_extra_return("STOCK_MERGER", "base", self.p), 0.0)
        broken = {**FRICTIONS, "delisting_classes": {"UNKNOWN": {"base": -0.3, "stress": -1}}}
        with self.assertRaises(ValueError):
            fr.FrictionParams.from_protocol(broken)
        with self.assertRaises(ValueError):
            fr.FrictionParams.from_protocol({**FRICTIONS, "stress": {"multiplier": 2.0,
                                                                     "gating": True}})
        with self.assertRaises(KeyError):
            fr.FrictionParams.from_protocol({k: v for k, v in FRICTIONS.items() if k != "impact"})


class TieBreakTests(unittest.TestCase):
    def test_key_formula_is_pinned(self):
        key = ct.tie_break_key(20260924, ["0000000009-10-000002", "0000000009-10-000001"])
        expected = hashlib.sha256(
            b"20260924|0000000009-10-000001,0000000009-10-000002").hexdigest()
        self.assertEqual(key, expected)
        with self.assertRaises(TypeError):
            ct.tie_break_key(True, ["a"])

    def test_probe_p5_admission_has_no_cik_tilt(self):
        # 400 issuers compete for 100 slots on one session: CIK order would admit CIKs 1..100.
        entries = [ct.Entry(0, f"{cik:010d}", (f"{cik:010d}-10-{cik:06d}",))
                   for cik in range(1, 401)]
        admitted = ct.admit(entries, slots=100, horizon=20, seed=20260924)
        ciks = [int(e.issuer) for e in admitted]
        self.assertEqual(len(ciks), 100)
        self.assertNotEqual(sorted(ciks), list(range(1, 101)))
        self.assertGreater(statistics.median(ciks), 150)
        self.assertLess(statistics.median(ciks), 250)
        self.assertEqual(ciks, [int(e.issuer) for e in
                                ct.admit(list(reversed(entries)), slots=100, horizon=20,
                                         seed=20260924)])

    def test_probe_p5v2_seed_changes_ties_only(self):
        entries = [ct.Entry(0, f"{cik:010d}", (f"{cik:010d}-10-{cik:06d}",))
                   for cik in range(1, 401)]
        a = {e.issuer for e in ct.admit(entries, slots=100, horizon=20, seed=20260924)}
        b = {e.issuer for e in ct.admit(entries, slots=100, horizon=20, seed=20260925)}
        self.assertEqual(len(a), 100)
        self.assertLess(len(a & b), 60)                     # ties re-drawn by the seed
        uncontested = [ct.Entry(i, f"{i:010d}", (f"x-{i}",)) for i in range(50)]
        self.assertEqual(ct.admit(uncontested, slots=100, horizon=20, seed=1),
                         ct.admit(uncontested, slots=100, horizon=20, seed=2))

    def test_slots_release_on_schedule_and_one_slot_per_issuer(self):
        entries = [ct.Entry(0, "A", ("a1",)), ct.Entry(0, "B", ("b1",)),
                   ct.Entry(5, "A", ("a2",)), ct.Entry(20, "A", ("a3",)),
                   ct.Entry(19, "C", ("c1",))]
        admitted = ct.admit(entries, slots=2, horizon=20, seed=1)
        self.assertEqual([(e.entry_index, e.issuer) for e in admitted],
                         [(0, "A"), (0, "B"), (20, "A")])


class PowerTests(unittest.TestCase):
    def test_tracking_error_restatement(self):
        with_te = portfolio_mde_annual(100, 5.0)
        without = portfolio_mde_annual(100, 5.0, tracking_error=0.0)
        self.assertGreater(with_te, without)
        self.assertAlmostEqual(without, 0.0677, places=3)
        self.assertAlmostEqual(with_te, 0.1117, places=3)


if __name__ == "__main__":
    unittest.main()

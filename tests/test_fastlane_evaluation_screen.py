"""Fast-lane screen, trial ledger, holdout request and the one holdout look.

SYNTHETIC data only (see tests/test_fastlane_evaluation.py). Every scenario runs
in a throw-away git repository with a bare 'origin'; outcome access goes through
require_outcome_access and the committed, write-once holdout request.
"""

import copy
import importlib.util
import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path
from unittest import mock

from quant.fastlane import evaluation as ev
from quant.fastlane import holdout as ho
from quant.fastlane import prices as px
from quant.fastlane import preregistration as pr
from quant.fastlane import screen as sc
from quant.fastlane import verdict as vd
from tests.test_fastlane_evaluation import (EvalWorld, SynthVendor, attestation, entry_index,
                                            make_bars, make_events, mappings_for, spy_series)

REPO = Path(__file__).resolve().parents[1]
VARIANTS = ["OD_V10K_H20", "CEO_CFO_V10K_H20", "FROZEN_FV_10S_V0_H20", "OD_V1M_H60"]
N_ISSUERS = 24


def pr_json(obj):
    """The report as it round-trips through canonical JSON."""
    import json
    return json.loads(pr.canonical_json(obj))


def load_cli():
    spec = importlib.util.spec_from_file_location("fastlane_cli", REPO / "scripts" / "fastlane.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ScreenAndHoldoutTests(unittest.TestCase):
    """Crash/replay of the trial records, request refusal, and the committed one look."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.rows = make_events(N_ISSUERS, date(2006, 1, 3), date(2022, 6, 30), spacing=40,
                               seed=21, ceo_prob=0.45, big_prob=0.01)
        cls.w = EvalWorld(cls.tmp.name, cls.rows, VARIANTS)
        cls.spy = spy_series(8)
        bars = make_bars(N_ISSUERS, cls.spy, cls.rows, seed=9, delta=0.002,
                         last=entry_index(date(2022, 12, 30)))
        cls.vendor = SynthVendor(bars, mappings=mappings_for(N_ISSUERS), spy=cls.spy)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_screen_crash_replay_request_and_the_one_look(self):
        fw = self.w.fw
        screen = sc.compute_screen(fw, self.vendor)
        statuses = {v: screen["variants"][v]["status"] for v in VARIANTS}
        self.assertEqual(statuses["OD_V1M_H60"], sc.STATUS_DROPPED)       # dropped, not replaced
        self.assertEqual(screen["variants"]["OD_V1M_H60"]["evaluations"], {})  # no return computed
        self.assertEqual(sum(s == sc.STATUS_EVALUATED for s in statuses.values()), 3)

        # crash after three trial records: nothing can be finalized or requested
        with self.assertRaises(ho.SimulatedCrash):
            sc.record_trials(fw, screen, crash_after=3)
        partial = ho.TrialLedger(fw).records()
        self.assertEqual(len(partial), 3)
        with self.assertRaises(sc.ScreenIncomplete):
            sc.finalize_screen(fw, screen)

        # replay: idempotent, exactly one record per declared variant and split
        sc.record_trials(fw, screen)
        sc.record_trials(fw, screen)
        records = ho.TrialLedger(fw).records()
        self.assertEqual(records[:3], partial)
        self.assertEqual(len(records), 2 * len(VARIANTS))
        disc = [r for r in records if r["split"] == "discovery"]
        self.assertEqual(len(disc), self.w.protocol["multiplicity"]["M_declared"])
        self.assertEqual(sorted(r["variant_id"] for r in disc), sorted(VARIANTS))
        self.assertEqual(len({r["trial_id"] for r in records}), len(records))

        report = sc.finalize_screen(fw, screen)
        self.assertEqual(report["n_trials_for_dsr"], 2 * len(VARIANTS))
        self.assertTrue(1 <= len(report["finalists"]) <= 3)
        self.assertNotIn("OD_V1M_H60", report["finalists"])
        for v in report["finalists"]:
            res = report["results"][v]
            self.assertLess(res["romano_wolf_p"], sc.RW_P_MAX)
            self.assertGreater(res["walk_forward_alpha_annual_net"], 0.0)
        dsrs = [report["results"][v]["dsr"]["dsr"] for v in report["ranking_by_dsr"]]
        self.assertEqual(dsrs, sorted(dsrs, reverse=True))
        self.assertTrue(sc.report_path(fw, report["config"]["digest"]).exists())

        # the request trusts no caller-supplied report: it recomputes the screen
        with self.assertRaises(pr.OutcomeAccessRefused):                  # no request yet
            vd.evaluate_holdout(fw, self.vendor)
        request = sc.request_holdout(fw, self.vendor)
        self.assertEqual(request["finalists"], report["finalists"])
        self.assertEqual(request["multiplicity"]["n_trials_for_dsr"], 2 * len(VARIANTS))
        committed = fw.read_json(ho.screen_report_path(fw))
        self.assertEqual(ho.json_digest(committed), request["screen_report_digest"])
        self.assertEqual({k: v for k, v in committed.items() if k != "trials"},
                         {k: v for k, v in pr_json(report).items() if k != "trials"})
        with self.assertRaises(pr.OutcomeAccessRefused):                  # written, not committed
            vd.evaluate_holdout(fw, self.vendor)
        self.assertEqual(ho.HoldoutLedger(fw).records(), [])
        self.assertEqual(sc.request_holdout(fw, self.vendor), request)    # idempotent replay
        self.w.commit_all("holdout request")
        self.w.publish()

        # a vendor whose evidence can never be GO does not get the look
        weak = SynthVendor(self.vendor._bars, mappings=self.vendor._maps, spy=self.spy,
                           att=attestation(includes_delisted=False))
        with self.assertRaises((pr.OutcomeAccessRefused, ev.VendorMismatch)):
            vd.evaluate_holdout(fw, weak)
        self.assertEqual(ho.HoldoutLedger(fw).records(), [])

        # a vendor whose discovery data changed since the screen cannot reproduce it
        shifted = {k: [b if b.session.year != 2012 else px.DailyBar(
            b.security_id, b.session, b.open, b.high * 1.02, b.low, b.close * 1.01, b.volume)
            for b in v] for k, v in self.vendor._bars.items()}
        with self.assertRaises(pr.OutcomeAccessRefused):
            vd.evaluate_holdout(fw, SynthVendor(shifted, mappings=self.vendor._maps,
                                                spy=self.spy))
        self.assertEqual(ho.HoldoutLedger(fw).records(), [])

        result = vd.evaluate_holdout(fw, self.vendor)
        decision = result["decision"]
        self.assertEqual(decision["verdict"], vd.VERDICT_GO)             # strong synthetic effect
        self.assertEqual(decision["finalists"], report["finalists"])
        self.assertEqual(len(ho.HoldoutLedger(fw).records()), 1)
        for v in report["finalists"]:
            detail = result["finalists"][v]
            self.assertEqual([c["c0_multiple"] for c in detail["capacity"]], [1.0, 10.0, 100.0])
            stress = detail["stress"]
            self.assertGreater(stress["net"]["alpha_annual"],
                               stress["net_friction_stress"]["alpha_annual"])
            self.assertFalse(detail["seed_robustness"]["gating"])
            self.assertEqual([r["seed"] for r in detail["seed_robustness"]["runs"]],
                             [20260925, 20260926, 20260927, 20260928, 20260929])
            self.assertEqual(detail["dsr"]["n_trials"], result["n_trials_for_dsr"])
            self.assertGreaterEqual(result["n_trials_for_dsr"], 2 * len(VARIANTS))
            self.assertEqual(detail["dsr"]["source"], "recomputed discovery screen")
            self.assertAlmostEqual(detail["dsr"]["sr_variance_used"],
                                   report["results"][v]["dsr"]["sr_variance_used"])
            self.assertIs(detail["c2_bias_diagnostic"]["gating"], False)
        self.assertTrue(vd.result_path(fw).exists())


class ZeroFinalistTests(unittest.TestCase):
    def test_zero_finalists_is_no_go_and_the_holdout_stays_unopened(self):
        rows = make_events(3, date(2006, 1, 3), date(2021, 6, 30), spacing=60, seed=5)
        spy = spy_series(2)
        with tempfile.TemporaryDirectory() as tmp:
            w = EvalWorld(tmp, rows, ["OD_V10K_H20", "CEO_CFO_V10K_H5"])
            bars = make_bars(3, spy, rows, seed=1, last=entry_index(date(2021, 12, 31)))
            vendor = SynthVendor(bars, mappings=mappings_for(3), spy=spy)
            report = sc.run_screen(w.fw, vendor)
            self.assertEqual(report["finalists"], [])
            self.assertTrue(all(r["status"] == sc.STATUS_DROPPED
                                for r in report["results"].values()))
            self.assertEqual(report["verdict"]["verdict"], vd.VERDICT_NO_GO)
            self.assertEqual(report["verdict"]["holdout"], "UNOPENED")
            self.assertEqual(len([r for r in ho.TrialLedger(w.fw).records()
                                  if r["split"] == "discovery"]), 2)
            with self.assertRaises(ho.NoFinalists):
                sc.request_holdout(w.fw, vendor)
            self.assertFalse(ho.request_path(w.fw).exists())
            self.assertFalse(ho.screen_report_path(w.fw).exists())


class ForgedLookRegressionTests(unittest.TestCase):
    """Review probe p10: fabricated trial records and a hand-written evaluation spec (forged
    discovery statistics) must never open the holdout or reach a verdict."""

    def test_p10_fabricated_trials_and_forged_spec_cannot_spend_the_look(self):
        rows = make_events(12, date(2021, 7, 6), date(2026, 5, 29), spacing=30, seed=7)
        spy = spy_series(9)
        with tempfile.TemporaryDirectory() as tmp:
            w = EvalWorld(tmp, rows, ["OD_V10K_H20", "CEO_CFO_V10K_H5"])
            bars = make_bars(12, spy, rows, seed=4, first=entry_index(date(2021, 1, 4)))
            vendor = SynthVendor(bars, mappings=mappings_for(12), spy=spy)       # NO effect
            ctx = ev.VendorContext(w.fw, vendor)
            ledger = ho.TrialLedger(w.fw)
            for v in ("OD_V10K_H20", "CEO_CFO_V10K_H5"):                    # fabricated trials
                for split in ("discovery", "walk_forward"):
                    ledger.record(f"{v}|{split}|fake", v, split, {"fabricated": True})
            spec = {"lineage": "QUANT_FASTLANE_HPIT_V1", "kind": "HOLDOUT_EVAL_SPEC",
                    "prereg_sha256": w.sha,
                    "screen_config": {"vendor": ctx.identity(), "events_digest": w.table.digest},
                    "finalists": ["OD_V10K_H20"],
                    "discovery_stats": {"OD_V10K_H20": {"sr": 0.5, "n": 3000, "skew": 0.0,
                                                        "kurtosis": 3.0}},
                    "sr_variance": 1e-6}
            spec_digest = ho.json_digest(spec)
            w.fw.create_exclusive(ho.eval_spec_path(w.fw), pr.canonical_json(spec) + b"\n")
            records = {(r["variant_id"], r["split"]): r for r in ledger.records()}
            report = {"prereg_sha256": w.sha, "finalists": ["OD_V10K_H20"],
                      "config": sc.screen_config(w.sealed, w.table, ctx),   # outcome-free
                      "holdout_request_payload": {"eval_spec_digest": spec_digest},
                      "n_trials_for_dsr": ho.n_trials_conservative(w.fw, w.sealed)[
                          "n_trials_for_dsr"],
                      "trials": {v: {s: {"trial_id": records[(v, s)]["trial_id"],
                                         "spec_digest": records[(v, s)]["spec_digest"]}
                                     for s in ("discovery", "walk_forward")}
                                 for v in ("OD_V10K_H20", "CEO_CFO_V10K_H5")}}
            report_digest = ho.json_digest(report)
            w.fw.create_exclusive(ho.screen_report_path(w.fw), pr.canonical_json(report) + b"\n")

            # 1. the public low-level writer is gone; the private one needs a receipt
            self.assertFalse(hasattr(ho, "write_holdout_request"))
            with self.assertRaises(pr.OutcomeAccessRefused):
                ho._write_holdout_request(w.fw, "forged-look", ["OD_V10K_H20"], spec_digest,
                                          report_digest, receipt="0" * 64)
            # 2. the verified path recomputes the screen and rejects the fabricated records
            with self.assertRaises(sc.ScreenIncomplete):
                sc.request_holdout(w.fw, vendor)
            self.assertFalse(ho.request_path(w.fw).exists())
            # 3. worst case: private internals abused to commit a forged request anyway
            receipt = ho._screen_receipt(w.fw, w.sha, "forged-look", ["OD_V10K_H20"],
                                         spec_digest, report_digest)
            ho._write_holdout_request(w.fw, "forged-look", ["OD_V10K_H20"], spec_digest,
                                      report_digest, receipt=receipt)
            w.commit_all("forged request")
            w.publish()
            with self.assertRaises(pr.OutcomeAccessRefused):          # no fresh receipt
                pr.require_outcome_access(w.fw, "holdout", w.sha,
                                          holdout_request_id="forged-look",
                                          holdout_variants=["OD_V10K_H20"],
                                          eval_spec_digest=spec_digest)
            with self.assertRaises(sc.ScreenIncomplete):              # recomputation mismatch
                vd.evaluate_holdout(w.fw, vendor, table=w.table)
            self.assertEqual(ho.HoldoutLedger(w.fw).records(), [])     # look never consumed
            self.assertFalse(vd.result_path(w.fw).exists())


class CliTests(unittest.TestCase):
    def run_cli(self, *args, key=None):
        cli = load_cli()
        env = {k: v for k, v in os.environ.items() if k != "NASDAQ_DATA_LINK_API_KEY"}
        if key:
            env["NASDAQ_DATA_LINK_API_KEY"] = key
        out = io.StringIO()
        with mock.patch.dict(os.environ, env, clear=True), redirect_stdout(out):
            code = cli.main(list(args))
        return code, out.getvalue()

    def test_screen_and_evaluate_holdout_refuse_cleanly_without_a_vendor_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = EvalWorld(tmp, make_events(2, date(2010, 1, 4), date(2010, 6, 30), spacing=30,
                                           seed=1), ["OD_V10K_H20"])
            for command in ("screen", "evaluate-holdout"):
                code, text = self.run_cli("--root", str(w.root), command)
                self.assertEqual(code, 2)
                self.assertIn("VendorUnavailable", text)
            code, text = self.run_cli("--root", str(w.root), "screen", key="synthetic-key")
            self.assertEqual(code, 2)                    # manifests name another vendor
            self.assertIn("refused", text)
            code, text = self.run_cli("--root", str(w.root), "evaluate-holdout",
                                      key="synthetic-key")
            self.assertEqual(code, 2)                    # no committed request
            self.assertIn("HOLDOUT_REQUEST", text)
            self.assertEqual(ho.TrialLedger(w.fw).records(), [])


if __name__ == "__main__":
    unittest.main()

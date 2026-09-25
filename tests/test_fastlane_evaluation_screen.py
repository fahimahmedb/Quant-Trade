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
from quant.fastlane import preregistration as pr
from quant.fastlane import screen as sc
from quant.fastlane import verdict as vd
from tests.test_fastlane_evaluation import (EvalWorld, SynthVendor, attestation, entry_index,
                                            make_bars, make_events, mappings_for, spy_series)

REPO = Path(__file__).resolve().parents[1]
VARIANTS = ["OD_V10K_H20", "CEO_CFO_V10K_H20", "FROZEN_FV_10S_V0_H20", "OD_V1M_H60"]
N_ISSUERS = 24


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

        # a report for a screen whose declared variants are not all recorded is refused
        forged = copy.deepcopy(report)
        forged["config"]["digest"] = "sha256:" + "0" * 64
        payload = forged["holdout_request_payload"]
        payload["eval_spec"]["screen_config"] = forged["config"]
        payload["eval_spec_digest"] = ev.digest(payload["eval_spec"])
        with self.assertRaises(sc.ScreenIncomplete):
            sc.request_holdout(fw, forged)
        self.assertFalse(ho.request_path(fw).exists())

        # without the committed request the holdout cannot be evaluated
        with self.assertRaises(pr.OutcomeAccessRefused):
            vd.evaluate_holdout(fw, self.vendor)
        request = sc.request_holdout(fw, report)
        self.assertEqual(request["finalists"], report["finalists"])
        self.assertEqual(request["multiplicity"]["n_trials_for_dsr"], 2 * len(VARIANTS))
        with self.assertRaises(pr.OutcomeAccessRefused):                  # written, not committed
            vd.evaluate_holdout(fw, self.vendor)
        self.assertEqual(ho.HoldoutLedger(fw).records(), [])
        self.assertEqual(sc.request_holdout(fw, report), request)         # idempotent replay
        other = copy.deepcopy(report)
        other["finalists"] = other["holdout_request_payload"]["finalists"] = report["finalists"][:1]
        other["holdout_request_payload"]["eval_spec"]["finalists"] = report["finalists"][:1]
        other["holdout_request_payload"]["eval_spec_digest"] = ev.digest(
            other["holdout_request_payload"]["eval_spec"])
        with self.assertRaises(ho.HoldoutAlreadyConsumed):                # one request only
            sc.request_holdout(fw, other)
        self.w.commit_all("holdout request")
        self.w.publish()

        # a vendor whose evidence can never be GO does not get the look
        weak = SynthVendor(self.vendor._bars, mappings=self.vendor._maps, spy=self.spy,
                           att=attestation(includes_delisted=False))
        with self.assertRaises((pr.OutcomeAccessRefused, ev.VendorMismatch)):
            vd.evaluate_holdout(fw, weak)
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
            self.assertEqual(detail["dsr"]["n_trials"], 2 * len(VARIANTS))
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
                sc.request_holdout(w.fw, report)
            self.assertFalse(ho.request_path(w.fw).exists())


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

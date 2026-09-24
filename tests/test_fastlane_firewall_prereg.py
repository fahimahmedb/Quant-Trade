"""Fast-lane firewall, pre-registration seal, one-look holdout and trial ledgers."""

import copy
import json
import os
import tempfile
import unittest
from pathlib import Path

from quant.fastlane import holdout as ho
from quant.fastlane import preregistration as pr
from quant.fastlane.firewall import Firewall, FirewallViolation, LINEAGE_ID

REPO = Path(__file__).resolve().parents[1]


def final_protocol(**overrides):
    protocol = {
        "lineage": LINEAGE_ID,
        "status": pr.STATUS_FINAL,
        "splits": {name: {"start": s.isoformat(), "end": e.isoformat(),
                          "price_window": {"start": "2005-10-01", "end": e.isoformat()}}
                   for name, (s, e) in pr.SPLITS.items()},
        "variants": [{"variant_id": "SYNTH_A"}, {"variant_id": "SYNTH_B"},
                     {"variant_id": "SYNTH_C"}, {"variant_id": "SYNTH_D"}],
        "multiplicity": {"max_finalists": 3},
    }
    protocol.update(overrides)
    return protocol


class FirewallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.fw = Firewall(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_allows_own_space(self):
        self.fw.write_json_atomic(self.fw.data("x", "a.json"), {"a": 1})
        self.fw.write_json_atomic(self.fw.artifact("b.json"), {"b": 2})
        self.assertEqual(self.fw.read_json(self.fw.data("x", "a.json")), {"a": 1})

    def test_refuses_writes_outside_its_space(self):
        for target in (self.root / "var" / "events.jsonl", self.root / "src" / "x.py",
                       self.root / "var" / "fastlane" / ".." / "book.json", Path("/tmp/x.json"),
                       self.root / "research" / "memory.jsonl"):
            with self.assertRaises(FirewallViolation, msg=str(target)):
                self.fw.write_json_atomic(target, {})
        self.assertFalse((self.root / "var" / "events.jsonl").exists())

    def test_refuses_frozen_lineage_paths_even_inside_its_space(self):
        for name in ("FORM4_FIRST_VERTICAL_MULTI_COHORT_V1", "form4_first_vertical_v1"):
            with self.assertRaises(FirewallViolation):
                self.fw.data(name, "ledger.jsonl")
            with self.assertRaises(FirewallViolation):
                self.fw.guard(self.root / "var" / "fastlane" / name, write=False)

    def test_refuses_symlink_escape(self):
        outside = self.root / "outside"
        outside.mkdir()
        self.fw.mkdirs(self.fw.data_root)
        os.symlink(outside, self.fw.data_root / "link")
        with self.assertRaises(FirewallViolation):
            self.fw.write_json_atomic(self.fw.data_root / "link" / "x.json", {})

    def test_governance_is_read_only(self):
        (self.root / "governance").mkdir()
        (self.root / "governance" / "rule.md").write_text("synthetic rule\n")
        self.assertTrue(self.fw.sha256_file(self.root / "governance" / "rule.md"))
        with self.assertRaises(FirewallViolation):
            self.fw.write_text_atomic(self.root / "governance" / "rule.md", "changed")


class PreregistrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.fw = Firewall(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def test_seal_is_write_once(self):
        record = pr.seal_protocol(self.fw, final_protocol())
        self.assertEqual(record["protocol_sha256"], pr.protocol_sha256(final_protocol()))
        again = pr.seal_protocol(self.fw, final_protocol())            # identical: replay
        self.assertEqual(again["sealed_at_utc"], record["sealed_at_utc"])
        changed = final_protocol(variants=[{"variant_id": "OTHER"}])
        with self.assertRaises(pr.PreregAlreadySealed):
            pr.seal_protocol(self.fw, changed)
        self.assertEqual(pr.load_sealed(self.fw)["protocol_sha256"], record["protocol_sha256"])

    def test_draft_cannot_be_sealed(self):
        with self.assertRaises(pr.PreregInvalid):
            pr.seal_protocol(self.fw, final_protocol(status=pr.STATUS_DRAFT))
        self.assertFalse(pr.sealed_path(self.fw).exists())

    def test_frozen_splits_and_limits_are_enforced(self):
        bad = final_protocol()
        bad["splits"]["holdout"]["start"] = "2021-01-01"
        with self.assertRaises(pr.PreregInvalid):
            pr.seal_protocol(self.fw, bad)
        with self.assertRaises(pr.PreregInvalid):
            pr.seal_protocol(self.fw, final_protocol(
                variants=[{"variant_id": f"V{i}"} for i in range(49)]))

    def test_canonical_hash_ignores_key_order(self):
        a = {"b": 1, "a": [1, {"y": 2, "x": 1}]}
        b = json.loads('{"a": [1, {"x": 1, "y": 2}], "b": 1}')
        self.assertEqual(pr.protocol_sha256(a), pr.protocol_sha256(b))

    def test_tampered_seal_is_detected(self):
        pr.seal_protocol(self.fw, final_protocol())
        path = pr.sealed_path(self.fw)
        record = json.loads(path.read_text())
        record["protocol"]["variants"].append({"variant_id": "SNUCK_IN"})
        path.write_text(json.dumps(record))
        with self.assertRaises(pr.PreregTampered):
            pr.load_sealed(self.fw)
        with self.assertRaises(pr.OutcomeAccessRefused):
            pr.require_outcome_access(self.fw, "discovery", record["protocol_sha256"])

    def test_outcome_access_requires_matching_sealed_prereg(self):
        with self.assertRaises(pr.OutcomeAccessRefused):
            pr.require_outcome_access(self.fw, "discovery", "sha256:" + "0" * 64)
        record = pr.seal_protocol(self.fw, final_protocol())
        with self.assertRaises(pr.OutcomeAccessRefused):
            pr.require_outcome_access(self.fw, "discovery", "sha256:" + "0" * 64)
        grant = pr.require_outcome_access(self.fw, "walk_forward", record["protocol_sha256"])
        self.assertEqual(grant.split, "walk_forward")
        with self.assertRaises(pr.OutcomeAccessRefused):
            pr.require_outcome_access(self.fw, "holdout", record["protocol_sha256"])

    def test_repository_draft_protocol_is_valid_but_unsealable(self):
        path = REPO / "research" / "fastlane" / "QUANT_FASTLANE_HPIT_V1_PROTOCOL.json"
        if not path.exists():
            self.skipTest("draft protocol not generated")
        protocol = json.loads(path.read_text())
        pr.validate_protocol(protocol, for_seal=False)
        self.assertEqual(protocol["status"], pr.STATUS_DRAFT)
        self.assertLessEqual(len(protocol["variants"]), pr.MAX_VARIANTS)
        with self.assertRaises(pr.PreregInvalid):
            pr.seal_protocol(self.fw, protocol)
        from quant.fastlane.frictions import FrictionParams
        params = FrictionParams.from_protocol(protocol["frictions"])
        self.assertEqual(params.participation_cap_adv20, 0.001)


class HoldoutLedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.fw = Firewall(Path(self.tmp.name))
        self.sha = pr.seal_protocol(self.fw, final_protocol())["protocol_sha256"]

    def tearDown(self):
        self.tmp.cleanup()

    def test_second_distinct_look_is_refused(self):
        grant = pr.require_outcome_access(self.fw, "holdout", self.sha,
                                          holdout_request_id="look-1",
                                          holdout_variants=["SYNTH_A", "SYNTH_B"])
        self.assertEqual(grant.holdout_request_id, "look-1")
        with self.assertRaises(ho.HoldoutAlreadyConsumed):
            pr.require_outcome_access(self.fw, "holdout", self.sha,
                                      holdout_request_id="look-2", holdout_variants=["SYNTH_A"])
        with self.assertRaises(ho.HoldoutAlreadyConsumed):   # same id, different finalists
            ho.HoldoutLedger(self.fw).request("look-1", self.sha, ["SYNTH_C"])
        self.assertEqual(len(ho.HoldoutLedger(self.fw).records()), 1)

    def test_idempotent_replay_after_simulated_crash(self):
        ledger = ho.HoldoutLedger(self.fw)
        with self.assertRaises(ho.SimulatedCrash):
            ledger.request("look-1", self.sha, ["SYNTH_A"], crash_after_append=True)
        # restart: a fresh ledger object replays the committed request
        replay = ho.HoldoutLedger(self.fw).request("look-1", self.sha, ["SYNTH_A"])
        self.assertEqual(replay["request_id"], "look-1")
        again = pr.require_outcome_access(self.fw, "holdout", self.sha,
                                          holdout_request_id="look-1",
                                          holdout_variants=["SYNTH_A"])
        self.assertEqual(again.holdout_request_id, "look-1")
        with self.assertRaises(ho.HoldoutAlreadyConsumed):
            ho.HoldoutLedger(self.fw).request("look-2", self.sha, ["SYNTH_A"])
        self.assertEqual(len(ho.HoldoutLedger(self.fw).records()), 1)

    def test_torn_ledger_fails_closed(self):
        ledger = ho.HoldoutLedger(self.fw)
        self.fw.mkdirs(ledger.path.parent)
        ledger.path.write_bytes(b'{"request_id": "look-1", "requ')
        with self.assertRaises(ho.LedgerCorrupted):
            ledger.request("look-2", self.sha, ["SYNTH_A"])

    def test_finalist_limit(self):
        with self.assertRaises(ValueError):
            ho.HoldoutLedger(self.fw).request("look-1", self.sha,
                                              ["SYNTH_A", "SYNTH_B", "SYNTH_C", "SYNTH_D"])
        self.assertEqual(ho.HoldoutLedger(self.fw).records(), [])


class TrialLedgerTests(unittest.TestCase):
    def test_every_trial_is_recorded_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            fw = Firewall(Path(tmp))
            ledger = ho.TrialLedger(fw)
            declared = ["SYNTH_A", "SYNTH_B"]
            spec = {"variant": "SYNTH_A", "h": 20}
            first = ledger.record("t1", "SYNTH_A", "discovery", "sha256:x", spec,
                                  declared_variants=declared)
            replay = ledger.record("t1", "SYNTH_A", "discovery", "sha256:x", copy.deepcopy(spec),
                                   declared_variants=declared)
            self.assertEqual(first, replay)
            with self.assertRaises(ho.TrialConflict):
                ledger.record("t1", "SYNTH_A", "discovery", "sha256:x", {"h": 60})
            with self.assertRaises(ho.TrialConflict):
                ledger.record("t2", "UNDECLARED", "discovery", "sha256:x", {},
                              declared_variants=declared)
            ledger.record("t2", "SYNTH_B", "walk_forward", "sha256:x", {})
            ledger.record("t3", "SYNTH_A", "walk_forward", "sha256:x", {})
            self.assertEqual(ledger.multiplicity(), {
                "trials": 3, "distinct_variants": 2,
                "distinct_variants_by_split": {"discovery": 1, "walk_forward": 2}})


if __name__ == "__main__":
    unittest.main()

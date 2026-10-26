"""Economic guardrails, crash recovery and concurrency on synthetic fixtures only."""
import copy
import hashlib
import json
import multiprocessing
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from quant.edge_lab.engine import Lab, initialize
from quant.edge_lab.seed import BRANCH
from quant.edge_lab.sources import monitor
from quant.edge_lab.store import Refused, Store, digest, event
from quant.state import write_json


def reserve_child(directory, output):
    try:
        output.put(Lab(directory).reserve("fixture-p", "fixture-data"))
    except Refused:
        output.put("REFUSED")


class LabTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name)
        self.directory = self.repo / "research/edge_lab"
        initialize(self.directory)
        self.lab = Lab(self.directory)
        self.packet = {"id": "fixture-source", "url": "https://example.test/fixture",
                       "version": "synthetic-v1", "passage": "synthetic permission/mechanism fixture",
                       "fact": "No market observations", "limit": "Software control only", "kind": "METHOD"}
        self.lab.evidence(self.packet)
        self.lab.family("fixture", "synthetic mechanism", "fixture-data", [self.packet["id"]])
        self.runner = self.repo / "runner.py"
        self.runner.write_text('import json,sys\nprint(json.dumps({"look_id":sys.argv[-1],"kind":"SOFTWARE_CHECK"}))\n')
        self.protocol = {"id": "fixture-p", "family": "fixture", "dataset": "fixture-data", "stage": "EXPLORATION",
                         "window": ["2020-01-01T00:00:00Z", "2020-02-01T00:00:00Z"],
                         "expressions": ["primary", "ablation"], "cost_paths": ["base", "stress"], "primary": "primary",
                         "mechanism": "synthetic", "payer": "fixture", "clock": "UTC causal fixture",
                         "independent_unit": "synthetic day", "benchmark": "zero fixture", "costs": "fixture zero",
                         "rights": {"permitted": True, "url": self.packet["url"], "scope": "software fixture"},
                         "decision_contract": {"positive": "prepare future independent validation", "negative": "stop expression",
                                               "inconclusive": "wait information", "invalid": "software evidence only"},
                         "multiplicity_policy": "charge every declared path; effective count UNKNOWN",
                         "runner": "runner.py", "runner_sha256": hashlib.sha256(self.runner.read_bytes()).hexdigest(),
                         "evidence_ids": [self.packet["id"]], "purpose": "SYNTHETIC_SOFTWARE_QA"}

    def tearDown(self):
        self.temp.cleanup()

    def admission_packet(self, fingerprint="fixture-data"):
        from quant.edge_lab.contracts import GATES
        p = self.lab.snapshot()[0]["protocols"][self.protocol["id"]]
        proof = {"protocol_hash": p["hash"], "runner_sha256": p["runner_sha256"],
                 "data_fingerprint": fingerprint, "paid_usd": 0}
        for gate in GATES:
            proof[gate] = {"qualified": True, "scope": "synthetic software only", "evidence_ids": [self.packet["id"]]}
        proof["software"].update(reviewed=True, synthetic_tests_passed=True, challenge_passed=True)
        proof["resources"].update(bound_type="FULL_PROTOCOL_UPPER_BOUND", wall_seconds_upper_bound=1,
            memory_bytes_upper_bound=268435456, disk_bytes_upper_bound=1048576,
            input_bound_evidence="fixed finite synthetic fixture; no market inputs")
        return proof

    def frozen(self, fingerprint="fixture-data"):
        self.lab.freeze(self.protocol)
        if self.protocol["rights"]["permitted"]:
            self.lab.admit(self.protocol["id"], self.admission_packet(fingerprint))

    def authority(self):
        state, control = self.lab.snapshot()
        return {"state": state, "control": control, "branch": BRANCH, "sha": "a" * 40,
                "runner_versions": {self.protocol["runner"]: self.protocol["runner_sha256"]}}

    def test_boot_tick_and_ci_never_open_market_outcomes(self):
        with patch("subprocess.run", side_effect=AssertionError("no workers at startup")):
            initialize(self.directory)
            self.lab.tick(actor="synthetic-test")
        state, _ = self.lab.snapshot()
        self.assertEqual(state["looks"], {})
        self.assertEqual(state["baseline"]["daily-etf-panel"]["declared_trials"], 40)
        self.assertIsNone(state["baseline"]["daily-etf-panel"]["effective_trials"])

    def test_pause_survives_restart_and_prevents_network(self):
        self.lab.store.pause(True, "fixture Owner pause")
        with patch("subprocess.run", side_effect=AssertionError("paused must not fetch")):
            monitor(self.directory, self.repo)
        with self.assertRaises(Refused):
            Lab(self.directory).freeze(self.protocol)
        self.assertTrue(Store(self.directory).control()["paused"])
        self.lab.store.pause(False, "fixture resume")
        self.frozen()

    def test_one_local_reservation_across_processes(self):
        self.frozen()
        context = multiprocessing.get_context("fork")
        output = context.Queue()
        children = [context.Process(target=reserve_child, args=(self.directory, output)) for _ in range(2)]
        for child in children:
            child.start()
        for child in children:
            child.join(5)
            self.assertEqual(child.exitcode, 0)
        self.assertCountEqual([output.get(timeout=1), output.get(timeout=1)], ["look:fixture-p", "REFUSED"])
        state, _ = self.lab.snapshot()
        self.assertEqual(state["trial_charges"]["fixture-data"], 4)

    def test_new_fingerprint_is_not_a_new_clean_look(self):
        self.frozen("data-v1")
        self.lab.reserve("fixture-p", "data-v1")
        with self.assertRaises(Refused):
            self.lab.reserve("fixture-p", "new-vendor-v2")

    def test_frozen_threshold_window_and_runner_are_immutable(self):
        self.frozen()
        for field, value in (("window", ["2020-01-02T00:00:00Z", "2020-02-01T00:00:00Z"]),
                             ("multiplicity_policy", "reset trials"), ("runner_sha256", "b" * 64)):
            changed = {**self.protocol, field: value}
            with self.assertRaises(Refused):
                self.lab.freeze(changed)

    def test_unknown_history_blocks_historical_confirmation(self):
        with self.assertRaisesRegex(Refused, "UNKNOWN"):
            self.lab.freeze({**self.protocol, "stage": "VALIDATION"})

    def test_prospective_cannot_be_backdated_or_peeked(self):
        with self.assertRaises(Refused):
            self.lab.freeze({**self.protocol, "stage": "PROSPECTIVE"})
        future = datetime.now(timezone.utc) + timedelta(days=1)
        self.protocol.update(stage="PROSPECTIVE", window=[future.isoformat(), (future + timedelta(days=5)).isoformat()])
        self.frozen("future-fixture")
        self.lab.reserve("fixture-p", "future-fixture")
        authority = self.authority()
        with self.assertRaisesRegex(Refused, "WAIT_OBSERVATIONS"):
            self.lab.execute("fixture-p", self.repo, lambda: authority, lambda s, sha: "b" * 40)

    def test_terminal_family_and_protected_window_cannot_be_rebranded(self):
        with self.assertRaises(Refused):
            self.lab.freeze({**self.protocol, "family": "f1-crypto-carry", "dataset": "crypto-carry-f1"})
        self.lab.family("fixture-etf", "different synthetic expression", "daily-etf-panel", [self.packet["id"]])
        with self.assertRaisesRegex(Refused, "holdout"):
            self.lab.freeze({**self.protocol, "family": "fixture-etf", "dataset": "daily-etf-panel",
                             "window": ["2025-04-01T00:00:00Z", "2025-05-01T00:00:00Z"]})

    def test_legacy_freeze_is_not_an_editable_template(self):
        with self.assertRaisesRegex(Refused, "upstream adapter"):
            self.lab.freeze({**self.protocol, "family": "eurusd-technical-grid", "dataset": "eurusd-histdata"})

    def test_intraday_or_timezone_spelling_cannot_bypass_reserved_dates(self):
        from quant.edge_lab.engine import overlap
        self.assertTrue(overlap(["2025-04-01T12:00:00Z", "2025-04-01T13:00:00Z"], ["2025-03-12", "2026-09-12"]))
        self.assertTrue(overlap(["2025-03-11T23:30:00-02:00", "2025-03-12T00:00:00-02:00"], ["2025-03-12", "2026-09-12"]))

    def test_measured_cost_cannot_be_reset_after_restart(self):
        with self.lab.store.lock():
            state = self.lab.store.read()
            state["usage"]["cpu_seconds"] = 5
            self.lab.store.save(state)
        with self.lab.store.lock():
            state = self.lab.store.read()
            state["usage"]["cpu_seconds"] = 0
            with self.assertRaises(Refused):
                self.lab.store.save(state)

    def test_access_failure_is_not_an_economic_rejection(self):
        with self.assertRaises(Refused):
            self.lab.decide("qualify:treasury-auction-zf", "REJECTED", [self.packet["id"]], "fixture")
        self.lab.decide("qualify:treasury-auction-zf", "WAIT", [self.packet["id"]], "wait qualified BBO")
        self.assertEqual(self.lab.snapshot()[0]["families"]["treasury-auction-zf"]["status"], "BLOCKED_DATA_ACCESS")

    def test_repeated_head_and_source_packet_do_not_create_work_or_trials(self):
        state, _ = self.lab.snapshot()
        f = state["families"]["treasury-auction-zf"]
        observations = {"treasury-auction-zf": {"ref": f["ref"], "sha": "c" * 40}}
        self.lab.tick(observations)
        count = len(self.lab.snapshot()[0]["events"])
        self.lab.tick(observations)
        self.lab.evidence(self.packet)
        self.assertEqual(len(self.lab.snapshot()[0]["events"]), count)
        self.assertEqual(self.lab.snapshot()[0]["looks"], {})

    def test_question_claim_prevents_duplicate_reasoning_and_stale_completion(self):
        identity = "qualify:eurusd-technical-grid"
        claim = self.lab.claim_decision(identity, "fixture-host-a")
        with self.assertRaises(Refused):
            Lab(self.directory).claim_decision(identity, "fixture-host-b")
        with self.assertRaisesRegex(Refused, "recorded claim"):
            self.lab.decide(identity, "WAIT", [self.packet["id"]], "fixture wait", claim_id="wrong")
        self.lab.decide(identity, "WAIT", [self.packet["id"]], "fixture wait", claim_id=claim)
        self.assertNotEqual(self.lab.next_decision()[0], identity)

    def test_missing_permission_and_paid_access_stop_reservation(self):
        self.protocol["rights"]["permitted"] = False
        self.frozen()
        with self.assertRaisesRegex(Refused, "PERMISSION"):
            self.lab.reserve("fixture-p", "fixture")

    def test_budget_counters_persist_and_unknown_tokens_fail_closed_when_capped(self):
        control = self.lab.store.control()
        control["limits"]["tokens_total"] = 100
        write_json(self.lab.store.control_path, control)
        with self.assertRaisesRegex(Refused, "UNMEASURED"):
            self.frozen()
        control["limits"].update(tokens_total=None, cpu_seconds_total=0)
        write_json(self.lab.store.control_path, control)
        with self.assertRaisesRegex(Refused, "EXHAUSTED"):
            Lab(self.directory).freeze(self.protocol)

    def test_no_capital_authority_override(self):
        control = self.lab.store.control()
        control["live_trading_authorized"] = True
        write_json(self.lab.store.control_path, control)
        with self.assertRaises(Refused):
            self.lab.tick()

    def test_corrupt_or_truncated_history_is_not_reset(self):
        self.lab.store.state_path.write_text('{"schema":1,')
        with self.assertRaises(json.JSONDecodeError):
            initialize(self.directory)

    def test_evidence_chain_and_baseline_cannot_be_rewritten(self):
        with self.lab.store.lock():
            state = self.lab.store.read()
            state["baseline"]["daily-etf-panel"]["declared_trials"] = 0
            with self.assertRaises(Refused):
                self.lab.store.save(state)

    def test_outcome_evidence_requires_a_prior_spent_reservation(self):
        with self.assertRaises(Refused):
            self.lab.evidence({**self.packet, "id": "unreserved-outcome", "kind": "OUTCOME"})

    def test_remote_cas_loser_never_launches_a_process(self):
        self.frozen()
        self.lab.reserve("fixture-p", "fixture-data")
        remote = self.authority()
        def conflict(*args):
            raise Refused("fixture competing host/Owner pause")
        with patch("subprocess.run", side_effect=AssertionError("loser must not launch")):
            with self.assertRaisesRegex(Refused, "claim rejected"):
                self.lab.execute("fixture-p", self.repo, lambda: remote, conflict)
        self.assertEqual(self.lab.snapshot()[0]["looks"]["look:fixture-p"]["status"], "UNKNOWN_OUTCOME")
        with self.assertRaises(Refused):
            self.lab.reserve("fixture-p", "another-fingerprint")

    def test_remote_pause_stops_a_locally_resumed_process(self):
        self.frozen()
        self.lab.reserve("fixture-p", "fixture-data")
        remote = self.authority()
        remote["control"]["paused"] = True
        with self.assertRaisesRegex(Refused, "PAUSED"):
            self.lab.execute("fixture-p", self.repo, lambda: remote, lambda s, sha: "b" * 40)

    def test_exactly_one_execution_then_no_retry(self):
        self.frozen()
        self.lab.reserve("fixture-p", "fixture-data")
        remote = self.authority()
        claims = []
        def claim(state, sha):
            claims.append((state["looks"]["look:fixture-p"]["status"], sha))
            return "b" * 40
        receipt = self.lab.execute("fixture-p", self.repo, lambda: remote, claim)
        self.assertEqual(receipt["result"]["kind"], "SOFTWARE_CHECK")
        self.assertEqual([x[0] for x in claims], ["RUNNING_SPENT", "COMPLETED_SPENT"])
        with self.assertRaises(Refused):
            self.lab.execute("fixture-p", self.repo, lambda: self.authority(), claim)

    def test_crash_look_is_quarantined_not_retried(self):
        self.frozen()
        self.lab.reserve("fixture-p", "fixture-data")
        with self.lab.store.lock():
            state = self.lab.store.read()
            state["jobs"]["execute:fixture-p"].update(status="RUNNING", started_at="2000-01-01T00:00:00+00:00", lease_seconds=1)
            state["looks"]["look:fixture-p"]["status"] = "RUNNING_SPENT"
            event(state, "SYNTHETIC_CRASH", {})
            self.lab.store.save(state)
        self.lab.tick()
        self.lab.tick()
        state, _ = self.lab.snapshot()
        self.assertEqual(state["jobs"]["execute:fixture-p"]["status"], "UNKNOWN_OUTCOME")
        self.assertEqual(state["trial_charges"]["fixture-data"], 4)

    def test_metadata_failure_does_not_modify_economic_verdicts(self):
        response = __import__("subprocess").CompletedProcess([], 1, stdout="", stderr="hidden diagnostics")
        with patch("subprocess.run", return_value=response):
            monitor(self.directory, self.repo)
        state, _ = self.lab.snapshot()
        self.assertEqual(state["scheduler"]["metadata_probe"]["status"], "REMOTE_METADATA_UNAVAILABLE")
        self.assertEqual(state["looks"], {})


if __name__ == "__main__":
    unittest.main()

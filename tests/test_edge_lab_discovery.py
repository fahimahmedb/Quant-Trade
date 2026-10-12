"""Discovery authority, typed evidence and dispatch boundaries on synthetic fixtures."""
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from quant.edge_lab import discovery
from quant.edge_lab.engine import Lab, initialize
from quant.edge_lab.store import Refused, digest
from quant.edge_lab.worker import start


NOW = datetime(2026, 10, 12, 12, tzinfo=timezone.utc)


def contract():
    return {
        "mechanism": "Synthetic mechanism",
        "who_pays": "Synthetic counterparty",
        "why_persist": "Synthetic constraint",
        "primary_signature": "One fixed synthetic signature",
        "alternative_explanation": "Synthetic alternative",
        "negative_control": "One fixed synthetic control",
        "TEST_CAN_KILL": ["KILL_EXPRESSION"],
        "TEST_CAN_SUPPORT": ["PROMOTE_EXPRESSION"],
        "TEST_CANNOT_SAY": ["KILL_MECHANISM", "PROMOTE_MECHANISM", "PROMOTE_HIGH", "ALPHA", "V3_VALIDATED"],
        "BIAS_DIRECTION": {"missing_data": "Unknown; all-or-nothing admission"},
        "unit_economics": {"unit": "synthetic points", "break_even_friction": "Synthetic gross mean covers fixed costs",
                           "central_roundtrip_cost_points": 0.1, "stress_roundtrip_cost_points": 0.25},
        "adequacy": {"minimum_contracts": 36, "all_or_nothing": True, "failure_verdict": "PARK_DATA"},
        "red_team": {"fixed": "One fixed synthetic red-team test", "method": "One synthetic placebo",
                     "pass_if": "The fixed synthetic signature survives the placebo", "required_before_promotion": True},
        "claim_ceiling": "PROMOTE_EXPRESSION",
    }


def card(identity="synthetic-one"):
    return {
        "id": identity, "family": "synthetic", "mechanism_cluster": "synthetic",
        "level": "L1", "status": "TEST_NOW", "runner": "vix-known-prefix-v1",
        "selection": {"economic_plausibility": "HIGH", "decision_leverage": "HIGH",
                      "discriminating_power": "HIGH", "data_friction": "LOW", "expected_minutes": 5},
        "contract": contract(),
    }


def seal(state):
    state["integrity"] = digest({key: value for key, value in state.items() if key != "integrity"})
    return state


def synthetic_state(*cards):
    return seal({"schema": 1, "queue": list(cards), "closed_families": [],
                 "exposure_ledger": [], "events": [],
                 "metrics": {"actual_data_test_attempts": 0, "completed_economic_tests": 0,
                             "experiments_with_decision": 0, "data_parks": 0},
                 "real_capital_authorized": False, "live_trading_authorized": False})


def result(verdict="PARK_DATA", adequate=False, **extra):
    return {"experiment_id": "synthetic-one", "typed_verdict": verdict,
            "adequacy_passed": adequate, **extra}


class Authority:
    """A local CAS stub; it records ordering and never reads a remote or outcomes."""
    def __init__(self, state, control=None, versions=None, reject=False, v3=None):
        self.remote = copy.deepcopy(state)
        self.control = {"paused": False} if control is None else copy.deepcopy(control)
        self.versions = copy.deepcopy(versions or {})
        self.reject, self.v3 = reject, copy.deepcopy(v3)
        self.claims = []
        self.sha = "a" * 40

    def snapshot(self):
        return {"sha": self.sha, "control": copy.deepcopy(self.control),
                "discovery": copy.deepcopy(self.remote), "state": copy.deepcopy(self.v3),
                "code_versions": copy.deepcopy(self.versions)}

    def claim(self, state, parent):
        self.claims.append((copy.deepcopy(state), parent))
        if self.reject:
            raise Refused("Synthetic losing CAS")
        self.remote = copy.deepcopy(state)
        self.sha = chr(ord("a") + len(self.claims)) * 40
        return self.sha


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def test_missing_state_is_absent_and_saved_state_survives_restart(self):
        self.assertIsNone(discovery.load(self.directory))
        state = synthetic_state(card())
        discovery.save(self.directory, state)
        self.assertEqual(discovery.load(self.directory), state)

    def test_contract_requires_falsification_controls_and_bounded_claims(self):
        discovery.validate_contract(card())
        for field in ("who_pays", "why_persist", "primary_signature", "negative_control",
                      "TEST_CAN_KILL", "TEST_CAN_SUPPORT", "TEST_CANNOT_SAY", "BIAS_DIRECTION",
                      "unit_economics", "adequacy", "red_team", "claim_ceiling"):
            with self.subTest(field=field):
                invalid = card()
                del invalid["contract"][field]
                with self.assertRaises(Refused):
                    discovery.validate_contract(invalid)
        invalid = card()
        invalid["contract"]["adequacy"]["all_or_nothing"] = False
        with self.assertRaises(Refused):
            discovery.validate_contract(invalid)

    def test_contract_costs_must_be_finite_and_red_team_must_be_predeclared(self):
        for cost in (-0.1, True, "0.1", float("nan"), float("inf")):
            with self.subTest(cost=cost):
                invalid = card()
                invalid["contract"]["unit_economics"]["central_roundtrip_cost_points"] = cost
                with self.assertRaises(Refused):
                    discovery.validate_contract(invalid)
        for field in ("unit", "break_even_friction", "central_roundtrip_cost_points", "stress_roundtrip_cost_points"):
            invalid = card()
            del invalid["contract"]["unit_economics"][field]
            with self.subTest(field=field), self.assertRaises(Refused):
                discovery.validate_contract(invalid)
        for field in ("method", "pass_if"):
            invalid = card()
            del invalid["contract"]["red_team"][field]
            with self.subTest(red_team=field), self.assertRaises(Refused):
                discovery.validate_contract(invalid)

    def test_priority_favors_discriminating_low_friction_work_and_closed_families_stay_parked(self):
        expensive = card("synthetic-expensive")
        expensive["selection"]["data_friction"] = "HIGH"
        cheap = card("synthetic-cheap")
        weak = card("synthetic-weak")
        weak["selection"]["economic_plausibility"] = "LOW"
        closed = card("synthetic-closed")
        closed["family"] = "closed-synthetic"
        state = synthetic_state(expensive, cheap, weak, closed)
        state["closed_families"] = ["closed-synthetic"]
        projection = discovery.project(state, {"paused": False}, now=NOW)
        self.assertEqual(projection["next"]["id"], "synthetic-cheap")
        self.assertEqual({row["id"] for row in projection["groups"]["parked"]},
                         {"synthetic-weak", "synthetic-closed"})

    def test_projection_obeys_pause_and_due_boundary_without_mutating_state(self):
        pending = card()
        pending["not_before"] = "2026-10-12T12:01:00Z"
        state = synthetic_state(pending)
        before = copy.deepcopy(state)
        self.assertIsNone(discovery.project(state, {"paused": False}, now=NOW)["next"])
        due = discovery.project(state, {"paused": False}, now=NOW + timedelta(minutes=1))
        self.assertEqual(due["next"]["id"], pending["id"])
        self.assertIsNone(discovery.project(state, {"paused": True}, now=NOW + timedelta(minutes=1))["next"])
        self.assertEqual(state, before)

    def test_running_and_expired_original_claim_both_block_a_new_claim(self):
        state = synthetic_state(card(), card("synthetic-two"))
        original = copy.deepcopy(state)
        state = discovery.claim(state, "synthetic-one", "invocation-one", now=NOW)
        self.assertEqual(original["queue"][0]["status"], "TEST_NOW")
        self.assertIsNone(discovery.project(state, {"paused": False}, now=NOW)["next"])
        expired = discovery.project(state, {"paused": False}, now=NOW + timedelta(days=1))
        self.assertEqual(expired["status"], "RECOVERY_REQUIRED")
        self.assertIsNone(expired["next"])
        before = copy.deepcopy(state)
        with self.assertRaises(Refused):
            discovery.claim(state, "synthetic-two", "invocation-two", now=NOW + timedelta(days=1))
        self.assertEqual(state, before)

    def test_future_claim_timestamp_requires_recovery_and_cannot_hide_an_unfinished_attempt(self):
        state = discovery.claim(synthetic_state(card()), "synthetic-one", "original", now=NOW + timedelta(minutes=1))
        projection = discovery.project(state, {"paused": False}, now=NOW)
        self.assertEqual(projection["status"], "RECOVERY_REQUIRED")
        self.assertIsNone(projection["active_lease"])
        self.assertIsNone(projection["next"])

    def test_invocation_cannot_complete_another_claim_or_replay_a_terminal_card(self):
        state = synthetic_state(card())
        state = discovery.claim(state, "synthetic-one", "original", now=NOW)
        before = copy.deepcopy(state)
        with self.assertRaises(Refused):
            discovery.complete(state, "synthetic-one", "other", result(), now=NOW)
        self.assertEqual(state, before)
        state = discovery.complete(state, "synthetic-one", "original", result(), now=NOW)
        finished = copy.deepcopy(state)
        with self.assertRaises(Refused):
            discovery.claim(state, "synthetic-one", "retry", now=NOW)
        self.assertEqual(state, finished)

    def test_inadequate_sample_cannot_kill_or_promote_an_expression(self):
        for verdict in ("KILL_EXPRESSION", "PROMOTE_EXPRESSION"):
            with self.subTest(verdict=verdict):
                state = synthetic_state(card())
                state = discovery.claim(state, "synthetic-one", "original", now=NOW)
                before = copy.deepcopy(state)
                with self.assertRaises(Refused):
                    discovery.complete(state, "synthetic-one", "original",
                                       result(verdict, False, red_team={"passed": True}), now=NOW)
                self.assertEqual(state, before)

    def test_expression_promotion_requires_fixed_red_team_and_cannot_exceed_contract(self):
        for receipt in (result("PROMOTE_EXPRESSION", True),
                        result("PROMOTE_EXPRESSION", True, red_team={"passed": False}),
                        result("PROMOTE_MECHANISM", True, red_team={"passed": True}, mechanism_signature_passed=True),
                        result("PROMOTE_HIGH", True, red_team={"passed": True}, mechanism_signature_passed=True)):
            with self.subTest(result=receipt):
                state = synthetic_state(card())
                state = discovery.claim(state, "synthetic-one", "original", now=NOW)
                before = copy.deepcopy(state)
                with self.assertRaises(Refused):
                    discovery.complete(state, "synthetic-one", "original", receipt, now=NOW)
                self.assertEqual(state, before)

    def test_valid_expression_promotion_is_exploratory_and_capital_flags_are_refused(self):
        state = discovery.claim(synthetic_state(card()), "synthetic-one", "original", now=NOW)
        promoted = discovery.complete(state, "synthetic-one", "original",
                                      result("PROMOTE_EXPRESSION", True, red_team={"passed": True}), now=NOW)
        receipt = promoted["queue"][0]["result"]
        self.assertEqual(receipt["label"], "EXPLORATORY")
        self.assertFalse(receipt["edge_validated"])
        self.assertFalse(receipt["real_capital_authorized"])
        self.assertFalse(receipt["live_trading_authorized"])
        self.assertEqual(state["queue"][0]["status"], "RUNNING")
        for flag in ("edge_validated", "real_capital_authorized", "live_trading_authorized"):
            with self.subTest(flag=flag), self.assertRaises(Refused):
                discovery.complete(state, "synthetic-one", "original", result(**{flag: True}), now=NOW)

    def test_explicit_support_rights_cannot_override_the_frozen_claim_ceiling(self):
        broader = card()
        broader["contract"]["TEST_CAN_SUPPORT"] += ["PROMOTE_MECHANISM", "PROMOTE_HIGH"]
        broader["contract"]["TEST_CANNOT_SAY"] = ["KILL_MECHANISM", "ALPHA", "V3_VALIDATED"]
        state = discovery.claim(synthetic_state(broader), "synthetic-one", "original", now=NOW)
        for verdict in ("PROMOTE_MECHANISM", "PROMOTE_HIGH"):
            with self.subTest(verdict=verdict), self.assertRaises(Refused):
                discovery.complete(state, "synthetic-one", "original",
                                   result(verdict, True, red_team={"passed": True}, mechanism_signature_passed=True), now=NOW)

    def test_completed_result_must_be_bound_to_its_exact_experiment(self):
        state = discovery.claim(synthetic_state(card()), "synthetic-one", "original", now=NOW)
        for identity in (None, "synthetic-other"):
            receipt = result()
            receipt["experiment_id"] = identity
            with self.subTest(identity=identity), self.assertRaises(Refused):
                discovery.complete(state, "synthetic-one", "original", receipt, now=NOW)

    def test_accounting_distinguishes_an_attempt_data_park_and_computed_economics(self):
        for computed in (False, True):
            with self.subTest(computed=computed):
                state = discovery.claim(synthetic_state(card()), "synthetic-one", "original", now=NOW)
                self.assertEqual(state["metrics"]["actual_data_test_attempts"], 1)
                self.assertEqual(len(state["exposure_ledger"]), 1)
                verdict = "KILL_EXPRESSION" if computed else "PARK_DATA"
                finished = discovery.complete(state, "synthetic-one", "original",
                                              result(verdict, computed, economics_computed=computed), now=NOW)
                self.assertEqual(finished["metrics"]["actual_data_test_attempts"], 1)
                self.assertEqual(finished["metrics"]["completed_economic_tests"], int(computed))
                self.assertEqual(finished["metrics"]["experiments_with_decision"], 1)
                self.assertEqual(finished["metrics"]["data_parks"], int(not computed))
                directory = self.directory / ("computed" if computed else "parked")
                discovery.save(directory, finished)
                for key, value in finished["metrics"].items():
                    if not isinstance(value, int) or value == 0:
                        continue
                    invalid = copy.deepcopy(finished)
                    invalid["metrics"][key] = 0
                    with self.subTest(counter=key), self.assertRaises(Refused):
                        discovery.save(directory, invalid)

    def test_save_cannot_erase_prior_exposure_or_terminal_evidence(self):
        state = synthetic_state(card())
        state["closed_families"] = ["previously-closed-synthetic"]
        state["exposure_ledger"] = [{"experiment_id": "synthetic-one", "kind": "SYNTHETIC_PRIOR_EXPOSURE"}]
        seal(state)
        discovery.save(self.directory, state)
        state = discovery.claim(state, "synthetic-one", "original", now=NOW)
        state = discovery.complete(state, "synthetic-one", "original", result(), now=NOW)
        discovery.save(self.directory, state)
        before = discovery.load(self.directory)
        for field in ("exposure_ledger", "events", "queue", "closed_families"):
            with self.subTest(field=field):
                invalid = copy.deepcopy(before)
                invalid[field] = []
                seal(invalid)
                with self.assertRaises(Refused):
                    discovery.save(self.directory, invalid)
                self.assertEqual(discovery.load(self.directory), before)


class DiscoveryExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.directory = self.root / "research/edge_lab/discovery"
        self.v3_directory = self.root / "research/edge_lab"
        initialize(self.v3_directory)
        self.v3, self.control = Lab(self.v3_directory).snapshot()
        self.cache = self.root / "empty-cache"
        self.cache.mkdir()
        experiment = self.directory / "experiments"
        experiment.mkdir(parents=True)
        self.card = card()
        self.card["contract_path"] = "experiments/synthetic.contract.json"
        self.card["manifest_path"] = "experiments/synthetic.manifest.json"
        (self.directory / self.card["contract_path"]).write_text(json.dumps(self.card["contract"]))
        (self.directory / self.card["manifest_path"]).write_text(json.dumps({"schema": 1, "id": "synthetic-manifest"}))
        self.card["contract_sha256"] = self.file_hash(self.card["contract_path"], self.directory)
        self.card["manifest_sha256"] = self.file_hash(self.card["manifest_path"], self.directory)
        self.card["code_sha256"] = {}
        for relative in ("src/quant/edge_lab/vix.py", "src/quant/edge_lab/discovery.py"):
            fixture = self.root / relative
            fixture.parent.mkdir(parents=True, exist_ok=True)
            fixture.write_text("raise AssertionError('Synthetic code binding only; never execute')\n")
            self.card["code_sha256"][relative] = self.file_hash(relative)
        self.state = synthetic_state(self.card)
        discovery.save(self.directory, self.state)
        self.authority = Authority(self.state, self.control, self.card["code_sha256"], v3=self.v3)

    def file_hash(self, relative, directory=None):
        return hashlib.sha256(((directory or self.root) / relative).read_bytes()).hexdigest()

    def execute(self, runner):
        return discovery.execute(self.directory, self.root, self.authority, self.card["id"],
                                 self.cache, invocation_id="synthetic-run", runner=runner)

    def test_fresh_cas_is_published_before_runner_and_completion_is_exploratory(self):
        calls = []
        def runner(manifest, fixed_contract, cache_dir):
            self.assertEqual(len(self.authority.claims), 1)
            self.assertEqual(self.authority.remote["queue"][0]["status"], "RUNNING")
            self.assertEqual(manifest["id"], "synthetic-manifest")
            self.assertEqual(fixed_contract, self.card["contract"])
            self.assertEqual(Path(cache_dir), self.cache)
            calls.append(True)
            return result()
        self.execute(runner)
        self.assertEqual(calls, [True])
        self.assertEqual(len(self.authority.claims), 2)
        after = discovery.load(self.directory)
        self.assertFalse(after["real_capital_authorized"])
        self.assertFalse(after["live_trading_authorized"])
        self.assertIn("EXPLORATORY", json.dumps(after))

    def test_losing_cas_or_fresh_pause_never_invokes_runner(self):
        for paused, rejected in ((False, True), (True, False)):
            with self.subTest(paused=paused, rejected=rejected):
                discovery.save(self.directory, self.state)
                control = {**self.control, "paused": paused}
                self.authority = Authority(self.state, control, self.card["code_sha256"], reject=rejected, v3=self.v3)
                with self.assertRaises(Refused):
                    self.execute(lambda *args: self.fail("Runner must not launch without fresh authority"))

    def test_tampered_manifest_or_unpublished_code_stops_before_cas_and_runner(self):
        manifest = self.directory / self.card["manifest_path"]
        original = manifest.read_bytes()
        manifest.write_bytes(original + b" ")
        with self.assertRaises(Refused):
            self.execute(lambda *args: self.fail("Tampered manifest must not launch"))
        self.assertEqual(self.authority.claims, [])
        manifest.write_bytes(original)
        self.authority.versions = {**self.card["code_sha256"], "src/quant/edge_lab/vix.py": "0" * 64}
        with self.assertRaises(Refused):
            self.execute(lambda *args: self.fail("Unpublished code must not launch"))
        self.assertEqual(self.authority.claims, [])

    def test_runner_failure_preserves_original_running_claim_and_refuses_retry(self):
        calls = []
        def runner(*args):
            calls.append(True)
            raise RuntimeError("Synthetic interrupted runner")
        with self.assertRaises(RuntimeError):
            self.execute(runner)
        partial = discovery.load(self.directory)
        self.assertEqual(partial["queue"][0]["status"], "RUNNING")
        self.assertEqual(len(self.authority.claims), 1)
        with self.assertRaises(Refused):
            self.execute(runner)
        self.assertEqual(calls, [True])


class DiscoveryWorkerAndCLITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.discovery_directory = self.directory / "discovery"
        initialize(self.directory)
        self.lab = Lab(self.directory)
        self.discovery = synthetic_state(card())
        discovery.save(self.discovery_directory, self.discovery)

    def test_ready_discovery_precedes_active_and_expired_v3_sessions_without_v3_cas(self):
        for claimed_at in ("2099-01-01T00:00:00Z", "2000-01-01T00:00:00Z"):
            with self.subTest(claimed_at=claimed_at):
                v3, control = self.lab.snapshot()
                v3["decisions"] = {"synthetic-v3": {"status": "RESEARCHING", "family": "synthetic",
                    "claimed_at": claimed_at, "lease_seconds": 600, "claim_id": "v3-original"}}
                v3["worker_sessions"] = {"v3-session": {"id": "v3-session", "status": "STARTED",
                    "question_id": "synthetic-v3", "claim_id": "v3-original", "heartbeat_at": claimed_at}}
                with self.lab.store.lock():
                    self.lab.store.save(v3)
                v3, control = self.lab.snapshot()
                authority = Authority(self.discovery, control, v3=v3)
                before = self.lab.snapshot()
                receipt = start(self.lab, authority, "synthetic-worker", invocation_id="discovery-handoff")
                self.assertEqual(receipt["status"], "DISCOVERY_READY")
                self.assertEqual(receipt["lane"], "DISCOVERY")
                self.assertEqual(receipt["next"]["id"], "synthetic-one")
                self.assertFalse(receipt["economic_access_authorized"])
                self.assertFalse(receipt["outcome_access_authorized"])
                self.assertEqual(authority.claims, [])
                self.assertEqual(self.lab.snapshot(), before)

    def cli(self):
        script = Path(__file__).resolve().parents[1] / "scripts/edge_lab.py"
        spec = importlib.util.spec_from_file_location("synthetic_edge_lab_cli", script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_cli_discovery_queue_is_read_only_and_execute_dispatches_bounded_arguments(self):
        cli = self.cli()
        output = io.StringIO()
        before = self.lab.snapshot()
        with patch.object(cli, "GitAuthority", side_effect=AssertionError("Queue must not contact authority")), \
             patch("quant.edge_lab.remote.DiscoveryAuthority", side_effect=AssertionError("Queue must not contact authority")), \
             patch.object(cli, "render"), contextlib.redirect_stdout(output):
            cli.main(["--state-dir", str(self.directory), "discovery-queue"])
        self.assertEqual(json.loads(output.getvalue())["next"]["id"], "synthetic-one")
        self.assertEqual(self.lab.snapshot(), before)
        self.assertEqual(discovery.load(self.discovery_directory), self.discovery)
        authority = Authority(self.discovery)
        cache = self.directory / "synthetic-cache"
        with patch("quant.edge_lab.remote.DiscoveryAuthority", return_value=authority), \
             patch.object(cli, "render"), patch.object(discovery, "execute", return_value={"status": "synthetic-complete"}) as execute, \
             contextlib.redirect_stdout(io.StringIO()):
            cli.main(["--state-dir", str(self.directory), "discovery-execute", "synthetic-one",
                      "--cache-dir", str(cache), "--invocation-id", "cli-once"])
        self.assertEqual(execute.call_count, 1)
        args, kwargs = execute.call_args
        self.assertEqual(Path(args[0]), self.discovery_directory)
        self.assertEqual(args[2], authority)
        self.assertEqual(args[3], "synthetic-one")
        self.assertEqual(Path(args[4]), cache)
        self.assertEqual(args[5], "cli-once")


if __name__ == "__main__":
    unittest.main()

import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from research.research_os.engines.builtin import ENGINE_REGISTRY
from research.research_os.engines.protocol import EngineContext
from research.research_os.expansion.economic_test_readiness_v1 import READY as V1_READY
from research.research_os.expansion.v2_core import (
    build_candidate,
    build_research_trial,
    build_validator_result,
    canonical_hash,
)
from research.research_os.expansion.v2_stage_executor import (
    ACTIVE_EPOCH_PATH,
    V2StageExecutor,
    v2_artifact_path,
)
from research.research_os.oracle_worker_v2 import build_v2_worker
from research.research_os.worker_stages import CanonicalStageExecutor, artifact_path


class FakeSnapshot:
    def __init__(self, values=None):
        self.values = dict(values or {})
        self.head = "a" * 40
        self.blobs = {key: "b" * 40 for key in self.values}

    def read(self, path):
        if path not in self.values:
            raise KeyError(path)
        return self.values[path]


class V2WorkerIntegrationTests(unittest.TestCase):
    def epoch(self):
        return {
            "schema_version": "oracle-v2-research-epoch-v1",
            "state": "OPEN",
            "research_epoch_id": "E1",
            "parent_epoch_id": None,
            "opened_at": "2026-10-20T01:30:00Z",
            "knowledge_cutoff": "2026-10-20T01:00:00Z",
            "research_window": {"start": "2026-10-20T01:30:00Z", "end": "2026-12-31T00:00:00Z"},
            "export_cutoff": "2026-12-31T00:00:00Z",
            "close_policy": "PREDECLARED_COMPOSITE",
            "feedback_release_policy": {"mode": "AFTER_CLOSE_AND_GOVERNED_RELEASE"},
            "research_policy_hash": "r" * 64,
            "model_routing_policy_hash": "m" * 64,
            "allowed_model_set": ["DETERMINISTIC_ENGINE", "gpt-oss-10.2b-q4-k-m"],
            "allowed_model_change_policy": "WITHIN_ALLOWED_SET_ONLY",
            "source_policy_hash": "s" * 64,
            "retrieval_policy_hash": "q" * 64,
            "validator_policy_hash": "v" * 64,
            "max_candidate_exports": 100,
            "scheduled_close_at": "2027-01-01T00:00:00Z",
            "epoch_knowledge_parent": None,
            "epoch_feedback_dependencies": [],
            "contamination_status": "CLEAN",
            "owner_outcome_blinding_status": "BLINDED",
            "supervisor_outcome_blinding_status": "BLINDED",
            "first_evaluation_export_accepted": False,
        }

    def worker_config(self):
        return {
            "research_contract_version": "v2-core",
            "repository": "owner/repo",
            "branch": "builder/oracle-v2-core-20261020",
            "cache": "/tmp/not-used",
            "worker_id": "oracle-v2-test",
            "release_sha": "f" * 40,
            "lane": "auto",
            "economic_experiment_authorized": False,
            "prospective_observation_authorized": False,
            "real_capital_authorized": False,
            "live_trading_authorized": False,
        }

    def v2_candidate(self):
        return build_candidate({
            "hypothesis_id": "H1",
            "generation_id": "G1",
            "research_trial_id": "T1",
            "research_epoch_id": "E1",
            "family": "fundamental",
            "claim": "bounded claim",
            "mechanism_statement": "bounded mechanism",
            "universe": ["AAPL"],
            "clock": "publication",
            "horizon": "5d",
            "economic_expression": {"instrument": "equity", "direction": "NOT_YET_MEASURABLE"},
            "evidence_manifest": {"sources": ["S1"], "source_candidate_hash": "c" * 64,
                                  "documentary_packet_hash": "e" * 64},
            "falsification_scope": "counterevidence",
            "decision_map": {"fails": "KILL", "survives": "EXPLORE"},
            "known_confounders": [],
            "disconfirmation_manifest": {"attempted": True},
            "producer_identity": {"worker_id": "producer"},
            "extension": {
                "type": "FundamentalExtension",
                "issuer": "AAPL",
                "business_driver": "services",
                "valuation_transmission": "cash generation",
            },
        })

    def v2_trial(self, candidate):
        return build_research_trial({
            "research_trial_id": candidate["research_trial_id"], "research_epoch_id": candidate["research_epoch_id"],
            "trial_type": "RESEARCH_GENERATION_TRIAL", "model_identity": "DETERMINISTIC_ENGINE",
            "prompt_hash": "p", "context_hash": "c", "retrieval_manifest_hash": "r",
            "source_packet_hash": candidate["evidence_manifest"]["documentary_packet_hash"],
            "generated_at": "2026-10-20T02:00:00Z", "sampling_parameters": {"mode": "deterministic"},
            "generated_proposals": [{"hypothesis_id": candidate["hypothesis_id"],
                                     "generation_id": candidate["generation_id"],
                                     "candidate_hash": candidate["evidence_manifest"]["source_candidate_hash"]}],
            "discarded_proposals": [], "retry_count": 0,
        })

    def test_v2_worker_requires_explicit_contract_and_closed_authority(self):
        config = self.worker_config()
        worker = build_v2_worker(config, store=object(), backend=object())
        self.assertIsInstance(worker.executor, V2StageExecutor)

        invalid = dict(config)
        invalid.pop("research_contract_version")
        with self.assertRaisesRegex(ValueError, "EXPLICIT_V2_CORE_CONTRACT"):
            build_v2_worker(invalid, store=object(), backend=object())

        opened = dict(config, economic_experiment_authorized=True)
        with self.assertRaisesRegex(ValueError, "ECONOMIC_AUTHORITY_MUST_REMAIN_FALSE"):
            build_v2_worker(opened, store=object(), backend=object())

    def test_research_stage_adds_trial_candidate_and_leakage_sidecars_atomically(self):
        output = ENGINE_REGISTRY["fundamental"].run(
            {"source_ref": "synthetic://fundamental"},
            EngineContext("RUN", synthetic_only=True),
        )
        source_path = "research/research_os/sources/example.json"
        task = {"task_id": "TASK-1", "task_type": "FUNDAMENTAL_RESEARCH", "inputs": {"documentary_source": source_path}}
        snapshot = FakeSnapshot({ACTIVE_EPOCH_PATH: self.epoch(), source_path: {
            "documentary_packet": {"available_at": "2025-12-01T00:00:00Z"}}})
        base_result = {
            "stage": "document_or_fundamental_research",
            "engine_output": output,
            "source_path": "research/research_os/sources/example.json",
            "source_blob": "b" * 40,
            "reasoning": {"classification": "UNVERIFIED_MODEL_COMMENTARY"},
        }
        with patch.object(CanonicalStageExecutor, "execute", return_value=(base_result, {}, "CONTINUE")):
            result, writes, status = V2StageExecutor().execute(
                snapshot, task, "fundamental_events", "document_or_fundamental_research",
                "2026-10-20T02:00:00Z", "oracle-v2.fundamental_events",
            )
        self.assertEqual(status, "CONTINUE")
        self.assertIn(v2_artifact_path(task, "research_trial.json"), writes)
        self.assertIn(v2_artifact_path(task, "candidate_draft.json"), writes)
        self.assertIn(v2_artifact_path(task, "leakage.json"), writes)
        self.assertEqual(result["research_contract_version"], "v2-core")
        self.assertFalse(result["outcome_accessed"])

    def test_validation_handoff_binds_v2_candidate_trial_and_epoch(self):
        task = {"task_id": "PRODUCER", "task_type": "FUNDAMENTAL_RESEARCH"}
        child_path = "research/research_os/tasks/VALIDATE-H1.json"
        child = {"task_id": "VALIDATE-H1", "task_type": "VALIDATION", "inputs": {}}
        snapshot = FakeSnapshot({ACTIVE_EPOCH_PATH: self.epoch()})
        with patch.object(CanonicalStageExecutor, "execute", return_value=({"stage": "validation_handoff"}, {child_path: child}, "CONTINUE")):
            result, writes, _ = V2StageExecutor().execute(
                snapshot, task, "fundamental_events", "validation_handoff",
                "2026-10-20T02:10:00Z", "oracle-v2.fundamental_events",
            )
        inputs = writes[child_path]["inputs"]
        self.assertEqual(inputs["research_contract_version"], "v2-core")
        self.assertEqual(inputs["research_epoch_id"], "E1")
        self.assertEqual(inputs["v2_candidate"], v2_artifact_path(task, "candidate_frozen.json"))
        self.assertEqual(inputs["v2_trial"], v2_artifact_path(task, "research_trial.json"))
        self.assertEqual(result["v2_validation_handoff"]["task"], "VALIDATE-H1")

    def test_independent_validation_emits_separate_v2_validator_state(self):
        candidate = self.v2_candidate()
        candidate_path = "research/research_os/artifacts/PRODUCER/oracle-v2/candidate_frozen.json"
        task = {
            "task_id": "VALIDATE-H1",
            "task_type": "VALIDATION",
            "inputs": {
                "v2_candidate": candidate_path,
                "research_epoch_id": "E1",
            },
        }
        snapshot = FakeSnapshot({ACTIVE_EPOCH_PATH: self.epoch(), candidate_path: candidate,
                                 v2_artifact_path(task, "research_trial.json"): self.v2_trial(candidate)})
        from research.research_os.expansion.v2_core import build_epoch_manifest
        task["inputs"]["epoch_manifest_hash"] = build_epoch_manifest(self.epoch())["epoch_manifest_hash"]
        base = {
            "stage": "independent_validation",
            "validation": {"status": "PASS", "failures": []},
            "screen": {"status": "PASS"},
            "reasoning": {"backend_health": {"model": "gpt-oss-10.2b-q4-k-m"}},
        }
        proof = dict.fromkeys(("information_isolation", "retrieval_independence", "cognitive_independence", "state_isolation"), True)
        proof.update(retrieval={"fixture": "separate unit contract; actual retrieval tested separately"}, process={"pid": 2})
        with patch("research.research_os.expansion.v2_stage_executor.independent_context", return_value=proof), \
                patch.object(CanonicalStageExecutor, "execute", return_value=(base, {}, "CONTINUE")):
            result, writes, _ = V2StageExecutor().execute(
                snapshot, task, "independent_challenge", "independent_validation",
                "2026-10-20T02:20:00Z", "oracle-v2.independent_challenge",
            )
        validator = writes[v2_artifact_path(task, "validator.json")]
        self.assertEqual(validator["scientific_decision"], "PASS")
        self.assertNotEqual(validator["producer_identity_hash"], validator["validator_state_identity_hash"])
        self.assertEqual(result["v2_scientific_decision"], "PASS")

    def test_claim_restriction_can_emit_frozen_export_intent_without_evaluation(self):
        candidate = self.v2_candidate()
        producer_candidate_path = "research/research_os/artifacts/PRODUCER/oracle-v2/candidate_frozen.json"
        producer_trial_path = "research/research_os/artifacts/PRODUCER/oracle-v2/research_trial.json"
        task = {
            "task_id": "VALIDATE-H1",
            "task_type": "VALIDATION",
            "inputs": {
                "v2_candidate": producer_candidate_path,
                "v2_trial": producer_trial_path,
                "research_epoch_id": "E1",
            },
        }
        from research.research_os.expansion.v2_core import build_epoch_manifest
        task["inputs"]["epoch_manifest_hash"] = build_epoch_manifest(self.epoch())["epoch_manifest_hash"]
        trial = self.v2_trial(candidate)
        validator = build_validator_result({
            "hypothesis_id": "H1", "generation_id": "G1",
            "candidate_hash": candidate["candidate_hash"],
            "validator_identity": "validator", "validator_version": "v2",
            "validator_model": "gpt-oss", "validator_prompt_hash": "p",
            "validator_context_hash": "c", "validator_retrieval_manifest_hash": "r",
            "execution_state": "COMPLETE", "scientific_decision": "PASS",
            "epistemic_blockers": [],
            "independence_evidence": dict.fromkeys(("information_isolation", "retrieval_independence", "cognitive_independence", "state_isolation"), True),
        })
        readiness = {
            "status": V1_READY,
            "experiment_plan": {
                "plan": {"protocol_hash": "d" * 64},
                "frozen_protocol": {
                    "cost_assumptions": {"model_id": "cost-v1"},
                    "capacity_assumptions": {"model_id": "capacity-v1"},
                    "multiplicity_family": "F1",
                },
            },
            "source_qualifications": [{"snapshot_hash": "e" * 64, "route_hash": "f" * 64}],
            "trial_accounting": {"observed_attempt_count": 1},
        }
        validation_stage_path = artifact_path(task, "independent_validation")
        values = {
            ACTIVE_EPOCH_PATH: self.epoch(),
            producer_candidate_path: candidate,
            producer_trial_path: trial,
            v2_artifact_path(task, "validator.json"): validator,
            validation_stage_path: {"readiness": readiness},
        }
        snapshot = FakeSnapshot(values)
        with patch.object(CanonicalStageExecutor, "execute", return_value=({"stage": "claim_restriction", "blockers": []}, {}, "CONTINUE")):
            result, writes, _ = V2StageExecutor().execute(
                snapshot, task, "independent_challenge", "claim_restriction",
                "2026-10-20T02:30:00Z", "oracle-v2.independent_challenge",
            )
        export = writes[v2_artifact_path(task, "frozen_export_intent.json")]
        self.assertEqual(export["event_type"], "FROZEN_EXPORT_INTENT")
        self.assertEqual(export["export_bundle_hash"], canonical_hash({
            key: value for key, value in export.items() if key != "export_bundle_hash"
        }))
        self.assertEqual(export["evaluation_plane_status"], "SEALED")
        self.assertEqual(export["evaluation_ingest_status"], "NOT_ATTEMPTED_V2_CORE")
        self.assertFalse(export["economic_experiment_authorized"])
        self.assertFalse(export["prospective_observation_authorized"])
        self.assertEqual(result["v2_claim_ceiling"], "READY_FOR_AUTHORIZED_ECONOMIC_TEST_ONLY")

    def real_worker(self):
        from research.research_os.tests import test_oracle_worker as fixture
        harness = fixture.WorkerTests()
        harness.setUp()
        self.addCleanup(harness.tearDown)
        harness.producer()
        harness.now = datetime(2026, 10, 20, 2, tzinfo=timezone.utc)
        worker = build_v2_worker(self.worker_config(), store=harness.store, backend=harness.model)
        worker.now = lambda: harness.now
        return harness, worker

    def test_real_git_claim_counts_ideation_before_crash_and_replay(self):
        harness, worker = self.real_worker()
        worker.wake()
        def crash(point):
            if point == "after_claim":
                raise RuntimeError("process lost before ideation")
        worker.fault = crash
        with self.assertRaises(RuntimeError):
            worker.wake()
        task = harness.read("tasks/PRODUCER-TEST.json")
        intent = harness.read(task["execution"]["v2_trial_intent"].removeprefix("research/research_os/"))
        self.assertEqual(intent["state"], "STARTED_BEFORE_IDEATION")
        self.assertEqual(harness.model.calls, 0)
        harness.now += timedelta(seconds=601)
        resumed = build_v2_worker(self.worker_config(), store=harness.store, backend=harness.model)
        resumed.now = lambda: harness.now
        result = resumed.wake()
        self.assertEqual(result["stage"], "document_or_fundamental_research")
        trial_path = v2_artifact_path(task, "research_trial.json").removeprefix("research/research_os/")
        trial = harness.read(trial_path)
        self.assertEqual(len(trial["ideation_intents"]), 2)
        self.assertEqual(trial["retry_count"], 1)
        self.assertEqual(trial["proposal_count"], 1)
        self.assertEqual(trial["earlier_attempt_proposals"], "UNKNOWN_IF_NO_DURABLE_COMPLETION")
        with harness.store.snapshot() as snapshot:
            priorities = [snapshot.read(p) for p in snapshot.blobs if "/oracle-v2/priority/" in p]
        self.assertTrue(priorities)
        self.assertTrue(all(p["selected_task"] == "PRODUCER-TEST" for p in priorities))

    def test_real_git_epoch_change_cannot_relabel_existing_trial(self):
        harness, worker = self.real_worker()
        worker.wake()
        # This is a governed test fixture update, outside worker-write paths.
        import json, subprocess
        from research.research_os.tests import test_oracle_worker as fixture
        raw = harness.store._git("show", "refs/quant/observed:" + ACTIVE_EPOCH_PATH)
        epoch = json.loads(raw); epoch["knowledge_cutoff"] = "2026-10-19T00:00:00Z"
        subprocess.run(["git", "-C", str(harness.seed), "pull", str(harness.remote), "recovery"], check=True, capture_output=True)
        (harness.seed / ACTIVE_EPOCH_PATH).write_text(json.dumps(epoch))
        fixture.git(harness.seed, "add", "."); fixture.git(harness.seed, "commit", "-m", "test epoch policy update")
        fixture.git(harness.seed, "push", str(harness.remote), "HEAD:recovery")
        with self.assertRaisesRegex(RuntimeError, "EPOCH_OR_POLICY_CHANGED"):
            worker.wake()
        self.assertEqual(harness.read("tasks/PRODUCER-TEST.json")["lease"]["generation"], 1)

    def test_source_after_epoch_cutoff_is_blocked_before_model_generation(self):
        task = {"task_id": "TASK-1", "task_type": "FUNDAMENTAL_RESEARCH", "inputs": {
            "documentary_source": "research/research_os/sources/future.json"}}
        snapshot = FakeSnapshot({ACTIVE_EPOCH_PATH: self.epoch(), task["inputs"]["documentary_source"]: {
            "documentary_packet": {"available_at": "2026-10-21T00:00:00Z"}}})
        with patch.object(CanonicalStageExecutor, "execute") as base:
            with self.assertRaisesRegex(RuntimeError, "SOURCE_PIT_NOT_QUALIFIED"):
                V2StageExecutor().execute(snapshot, task, "fundamental_events", "document_or_fundamental_research",
                                          "2026-10-20T02:00:00Z", "oracle-v2")
            base.assert_not_called()

    def test_real_git_validator_requires_separate_process_and_reconstructs_primary_evidence(self):
        from copy import deepcopy
        from research.research_os.expansion.v2_independence import independent_context, process_identity, AXES
        import subprocess, sys, json
        harness, worker = self.real_worker()
        worker.wake(); worker.wake()
        task = harness.read("tasks/PRODUCER-TEST.json")
        with harness.store.snapshot() as snapshot:
            candidate = snapshot.read(v2_artifact_path(task, "candidate_draft.json"))
            with self.assertRaisesRegex(RuntimeError, "DISTINCT_PROCESS_NOT_PROVEN"):
                independent_context(snapshot, candidate)
            code = """
import json,sys
from pathlib import Path
from research.research_os.github_state import GitHubStateStore
from research.research_os.expansion.v2_independence import independent_context
s=GitHubStateStore(cache=Path(sys.argv[1]),repository='fixture/repo',branch='recovery')
s.remote=sys.argv[2]
with s.snapshot() as snapshot:
    print(json.dumps(independent_context(snapshot,snapshot.read(sys.argv[3]))))
"""
            actual = subprocess.run([sys.executable, "-c", code, str(harness.root / "validator-cache"),
                                     str(harness.remote), v2_artifact_path(task, "candidate_draft.json")],
                                    capture_output=True, text=True, check=True, timeout=60)
            proof = json.loads(actual.stdout)
            self.assertTrue(all(proof[axis] is True for axis in AXES))
            self.assertNotEqual(proof["process"], candidate["producer_identity"]["process"])
            different = dict(process_identity(), pid=-1)
            with patch("research.research_os.expansion.v2_independence.process_identity", return_value=different):
                proof = independent_context(snapshot, candidate)
                self.assertTrue(all(proof[axis] is True for axis in AXES))
                self.assertEqual(proof["retrieval"]["source_blob"], candidate["evidence_manifest"]["source_blob"])
                forged = deepcopy(candidate); forged["evidence_manifest"]["source_blob"] = "0" * 40
                with self.assertRaisesRegex(RuntimeError, "SOURCE_BINDING_NOT_PROVEN"):
                    independent_context(snapshot, forged)
                forged = deepcopy(candidate); forged["evidence_manifest"]["source_candidate_hash"] = "0" * 64
                with self.assertRaisesRegex(RuntimeError, "RECONSTRUCTION_MISMATCH"):
                    independent_context(snapshot, forged)


if __name__ == "__main__":
    unittest.main()

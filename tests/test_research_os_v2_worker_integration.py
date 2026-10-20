import unittest
from unittest.mock import patch

from research.research_os.engines.builtin import ENGINE_REGISTRY
from research.research_os.engines.protocol import EngineContext
from research.research_os.expansion.economic_test_readiness_v1 import READY as V1_READY
from research.research_os.expansion.v2_core import (
    build_candidate,
    build_research_trial,
    build_validator_result,
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
            "evidence_manifest": {"sources": ["S1"]},
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
        task = {"task_id": "TASK-1", "task_type": "FUNDAMENTAL_RESEARCH"}
        snapshot = FakeSnapshot({ACTIVE_EPOCH_PATH: self.epoch()})
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
        snapshot = FakeSnapshot({ACTIVE_EPOCH_PATH: self.epoch(), candidate_path: candidate})
        from research.research_os.expansion.v2_core import build_epoch_manifest
        task["inputs"]["epoch_manifest_hash"] = build_epoch_manifest(self.epoch())["epoch_manifest_hash"]
        base = {
            "stage": "independent_validation",
            "validation": {"status": "PASS", "failures": []},
            "screen": {"status": "PASS"},
            "reasoning": {"backend_health": {"model": "gpt-oss-10.2b-q4-k-m"}},
        }
        with patch.object(CanonicalStageExecutor, "execute", return_value=(base, {}, "CONTINUE")):
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
        trial = build_research_trial({
            "research_trial_id": "T1", "research_epoch_id": "E1",
            "trial_type": "RESEARCH_GENERATION_TRIAL", "model_identity": "DETERMINISTIC_ENGINE",
            "prompt_hash": "p", "context_hash": "c", "retrieval_manifest_hash": "r",
            "source_packet_hash": "s", "generated_at": "2026-10-20T02:00:00Z",
            "sampling_parameters": {"mode": "deterministic"},
            "generated_proposals": [{"id": "P1"}], "discarded_proposals": [], "retry_count": 0,
        })
        validator = build_validator_result({
            "hypothesis_id": "H1", "generation_id": "G1",
            "validator_identity": "validator", "validator_version": "v2",
            "validator_model": "gpt-oss", "validator_prompt_hash": "p",
            "validator_context_hash": "c", "validator_retrieval_manifest_hash": "r",
            "execution_state": "COMPLETE", "scientific_decision": "PASS",
            "epistemic_blockers": [],
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
        self.assertEqual(export["evaluation_plane_status"], "SEALED")
        self.assertEqual(export["evaluation_ingest_status"], "NOT_ATTEMPTED_V2_CORE")
        self.assertFalse(export["economic_experiment_authorized"])
        self.assertFalse(export["prospective_observation_authorized"])
        self.assertEqual(result["v2_claim_ceiling"], "READY_FOR_AUTHORIZED_ECONOMIC_TEST_ONLY")


if __name__ == "__main__":
    unittest.main()

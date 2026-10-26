import unittest

from research.research_os.expansion.v2_core import CLOSED_AUTHORITY, V2ContractError, build_candidate
from research.research_os.expansion.v2_pipeline import run_pre_outcome_pipeline


class V2PipelineTests(unittest.TestCase):
    def bundle(self):
        bundle = {
            "authority": CLOSED_AUTHORITY,
            "epoch": {
                "research_epoch_id": "E1",
                "parent_epoch_id": None,
                "opened_at": "2026-10-20T01:00:00Z",
                "knowledge_cutoff": "2026-10-20T00:00:00Z",
                "research_window": {"start": "2026-10-20T01:00:00Z", "end": "2026-10-27T01:00:00Z"},
                "export_cutoff": "2026-10-26T01:00:00Z",
                "close_policy": "PREDECLARED_COMPOSITE",
                "feedback_release_policy": {"mode": "AFTER_CLOSE_AND_GOVERNED_RELEASE"},
                "research_policy_hash": "r" * 64,
                "model_routing_policy_hash": "m" * 64,
                "allowed_model_set": ["gpt-oss-10.2b-q4-k-m"],
                "allowed_model_change_policy": "WITHIN_ALLOWED_SET_ONLY",
                "source_policy_hash": "s" * 64,
                "retrieval_policy_hash": "q" * 64,
                "validator_policy_hash": "v" * 64,
                "max_candidate_exports": 10,
                "scheduled_close_at": "2026-10-27T01:00:00Z",
                "epoch_knowledge_parent": None,
                "epoch_feedback_dependencies": [],
                "contamination_status": "CLEAN",
            },
            "trial": {
                "research_trial_id": "T1", "research_epoch_id": "E1",
                "trial_type": "RESEARCH_GENERATION_TRIAL",
                "model_identity": "gpt-oss-10.2b-q4-k-m", "prompt_hash": "p",
                "context_hash": "c", "retrieval_manifest_hash": "r", "source_packet_hash": "s",
                "generated_at": "2026-10-20T01:10:00Z",
                "sampling_parameters": {"temperature": 0},
                "generated_proposals": [{"id": "P1"}, {"id": "P2"}],
                "discarded_proposals": [{"id": "P2", "reason": "duplicate"}],
                "retry_count": 0,
            },
            "candidate": {
                "hypothesis_id": "H1", "generation_id": "G1",
                "research_trial_id": "T1", "research_epoch_id": "E1",
                "family": "fundamental", "claim": "bounded claim",
                "mechanism_statement": "cash generation mechanism",
                "universe": ["AAPL"], "clock": "publication", "horizon": "5d",
                "economic_expression": {"instrument": "equity", "direction": "UNKNOWN"},
                "evidence_manifest": {"sources": ["S1"]},
                "falsification_scope": "counterevidence X",
                "decision_map": {"fails": "KILL", "survives": "EXPLORE"},
                "known_confounders": [],
                "disconfirmation_manifest": {"attempted": True},
                "producer_identity": {"worker": "producer-a"},
                "extension": {
                    "type": "FundamentalExtension", "issuer": "AAPL",
                    "business_driver": "services", "valuation_transmission": "cash generation"
                },
            },
            "validator": {
                "hypothesis_id": "H1", "generation_id": "G1",
                "validator_identity": "validator-a", "validator_version": "2",
                "validator_model": "gpt-oss-10.2b-q4-k-m", "validator_prompt_hash": "vp",
                "validator_context_hash": "vc", "validator_retrieval_manifest_hash": "vr",
                "execution_state": "COMPLETE", "scientific_decision": "PASS",
                "epistemic_blockers": [],
            },
            "status": {
                "scientific_maturity": "VALIDATED",
                "experiment_readiness": "READY",
                "portfolio_relationship": "DISTINCT",
                "authority": "CLOSED",
            },
            "blinding": {"owner_status": "BLINDED", "supervisor_status": "BLINDED"},
            "priority_policy_version": "P1",
            "priority_eligible": [{
                "task_id": "H1", "priority": 10, "reason_codes": ["READY_VALIDATED"],
                "resource_cost": 1, "starvation_factor": 1,
            }],
            "negative_memory": {
                "negative_knowledge_id": "N1", "failure_scope": "none-yet",
                "assumptions": [], "regime_context": {}, "source_context": {},
                "failure_reason": "NO_FAILURE", "revisit_conditions": [],
                "revisit_policy": "ON_NEW_EVIDENCE",
            },
            "export": {
                "candidate_hash": "AUTO", "research_trial_history_hash": "AUTO",
                "research_epoch_id": "AUTO", "epoch_manifest_hash": "AUTO",
                "protocol_hash": "d" * 64, "source_snapshot_hashes": ["e" * 64],
                "pit_manifest_hash": "f" * 64, "universe": ["AAPL"], "clock": "publication",
                "horizon": "5d", "economic_expression": {"instrument": "equity", "direction": "UNKNOWN"},
                "cost_model_declaration": "DECLARED", "capacity_declaration": "DECLARED",
                "multiplicity_declaration": "DECLARED", "validator_artifact_hash": "AUTO",
                "research_head": "2" * 40,
            },
            "leakage_classification": {
                "source_pit": "PASS", "model_pit": "NOT_PROVABLE",
                "historical_generation_status": "HISTORICAL_IDEA_GENERATION_NOT_PROVABLY_PIT",
            },
            "validator_independence_qualified": True,
            "feedback_lineage_qualified": True,
            "bounded_orchestration_qualified": True,
        }
        bundle["validator"]["candidate_hash"] = build_candidate(bundle["candidate"])["candidate_hash"]
        return bundle

    def test_end_to_end_pre_outcome_receipt(self):
        receipt = run_pre_outcome_pipeline(self.bundle())
        self.assertEqual(receipt["status"], "READY_FOR_AUTHORIZED_ECONOMIC_TEST_ONLY")
        self.assertEqual(receipt["system_qualification"], "AUTONOMOUS_PRE_OUTCOME_RESEARCH_PIPELINE_QUALIFIED")
        self.assertFalse(receipt["outcome_accessed"])
        self.assertTrue(all(value is False for value in receipt["authority"].values()))

    def test_outcome_key_anywhere_in_research_bundle_fails_closed(self):
        bundle = self.bundle()
        bundle["hidden"] = {"outcome": {"return": 0.12}}
        with self.assertRaisesRegex(V2ContractError, "OUTCOME_DATA_VISIBLE_TO_RESEARCH"):
            run_pre_outcome_pipeline(bundle)

    def test_validator_block_cannot_export(self):
        bundle = self.bundle()
        bundle["validator"]["scientific_decision"] = "BLOCK"
        with self.assertRaisesRegex(V2ContractError, "EXPORT_REQUIRES_COMPLETED_VALIDATOR_PASS"):
            run_pre_outcome_pipeline(bundle)

    def test_broken_blinding_cannot_export(self):
        bundle = self.bundle()
        bundle["blinding"]["supervisor_status"] = "OUTCOME_VIEWED"
        with self.assertRaisesRegex(V2ContractError, "BLINDING_INTEGRITY_BROKEN"):
            run_pre_outcome_pipeline(bundle)


if __name__ == "__main__":
    unittest.main()

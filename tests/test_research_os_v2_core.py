import unittest
from copy import deepcopy

from research.research_os.expansion.v2_core import (
    CLOSED_AUTHORITY,
    V2ContractError,
    assert_authority_closed,
    assert_epoch_update,
    assert_model_allowed,
    blinding_integrity,
    build_candidate,
    build_epoch_manifest,
    build_evaluation_ingest_receipt,
    build_frozen_export_intent,
    build_negative_memory,
    build_priority_decision,
    build_research_trial,
    build_validator_result,
    classify_model_pit,
    qualify_v2_core,
    release_feedback,
    validate_multidimensional_status,
    validate_reverse_message,
)


class V2CoreContractTests(unittest.TestCase):
    def epoch_payload(self):
        return {
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
            "allowed_model_set": ["gpt-oss-10.2b-q4-k-m", "senior-review-model"],
            "allowed_model_change_policy": "WITHIN_ALLOWED_SET_ONLY",
            "source_policy_hash": "s" * 64,
            "retrieval_policy_hash": "q" * 64,
            "validator_policy_hash": "v" * 64,
            "max_candidate_exports": 10,
            "scheduled_close_at": "2026-10-27T01:00:00Z",
            "epoch_knowledge_parent": None,
            "epoch_feedback_dependencies": [],
            "contamination_status": "CLEAN",
        }

    def candidate_payload(self, family="fundamental"):
        extensions = {
            "fundamental": {
                "type": "FundamentalExtension", "issuer": "AAPL",
                "business_driver": "services", "valuation_transmission": "cash generation"
            },
            "event": {
                "type": "EventExtension", "event": "filing", "availability_time": "2026-10-20T00:00:00Z",
                "event_clock": "publication", "reaction_channel": "repricing", "revision_policy": "immutable"
            },
            "forced_flow": {
                "type": "ForcedFlowExtension", "forced_constrained_actor": "index_fund",
                "binding_constraint": "rebalance", "payer": "passive_fund", "instrument": "equity",
                "timing": "close"
            },
            "quant": {
                "type": "QuantExtension", "signal_definition": "zscore", "observation_clock": "t0",
                "decision_clock": "t0+1", "execution_clock": "t0+2", "data_route": "pit-route",
                "multiplicity_family": "family-1"
            },
        }
        return {
            "hypothesis_id": "H1",
            "generation_id": "G1",
            "research_trial_id": "T1",
            "research_epoch_id": "E1",
            "family": family,
            "claim": "bounded claim",
            "mechanism_statement": "bounded mechanism",
            "universe": ["AAPL"],
            "clock": "publication",
            "horizon": "5d",
            "economic_expression": {"instrument": "equity", "direction": "UNKNOWN"},
            "evidence_manifest": {"sources": ["S1"]},
            "falsification_scope": "counterevidence X",
            "decision_map": {"fails": "KILL", "survives": "EXPLORE"},
            "known_confounders": [],
            "disconfirmation_manifest": {"attempted": True},
            "producer_identity": {"worker": "producer-a"},
            "extension": extensions[family],
        }

    def test_authority_closed(self):
        assert_authority_closed(CLOSED_AUTHORITY)
        opened = dict(CLOSED_AUTHORITY, economic_experiment_authorized=True)
        with self.assertRaisesRegex(V2ContractError, "AUTHORITY_OPEN"):
            assert_authority_closed(opened)

    def test_epoch_is_hashed_and_close_policy_freezes_after_export(self):
        epoch = build_epoch_manifest(self.epoch_payload())
        self.assertEqual(len(epoch["epoch_manifest_hash"]), 64)
        mutated = deepcopy(epoch)
        mutated["close_policy"] = "TIME_BOUND"
        with self.assertRaisesRegex(V2ContractError, "POST_EXPORT_EPOCH_MUTATION"):
            assert_epoch_update(epoch, mutated, first_export_accepted=True)
        assert_epoch_update(epoch, mutated, first_export_accepted=False)

    def test_epoch_rejects_bad_temporal_order(self):
        payload = self.epoch_payload()
        payload["knowledge_cutoff"] = "2026-10-21T00:00:00Z"
        with self.assertRaisesRegex(V2ContractError, "KNOWLEDGE_CUTOFF_AFTER_OPEN"):
            build_epoch_manifest(payload)

    def test_model_policy(self):
        epoch = build_epoch_manifest(self.epoch_payload())
        assert_model_allowed(epoch, "gpt-oss-10.2b-q4-k-m")
        with self.assertRaisesRegex(V2ContractError, "MODEL_OUTSIDE_EPOCH_POLICY"):
            assert_model_allowed(epoch, "unapproved")

    def test_model_pit_distinct_from_source_pit(self):
        result = classify_model_pit(source_pit=True, model_knowledge_cutoff_status="NOT_PROVABLE")
        self.assertEqual(result["historical_generation_status"], "HISTORICAL_IDEA_GENERATION_NOT_PROVABLY_PIT")

    def test_trial_accounting_counts_discarded_proposals(self):
        trial = build_research_trial({
            "research_trial_id": "T1", "research_epoch_id": "E1",
            "trial_type": "RESEARCH_GENERATION_TRIAL",
            "model_identity": "gpt-oss", "prompt_hash": "p", "context_hash": "c",
            "retrieval_manifest_hash": "r", "source_packet_hash": "s",
            "generated_at": "2026-10-20T01:00:00Z", "sampling_parameters": {"temperature": 0},
            "generated_proposals": [{"id": 1}, {"id": 2}, {"id": 3}],
            "discarded_proposals": [{"id": 1, "reason": "duplicate"}, {"id": 2, "reason": "weak"}],
            "retry_count": 1,
        })
        self.assertEqual(trial["proposal_count"], 3)
        self.assertEqual(trial["discard_count"], 2)

    def test_family_specific_candidate_contracts(self):
        for family in ("fundamental", "event", "forced_flow", "quant"):
            candidate = build_candidate(self.candidate_payload(family))
            self.assertEqual(len(candidate["candidate_hash"]), 64)

    def test_family_extension_mismatch_blocks(self):
        payload = self.candidate_payload("fundamental")
        payload["extension"] = self.candidate_payload("quant")["extension"]
        with self.assertRaisesRegex(V2ContractError, "FAMILY_EXTENSION_MISMATCH"):
            build_candidate(payload)

    def test_validator_infrastructure_failure_is_not_scientific_block(self):
        result = build_validator_result({
            "hypothesis_id": "H1", "generation_id": "G1",
            "validator_identity": "validator-a", "validator_version": "2",
            "validator_model": "gpt-oss", "validator_prompt_hash": "p",
            "validator_context_hash": "c", "validator_retrieval_manifest_hash": "r",
            "execution_state": "RETRYABLE_ERROR",
            "epistemic_blockers": [],
        })
        self.assertNotIn("scientific_decision", result)

    def test_complete_validator_must_decide(self):
        payload = {
            "hypothesis_id": "H1", "generation_id": "G1",
            "validator_identity": "validator-a", "validator_version": "2",
            "validator_model": "gpt-oss", "validator_prompt_hash": "p",
            "validator_context_hash": "c", "validator_retrieval_manifest_hash": "r",
            "execution_state": "COMPLETE", "epistemic_blockers": [],
        }
        with self.assertRaisesRegex(V2ContractError, "REQUIRES_PASS_OR_BLOCK"):
            build_validator_result(payload)
        payload["scientific_decision"] = "PASS"
        self.assertEqual(build_validator_result(payload)["scientific_decision"], "PASS")

    def test_multidimensional_status(self):
        validate_multidimensional_status({
            "scientific_maturity": "VALIDATED",
            "experiment_readiness": "READY",
            "portfolio_relationship": "REPLICATION",
            "authority": "CLOSED",
        })

    def test_priority_is_explainable_and_rejects_outcome_like_signal(self):
        decision = build_priority_decision(policy_version="P1", eligible=[
            {"task_id": "B", "priority": 10, "reason_codes": ["AGE"], "resource_cost": 2, "starvation_factor": 0},
            {"task_id": "A", "priority": 10, "reason_codes": ["BLOCKS_VALIDATION"], "resource_cost": 1, "starvation_factor": 1},
        ])
        self.assertEqual(decision["selected_task"], "A")
        with self.assertRaisesRegex(V2ContractError, "OUTCOME_LIKE_PRIORITY"):
            build_priority_decision(policy_version="P1", eligible=[{
                "task_id": "X", "priority": 1, "reason_codes": [], "resource_cost": 1,
                "starvation_factor": 0, "expected_return": 0.2,
            }])

    def test_negative_memory_requires_scope_for_permanent_claim(self):
        base = {
            "negative_knowledge_id": "N1", "failure_scope": "regime-1", "assumptions": [],
            "regime_context": {}, "source_context": {}, "failure_reason": "weak evidence",
            "revisit_conditions": ["new source"], "revisit_policy": "ON_CONDITION",
        }
        self.assertEqual(len(build_negative_memory(base)["negative_knowledge_hash"]), 64)
        base["failure_reason"] = "IDEA_FALSE_FOREVER"
        with self.assertRaisesRegex(V2ContractError, "UNSCOPED_PERMANENT"):
            build_negative_memory(base)

    def test_export_rejects_outcome_data(self):
        base = {
            "candidate_hash": "a" * 64, "research_trial_history_hash": "b" * 64,
            "research_epoch_id": "E1", "epoch_manifest_hash": "c" * 64,
            "protocol_hash": "d" * 64, "source_snapshot_hashes": ["e" * 64],
            "pit_manifest_hash": "f" * 64, "universe": ["AAPL"], "clock": "t0", "horizon": "5d",
            "economic_expression": {"direction": "UNKNOWN"}, "cost_model_declaration": "DECLARED",
            "capacity_declaration": "DECLARED", "multiplicity_declaration": "DECLARED",
            "validator_artifact_hash": "1" * 64, "research_head": "2" * 40,
        }
        export = build_frozen_export_intent(base)
        self.assertEqual(export["event_type"], "FROZEN_EXPORT_INTENT")
        contaminated = dict(base, outcome={"return": 0.1})
        with self.assertRaisesRegex(V2ContractError, "OUTCOME_DATA_IN_RESEARCH_EXPORT"):
            build_frozen_export_intent(contaminated)

    def test_reverse_channel_is_restricted(self):
        receipt = build_evaluation_ingest_receipt(export_bundle_hash="x" * 64)
        validate_reverse_message(receipt)
        with self.assertRaisesRegex(V2ContractError, "FORBIDDEN_EVALUATION_REVERSE_MESSAGE"):
            build_evaluation_ingest_receipt(export_bundle_hash="x" * 64, message="EVALUATION_COMPLETE")

    def test_blinding_contaminates_when_influencer_views_outcomes(self):
        self.assertEqual(blinding_integrity(owner_status="BLINDED", supervisor_status="BLINDED")["epoch_blinding_integrity"], "PASS")
        self.assertEqual(blinding_integrity(owner_status="OUTCOME_VIEWED", supervisor_status="BLINDED")["epoch_blinding_integrity"], "BROKEN")

    def test_feedback_only_releases_to_successor_after_close(self):
        with self.assertRaisesRegex(V2ContractError, "FEEDBACK_BEFORE_EPOCH_CLOSE"):
            release_feedback(source_epoch_id="E1", successor_epoch_id="E2",
                             source_epoch_closed=False, policy_allows_release=True,
                             feedback_hash="f" * 64)
        event = release_feedback(source_epoch_id="E1", successor_epoch_id="E2",
                                 source_epoch_closed=True, policy_allows_release=True,
                                 feedback_hash="f" * 64)
        self.assertEqual(event["event_type"], "ECONOMIC_FEEDBACK_RELEASED")

    def test_v2_qualification_never_opens_authority(self):
        proof = {
            "authority": CLOSED_AUTHORITY,
            "epoch_contract_qualified": True,
            "ideation_trial_accounting_qualified": True,
            "leakage_classification_qualified": True,
            "candidate_contract_qualified": True,
            "validator_independence_qualified": True,
            "evaluation_membrane_qualified": True,
            "feedback_lineage_qualified": True,
            "priority_policy_qualified": True,
            "negative_memory_qualified": True,
            "multidimensional_status_qualified": True,
            "bounded_orchestration_qualified": True,
        }
        result = qualify_v2_core(proof)
        self.assertEqual(result["status"], "AUTONOMOUS_PRE_OUTCOME_RESEARCH_PIPELINE_QUALIFIED")
        self.assertTrue(all(v is False for v in result["authority"].values()))

    def test_v2_qualification_blocks_missing_gate(self):
        proof = {
            "authority": CLOSED_AUTHORITY,
            "epoch_contract_qualified": True,
        }
        result = qualify_v2_core(proof)
        self.assertEqual(result["status"], "BLOCK")
        self.assertIn("evaluation_membrane_qualified", result["missing_gates"])


if __name__ == "__main__":
    unittest.main()

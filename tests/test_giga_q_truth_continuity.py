"""Hostile pre-outcome handoffs; synthetic objects confer no execution authority."""
from copy import deepcopy
from dataclasses import dataclass
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from research.research_os.scientific_store import sha256_json
from research.research_os.expansion.experiment_outcome_firewall import (
    OutcomeFirewallError, assert_pre_outcome_payload,
)
from research.research_os.expansion.wave2_scientific_economic_bridge import (
    validate_scientific_economic_handoff,
)
from research.research_os.multi_source_ideation_hardening import DurableProposalLedger
from research.research_os.expansion.economic_lifecycle import (
    validate_economic_identity_ref, validate_portfolio_readiness_ref,
)
from tests import test_wave2_c2_scientific_economic_d0_seam as seam_fixture
from research.research_os.expansion.canonical_spine import run_canonical_spine
from research.research_os.queue_replenisher import derive_refill_task, load_frontier
from research.research_os.expansion.v2_core import _scan_forbidden_outcome_keys
from deploy.oracle_live_projection import validate_local_observation_receipt
from research.research_os.tests.test_mega_e_live_receipt_reconciliation import valid_receipt
from research.research_os.tests import test_economic_readiness_integration as readiness_fixture
from research.research_os.expansion.economic_test_readiness_v1 import economic_test_readiness

RESEARCH = Path(__file__).resolve().parents[1] / "research" / "research_os"


def rehash(value, key):
    value[key] = sha256_json({k: v for k, v in value.items() if k != key})
    return value


class ScientificEconomicContinuityTests(unittest.TestCase):
    def setUp(self):
        fixture = seam_fixture.Wave2C2ScientificEconomicD0SeamTests()
        fixture.setUp()
        self.adjudication = fixture.adjudication
        self.econ = fixture.econ_ref
        self.portfolio = fixture.readiness_ref
        self.handoff = fixture.handoff

    def validate(self, handoff):
        validate_scientific_economic_handoff(
            handoff, self.adjudication, self.econ, self.portfolio
        )

    def test_rehashed_copied_claim_and_readiness_cannot_diverge(self):
        for key, value in (
            ("claim_ceiling", "UNBOUNDED_ECONOMIC_EDGE"),
            ("portfolio_structural_mapping_status", "UNKNOWN"),
            ("portfolio_pre_outcome_decision_status", "UNKNOWN"),
        ):
            with self.subTest(field=key):
                changed = rehash({**self.handoff, key: value}, "handoff_hash")
                with self.assertRaises(ValueError):
                    self.validate(changed)

    def test_valid_blocked_adjudication_cannot_be_recast_as_promotable(self):
        self.adjudication.update(verdict="BLOCK", scientific_posture="BLOCKED",
                                 promotion_target=None, reason_codes=["UNRESOLVED"])
        rehash(self.adjudication, "adjudication_hash")
        forged = rehash({**self.handoff,
                         "scientific_adjudication_hash": self.adjudication["adjudication_hash"]},
                        "handoff_hash")
        with self.assertRaises(ValueError):
            self.validate(forged)

    def test_nested_outcome_extension_cannot_be_hash_laundered(self):
        for wrap in (lambda x: x, lambda x: [x], lambda x: (x,),
                     lambda x: json.loads(json.dumps([x]))):
            with self.subTest(wrapper=wrap):
                forged = rehash({**self.handoff, "extra": wrap({"future_returns": [0.1]})},
                                "handoff_hash")
                with self.assertRaises((ValueError, OutcomeFirewallError)):
                    self.validate(forged)

    def test_missing_explicit_closed_economic_ref_is_not_closed_evidence(self):
        for key in ("outcome_accessed", "empirical_return_data_consumed"):
            with self.subTest(field=key):
                changed = deepcopy(self.econ)
                del changed[key]
                rehash(changed, "ref_hash")
                with self.assertRaises(ValueError):
                    validate_economic_identity_ref(changed)

    def test_missing_portfolio_authority_is_not_closed_evidence(self):
        for key in ("economic_experiment_authorized", "prospective_observation_authorized",
                    "real_capital_authorized", "live_trading_authorized", "outcome_accessed",
                    "return_series_consumed"):
            with self.subTest(field=key):
                changed = deepcopy(self.portfolio)
                del changed[key]
                rehash(changed, "ref_hash")
                with self.assertRaises(ValueError):
                    validate_portfolio_readiness_ref(changed, self.econ)

    def test_frozen_execution_semantics_reach_economic_identity(self):
        package = readiness_fixture.fixture()
        expression = package["runner_meta"]["frozen_protocol"]["economic_expression"]
        package["engine_output"]["candidate"]["horizon"] = expression["horizon"]
        result = economic_test_readiness(package, legacy=readiness_fixture.legacy())
        for field, key in (("instrument", "instrument"), ("universe", "universe"),
                           ("timing_clock", "entry_clock"), ("horizon", "horizon")):
            with self.subTest(field=field):
                self.assertEqual(result["identity"]["fields"][field]["value"], expression[key])

    def test_conflicting_candidate_and_frozen_horizon_cannot_be_ready(self):
        package = readiness_fixture.fixture()
        package["engine_output"]["candidate"]["horizon"] = "a different frozen horizon"
        result = economic_test_readiness(package, legacy=readiness_fixture.legacy())
        self.assertEqual(result["status"], "BLOCK")
        self.assertIn("FROZEN_ECONOMIC_IDENTITY_MISMATCH:horizon", result["block_reasons"])


@dataclass
class HiddenOutcome:
    future_returns: list


class RecursiveFirewallContinuityTests(unittest.TestCase):
    def test_alternate_key_order_cannot_mask_a_role(self):
        for pairs in ((('role', 'OUTCOME'), ('ROLE', 'FEATURE')),
                      (('ROLE', 'FEATURE'), ('role', 'OUTCOME'))):
            with self.subTest(pairs=pairs):
                with self.assertRaises(OutcomeFirewallError):
                    assert_pre_outcome_payload(dict(pairs))

    def test_semantic_column_roles_survive_key_normalization_and_json(self):
        for key in ("role", "ROLE", "column_role", "COLUMN_ROLE", "field_role"):
            with self.subTest(key=key):
                with self.assertRaises(OutcomeFirewallError):
                    assert_pre_outcome_payload(json.loads(json.dumps(
                        {"metadata": [{key: "OUTCOME", "values": [0.1]}]})))

    def test_unknown_object_cannot_hide_uninspected_outcomes(self):
        for item in (HiddenOutcome([0.1]), SimpleNamespace(future_returns=[0.1])):
            with self.subTest(type=type(item).__name__):
                with self.assertRaises(OutcomeFirewallError):
                    assert_pre_outcome_payload({"metadata": (item,)})

    def test_passive_ledger_consumes_canonical_outcome_law(self):
        for value in ({"future_returns": [0.1]}, {"role": "OUTCOME", "values": [0.1]},
                      {"real_capital_authorized": True}, {"outcome_opened": True}):
            with self.subTest(value=value):
                with self.assertRaises((ValueError, OutcomeFirewallError)):
                    DurableProposalLedger().persist({"proposal_id": "opaque", "metadata": (value,)})

    def test_safe_provenance_and_unknown_remain_admissible(self):
        value = {"proposal_id": "opaque", "status": "REVIEW_REQUIRED",
                 "economic_result": "NOT_OBSERVED", "outcome_accessed": False,
                 "metadata": {"source": "ref://primary", "uncertainty": "UNKNOWN",
                              "outcome_definition": "preregistered future response"}}
        DurableProposalLedger().persist(value)
        assert_pre_outcome_payload(value)

    def test_v2_reverse_export_scans_json_equivalent_tuple(self):
        self.assertTrue(_scan_forbidden_outcome_keys({"metadata": ({"returns": [0.1]},)}))


class LegacyAndControlContinuityTests(unittest.TestCase):
    def test_legitimate_failed_task_remains_terminal_and_allows_new_work(self):
        result = derive_refill_task(frontier=load_frontier(RESEARCH),
                                    tasks=[{"task_id": "old", "status": "FAILED"}],
                                    created_at="2026-10-24T00:00:00Z")
        self.assertEqual(result["queue"]["terminal_count"], 1)
        self.assertEqual(result["queue"]["unknown_count"], 0)
        self.assertEqual(result["status"], "DERIVED_ONE_READY_TASK")
        self.assertNotEqual(result["task"]["task_id"], "old")

    def test_canonical_memory_refusal_survives_spine_handoff(self):
        fixture = json.loads((RESEARCH / "simulations/aggressive_architecture_fixture.json").read_text())
        task = json.loads((RESEARCH / "simulations/canonical_spine_task.json").read_text())
        for status in ("REVIEW_LEGACY_OVERLAP", "BLOCK_KNOWN_NEGATIVE_SAME_SEMANTIC_FAMILY",
                       "BLOCK_INVALIDATED_PROTOCOL_REPAIR_REQUIRED", "BLOCK_HISTORICAL_BLOCKER_UNRESOLVED",
                       "BLOCK_POSITIVE_INSUFFICIENT_VALIDATION_REQUIRED", "FUTURE_UNKNOWN_STATE"):
            with self.subTest(status=status):
                with patch("research.research_os.legacy.LegacyKnowledgeBase.screen_candidate",
                           return_value={"status": status, "scientific_equivalence": "NOT_ESTABLISHED"}):
                    result = run_canonical_spine(RESEARCH, fixture, task)
                self.assertFalse(result["downstream_executed"])
                self.assertEqual(result["downstream_stage_kinds"], [])
                self.assertEqual(result["legacy"]["screen"]["status"], status)

    def test_unknown_task_state_does_not_prove_empty_queue(self):
        for status in (None, "FUTURE_SCHEMA_STATUS", "RUNNING"):
            with self.subTest(status=status):
                result = derive_refill_task(frontier=load_frontier(RESEARCH),
                                            tasks=[{"task_id": "opaque", "status": status}],
                                            created_at="2026-10-24T00:00:00Z")
                self.assertIsNone(result["task"])
                self.assertEqual(result["status"], "BLOCKED_UNKNOWN_TASK_STATUS")


class LiveObservationContinuityTests(unittest.TestCase):
    def test_terminal_receipt_cannot_mix_lease_generations_or_truncate_provenance(self):
        for change in ({"generation": 3}, {"event_seq": 1}, {"source_commit": None}):
            with self.subTest(change=change):
                value = valid_receipt()
                value["canonical_terminal"] = {
                    "event_id": "task-g2-002", "session_id": value["source"]["session_id"],
                    "generation": 2, "event_seq": 2, "source_commit": "b" * 40,
                    **change,
                }
                with self.assertRaises(ValueError):
                    validate_local_observation_receipt(value)

    def test_terminal_receipt_requires_complete_provenance(self):
        value = valid_receipt()
        value["canonical_terminal"] = {"session_id": value["source"]["session_id"]}
        with self.assertRaises(ValueError):
            validate_local_observation_receipt(value)


if __name__ == "__main__":
    unittest.main()

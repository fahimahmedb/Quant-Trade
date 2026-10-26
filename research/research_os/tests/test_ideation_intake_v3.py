from __future__ import annotations

import tempfile
import unittest
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from quant.state import append_jsonl

from research.research_os.ideation_intake import (
    AUTHORITY_STATE,
    IdeationPolicy,
    ProposalLedger,
    ProposalLedgerCorruption,
    discovery_handoff,
    run_intake_cycle,
    source_binding_from_planner,
)


SNAP_A = "sha256:" + "a" * 64
SNAP_B = "sha256:" + "b" * 64
SNAP_C = "sha256:" + "c" * 64


def source(snapshot=SNAP_A, *, provenance="source://primary", qualified=True):
    return {
        "source_identity": "source:primary",
        "source_snapshot_identity": snapshot,
        "provenance_ref": provenance,
        "qualified": qualified,
        "clocks": {
            "publication_time": "2026-10-01T09:00:00+00:00",
            "public_time": "2026-10-01T09:00:00+00:00",
            "available_time": "2026-10-01T09:01:00+00:00",
            "ingestion_time": "2026-10-01T09:02:00+00:00",
        },
    }


def proposal(**overrides):
    value = {
        "policy_id": "systematic-coverage:v1",
        "policy_family": "SYSTEMATIC_COVERAGE",
        "sources": [source()],
        "mechanism_claim": "Forced benchmark trackers rebalance into the effective close.",
        "mechanism_identity": "forced benchmark rebalance",
        "actor_identity": "passive index funds",
        "universe_identity": "us equities",
        "clock_identity": {
            "name": "effective close",
            "publication_time": "2026-10-01T09:00:00+00:00",
            "public_time": "2026-10-01T09:00:00+00:00",
            "available_time": "2026-10-01T09:01:00+00:00",
        },
        "horizon_identity": "close to next close",
        "falsifiable_claim": {
            "statement": "The defined actor/mechanism relation is observable under the declared clock.",
            "falsifier": "No actor-linked imbalance is observable under the declared universe and clock.",
        },
        "assumptions": ["The source describes the mechanism, not its profitability."],
        "parameters": {"window": 1},
        "parent_proposal_ids": [],
    }
    value.update(overrides)
    return value


class IdeationIntakeV3Tests(unittest.TestCase):
    def ledger(self, directory, **kwargs):
        return ProposalLedger(Path(directory) / "proposal_ledger.jsonl", **kwargs)

    def test_01_identical_proposal_replay_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = self.ledger(directory)
            first = ledger.admit(proposal())
            second = ledger.admit(proposal())
            self.assertFalse(first.replayed)
            self.assertTrue(second.replayed)
            self.assertEqual(first.proposal["proposal_id"], second.proposal["proposal_id"])
            self.assertEqual(first.proposal["admission_disposition"], "ELIGIBLE_FOR_DISCOVERY")
            self.assertEqual(len(ledger.entries()), 1)

    def test_02_lexical_paraphrase_is_not_new_semantics(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = self.ledger(directory)
            first = ledger.admit(proposal())
            changed = proposal(
                mechanism_claim="At the closing event, benchmark followers are forced to rebalance.",
                mechanism_identity="forced benchmark rebalance",
            )
            second = ledger.admit(changed)
            self.assertEqual(first.proposal["novelty_disposition"], "GENUINELY_NOVEL")
            self.assertEqual(second.proposal["novelty_disposition"], "LEXICALLY_DIFFERENT")
            self.assertEqual(second.proposal["admission_disposition"], "REJECTED")
            self.assertIn("NEAR_DUPLICATE", second.proposal["rejection_reasons"])

    def test_03_semantic_duplicate_across_source_snapshot_is_duplicate(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = self.ledger(directory)
            ledger.admit(proposal())
            raw = proposal()
            raw["sources"] = [source(SNAP_B)]
            second = ledger.admit(raw)
            self.assertEqual(second.proposal["novelty_disposition"], "SEMANTICALLY_EQUIVALENT")
            self.assertIn("DUPLICATE", second.proposal["rejection_reasons"])
            self.assertEqual(second.proposal["admission_disposition"], "REJECTED")

    def test_04_parameter_only_variant_is_near_duplicate(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = self.ledger(directory)
            ledger.admit(proposal(parameters={"window": 1}))
            second = ledger.admit(proposal(parameters={"window": 2}))
            self.assertEqual(second.proposal["novelty_disposition"], "PARAMETER_VARIANT")
            self.assertIn("NEAR_DUPLICATE", second.proposal["rejection_reasons"])

    def test_05_mechanism_variant_is_distinguished_and_may_pass_membrane(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = self.ledger(directory)
            ledger.admit(proposal())
            second = ledger.admit(proposal(
                mechanism_claim="Dealer inventory constraints transfer pressure into the close.",
                mechanism_identity="dealer inventory constraint transfer",
            ))
            self.assertEqual(second.proposal["novelty_disposition"], "MECHANISM_VARIANT")
            self.assertEqual(second.proposal["admission_disposition"], "ELIGIBLE_FOR_DISCOVERY")

    def test_06_genuinely_novel_proposal_is_classified_without_edge_claim(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = self.ledger(directory)
            first = ledger.admit(proposal())
            second = ledger.admit(proposal(
                mechanism_claim="Issuer blackout windows change repurchase participation.",
                mechanism_identity="issuer blackout repurchase participation",
                actor_identity="public issuers",
                universe_identity="us issuer repurchases",
                horizon_identity="announcement to blackout start",
            ))
            self.assertEqual(first.proposal["novelty_disposition"], "GENUINELY_NOVEL")
            self.assertEqual(second.proposal["novelty_disposition"], "GENUINELY_NOVEL")
            self.assertEqual(second.proposal["admission_disposition"], "ELIGIBLE_FOR_DISCOVERY")
            self.assertNotIn("edge", second.proposal)

    def test_07_unknown_novelty_never_becomes_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.ledger(directory).admit(proposal(actor_identity="UNKNOWN"))
            self.assertEqual(result.proposal["novelty_disposition"], "UNKNOWN")
            self.assertEqual(result.proposal["admission_disposition"], "REJECTED")
            self.assertIn("UNKNOWN_CRITICAL_FIELD", result.proposal["rejection_reasons"])
            self.assertIn("UNIDENTIFIED_ACTOR", result.proposal["rejection_reasons"])

    def test_08_missing_source_provenance_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            raw = proposal()
            raw["sources"] = [source(provenance="UNKNOWN")]
            result = self.ledger(directory).admit(raw)
            self.assertEqual(result.proposal["admission_disposition"], "REJECTED")
            self.assertIn("UNTRACEABLE_PROVENANCE", result.proposal["rejection_reasons"])

    def test_09_malformed_source_snapshot_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            raw = proposal()
            raw["sources"] = [source("sha256:not-a-digest")]
            result = self.ledger(directory).admit(raw)
            self.assertEqual(result.proposal["admission_disposition"], "REJECTED")
            self.assertIn("MALFORMED", result.proposal["rejection_reasons"])

    def test_10_unresolved_clock_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.ledger(directory).admit(proposal(clock_identity="UNKNOWN"))
            self.assertEqual(result.proposal["novelty_disposition"], "UNKNOWN")
            self.assertIn("UNIDENTIFIED_CLOCK", result.proposal["rejection_reasons"])
            self.assertEqual(result.proposal["admission_disposition"], "REJECTED")

    def test_11_non_falsifiable_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.ledger(directory).admit(proposal(falsifiable_claim="interesting idea"))
            self.assertIn("NON_FALSIFIABLE", result.proposal["rejection_reasons"])
            self.assertEqual(result.proposal["admission_disposition"], "REJECTED")

    def test_12_outcome_contaminated_proposal_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            raw = proposal()
            raw["sharpe"] = 2.1
            result = self.ledger(directory).admit(raw)
            self.assertIn("OUTCOME_CONTAMINATED", result.proposal["rejection_reasons"])
            self.assertEqual(result.admission_evidence["pre_outcome_firewall"], "REJECT")

    def test_13_rejected_historical_idea_remains_memory(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = self.ledger(directory)
            rejected = proposal(falsifiable_claim={"statement": "vague", "falsifier": "UNKNOWN"})
            first = ledger.admit(rejected)
            self.assertEqual(first.proposal["admission_disposition"], "REJECTED")
            second = ledger.admit(proposal())
            self.assertIn("ALREADY_EXPLORED", second.proposal["rejection_reasons"])
            self.assertEqual(second.proposal["admission_disposition"], "REJECTED")
            self.assertEqual(len(ledger.entries()), 2)

    def test_14_concurrent_duplicate_generation_creates_one_attempt_record(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "proposal_ledger.jsonl"

            def submit(_):
                return ProposalLedger(path).admit(proposal()).to_dict()

            with ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(submit, range(16)))
            ledger = ProposalLedger(path)
            self.assertEqual(len(ledger.entries()), 1)
            self.assertEqual(len({row["proposal"]["proposal_id"] for row in results}), 1)
            self.assertEqual(sum(not row["replayed"] for row in results), 1)

    def test_15_repeated_policy_invocation_does_not_create_new_record(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = self.ledger(directory)
            policy = IdeationPolicy(
                "systematic-coverage:v1",
                "SYSTEMATIC_COVERAGE",
                lambda _context: [proposal()],
            )
            first = run_intake_cycle([policy], context={}, ledger=ledger)
            second = run_intake_cycle([policy], context={}, ledger=ledger)
            self.assertEqual(first["new_eligible_count"], 1)
            self.assertEqual(second["new_eligible_count"], 0)
            self.assertEqual(second["status"], "NOOP_NO_NOVEL_PROPOSAL")
            self.assertEqual(len(ledger.entries()), 1)

    def test_16_crash_after_ledger_persistence_retries_idempotently(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "proposal_ledger.jsonl"
            state = {"raised": False}

            def fault(stage, _context):
                if stage == "after_ledger_append" and not state["raised"]:
                    state["raised"] = True
                    raise RuntimeError("synthetic crash")

            with self.assertRaises(RuntimeError):
                ProposalLedger(path, fault_hook=fault).admit(proposal())
            recovered = ProposalLedger(path).admit(proposal())
            self.assertTrue(recovered.replayed)
            self.assertEqual(len(ProposalLedger(path).entries()), 1)

    def test_17_zero_proposal_cycle_is_successful_noop(self):
        with tempfile.TemporaryDirectory() as directory:
            policy = IdeationPolicy(
                "information-value:v1",
                "INFORMATION_VALUE",
                lambda _context: [],
            )
            result = run_intake_cycle([policy], context={}, ledger=self.ledger(directory))
            self.assertEqual(result["status"], "NOOP_NO_ADMISSIBLE_PROPOSAL")
            self.assertEqual(result["generated_count"], 0)
            self.assertFalse(result["scheduler_mutation"])

    def test_18_policy_may_return_only_inadmissible_ideas(self):
        with tempfile.TemporaryDirectory() as directory:
            raw = proposal()
            raw["sources"] = [source(provenance="UNKNOWN")]
            policy = IdeationPolicy("information-value:v1", "INFORMATION_VALUE", lambda _context: [raw])
            result = run_intake_cycle([policy], context={}, ledger=self.ledger(directory))
            self.assertEqual(result["status"], "NOOP_NO_ADMISSIBLE_PROPOSAL")
            self.assertEqual(result["new_eligible_count"], 0)

    def test_19_generative_backend_unsupported_claims_become_assumptions(self):
        with tempfile.TemporaryDirectory() as directory:
            raw = proposal()
            raw.pop("policy_id", None)
            raw.pop("policy_family", None)
            raw["unsupported_claims"] = ["This mechanism definitely has alpha."]
            policy = IdeationPolicy(
                "divergent:v1",
                "DIVERGENT_EXPLORATION",
                lambda _context: [raw],
            )
            result = run_intake_cycle([policy], context={}, ledger=self.ledger(directory))
            admitted = result["decisions"][0]["proposal"]
            self.assertEqual(admitted["generator_trust"], "UNTRUSTED")
            self.assertTrue(any(item.startswith("UNSUPPORTED_GENERATOR_CLAIM:")
                                for item in admitted["assumptions"]))
            self.assertEqual(admitted["admission_disposition"], "ELIGIBLE_FOR_DISCOVERY")

    def test_20_attempted_candidate_creation_is_outside_authority(self):
        with tempfile.TemporaryDirectory() as directory:
            raw = proposal()
            raw["candidate_id"] = "C-UNAUTHORIZED"
            result = self.ledger(directory).admit(raw)
            self.assertIn("OUTSIDE_AUTHORITY", result.proposal["rejection_reasons"])
            self.assertFalse(result.admission_evidence["candidate_created"])

    def test_21_attempted_downstream_authority_escalation_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            raw = proposal()
            raw["authority"] = {"live_trading_authorized": True}
            result = self.ledger(directory).admit(raw)
            self.assertIn("OUTSIDE_AUTHORITY", result.proposal["rejection_reasons"])
            self.assertEqual(result.admission_evidence["authority_state"], AUTHORITY_STATE)
            self.assertFalse(result.admission_evidence["authority_state"]["live_trading_authorized"])

    def test_22_malformed_committed_ledger_state_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "proposal_ledger.jsonl"
            append_jsonl(path, {"not": "a ledger envelope"})
            with self.assertRaises(ProposalLedgerCorruption):
                ProposalLedger(path).entries()

    def test_23_deterministic_replay_preserves_decision_and_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "proposal_ledger.jsonl"
            first = ProposalLedger(path).admit(proposal())
            reopened = ProposalLedger(path).admit(proposal())
            self.assertTrue(reopened.replayed)
            self.assertEqual(first.proposal, reopened.proposal)
            self.assertEqual(first.admission_evidence, reopened.admission_evidence)
            self.assertTrue(ProposalLedger(path).verify())

    def test_24_source_revision_does_not_mutate_historical_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = self.ledger(directory)
            first = ledger.admit(proposal())
            first_snapshot = first.proposal["source_snapshot_identity"]
            raw = proposal()
            raw["sources"] = [source(SNAP_B)]
            second = ledger.admit(raw)
            entries = ledger.entries()
            self.assertEqual(entries[0]["payload"]["proposal"]["source_snapshot_identity"], first_snapshot)
            self.assertEqual(first_snapshot, SNAP_A)
            self.assertEqual(second.proposal["source_snapshot_identity"], SNAP_B)
            self.assertIn("DUPLICATE", second.proposal["rejection_reasons"])

    def test_adversarial_paraphrase_loop_cannot_manufacture_novelty(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = self.ledger(directory)
            ledger.admit(proposal())
            for index in range(20):
                raw = proposal(
                    mechanism_claim=f"Paraphrase {index}: benchmark trackers rebalance at close.",
                    mechanism_identity="forced benchmark rebalance",
                )
                result = ledger.admit(raw)
                self.assertNotEqual(result.proposal["novelty_disposition"], "GENUINELY_NOVEL")
                self.assertEqual(result.proposal["admission_disposition"], "REJECTED")
            self.assertEqual(len(ledger.entries()), 21)

    def test_new_source_is_not_new_idea(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = self.ledger(directory)
            ledger.admit(proposal())
            raw = proposal()
            raw["sources"] = [source(SNAP_C)]
            result = ledger.admit(raw)
            self.assertEqual(result.proposal["novelty_disposition"], "SEMANTICALLY_EQUIVALENT")
            self.assertEqual(result.proposal["admission_disposition"], "REJECTED")

    def test_frontier_exhaustion_does_not_invoke_policy_or_manufacture_work(self):
        with tempfile.TemporaryDirectory() as directory:
            calls = {"count": 0}

            def generate(_context):
                calls["count"] += 1
                return [proposal()]

            policy = IdeationPolicy("coverage:v1", "SYSTEMATIC_COVERAGE", generate)
            result = run_intake_cycle(
                [policy],
                context={"frontier_state": "SCIENTIFICALLY_EXHAUSTED"},
                ledger=self.ledger(directory),
            )
            self.assertEqual(result["status"], "NOOP_FRONTIER_SCIENTIFICALLY_EXHAUSTED")
            self.assertEqual(calls["count"], 0)

    def test_policy_production_is_globally_bounded_without_symmetry(self):
        with tempfile.TemporaryDirectory() as directory:
            zero = IdeationPolicy("coverage:v1", "SYSTEMATIC_COVERAGE", lambda _context: [])
            many = IdeationPolicy(
                "divergent:v1",
                "DIVERGENT_EXPLORATION",
                lambda _context: (proposal(
                    mechanism_claim=f"idea {i}",
                    mechanism_identity=f"mechanism {i}",
                    actor_identity=f"actor {i}",
                ) for i in range(1000)),
            )
            result = run_intake_cycle(
                [zero, many],
                context={},
                ledger=self.ledger(directory),
                max_new_proposals_per_cycle=3,
            )
            self.assertEqual(result["generated_count"], 3)
            self.assertEqual(len(result["decisions"]), 3)

    def test_unresolved_or_contradictory_source_clock_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            raw = proposal()
            bad = source()
            bad["clocks"]["available_time"] = "2026-10-01T08:00:00+00:00"
            raw["sources"] = [bad]
            result = self.ledger(directory).admit(raw)
            self.assertIn("CONTRADICTORY_IDENTITY", result.proposal["rejection_reasons"])

    def test_planner_adapter_preserves_content_identity_not_path_novelty(self):
        selected = {
            "path": "research/research_os/sources/example.json",
            "packet_hash": "d" * 64,
            "record_hash": "e" * 64,
            "source_ref": "https://example.invalid/document",
            "available_at": "2026-10-01T00:00:00+00:00",
        }
        binding = source_binding_from_planner(selected, qualified=True)
        self.assertEqual(binding.source_snapshot_identity, "sha256:" + "d" * 64)
        self.assertEqual(binding.source_identity, "https://example.invalid/document")
        self.assertEqual(binding.provenance_ref, selected["path"])

    def test_self_admission_from_generator_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            raw = proposal()
            raw["admission_disposition"] = "ELIGIBLE_FOR_DISCOVERY"
            result = self.ledger(directory).admit(raw)
            self.assertIn("OUTSIDE_AUTHORITY", result.proposal["rejection_reasons"])

    def test_handoff_is_narrow_and_stops_at_discovery_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.ledger(directory).admit(proposal())
            handoff = discovery_handoff(result)
            self.assertEqual(handoff["terminal_state"], "ELIGIBLE_FOR_DISCOVERY")
            self.assertFalse(handoff["candidate_created"])
            self.assertNotIn("candidate_id", handoff)
            self.assertNotIn("experiment_spec", handoff)
            self.assertNotIn("expected_return", handoff)

    def test_torn_tail_is_not_silently_repaired_by_proposal_ledger(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "proposal_ledger.jsonl"
            ProposalLedger(path).admit(proposal())
            with path.open("ab") as handle:
                handle.write(b'{"torn":')
            with self.assertRaises(ProposalLedgerCorruption):
                ProposalLedger(path).entries()

    def test_scientific_memory_unresolved_relation_cannot_be_called_novel(self):
        with tempfile.TemporaryDirectory() as directory:
            unresolved = {
                "qualified": True,
                "same_semantic_family": False,
                "memory_id": "smem:ambiguous",
                "mismatched_core_dimensions": [],
                "unknown_core_dimensions": ["payer", "economic_exposure"],
            }
            with patch("research.research_os.ideation_intake.memory_relation", return_value=unresolved):
                result = self.ledger(directory, scientific_memory=[{"memory_id": "smem:ambiguous"}]).admit(proposal())
            self.assertEqual(result.proposal["novelty_disposition"], "UNKNOWN")
            self.assertEqual(result.proposal["admission_disposition"], "REJECTED")
            self.assertIn("INSUFFICIENT_INFORMATION", result.proposal["rejection_reasons"])

    def test_malformed_assumptions_do_not_become_valid_by_sanitization(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.ledger(directory).admit(proposal(assumptions="not-a-list"))
            self.assertEqual(result.proposal["admission_disposition"], "REJECTED")
            self.assertIn("MALFORMED", result.proposal["rejection_reasons"])

    def test_planner_adapter_requires_explicit_qualification_assertion(self):
        selected = {
            "path": "research/research_os/sources/example.json",
            "packet_hash": "d" * 64,
        }
        with self.assertRaises(TypeError):
            source_binding_from_planner(selected)


if __name__ == "__main__":
    unittest.main()

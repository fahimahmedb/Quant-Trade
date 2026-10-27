from copy import deepcopy
import unittest

import research.research_os.ideation_intake as intake
from research.research_os.ideation_intake import (
    AUTHORITY_STATE, AdmissionError, admit_proposal, bind_candidate_continuity,
    bind_ri_decision, discovery_handoff, research_intelligence_input,
)
from research.research_os.multi_source_ideation_hardening import DurableProposalLedger


class VerifiedContinuityAdmissionIdentityTests(unittest.TestCase):
    def raw(self, *, cohort="cohort-a", parameters=None, source_hash="1" * 64):
        return {
            "policy_id": "fixed-pre-discovery-v1",
            "cohort_id": cohort,
            "mechanism_claim": "dealer balance-sheet constraint around auction settlement",
            "mechanism_identity": "dealer balance-sheet constraint",
            "actor_identity": "primary dealers",
            "universe_identity": "UST primary dealer auction instruments",
            "clock_identity": {"name": "auction-settlement-clock"},
            "horizon_identity": "auction to settlement",
            "payer_identity": "UNKNOWN",
            "economic_exposure": "UNKNOWN",
            "instrument_identity": "UST",
            "source_family": "public documentary source",
            "evidence_identity": source_hash,
            "parameters": parameters or {"window": "fixed"},
            "falsifiable_claim": {
                "statement": "constraint state is observable before the declared horizon",
                "falsifier": "required documentary state is absent at the frozen cutoff",
            },
            "sources": [{
                "source_identity": "qualified-source-1",
                "source_snapshot_identity": source_hash,
                "provenance_ref": "research/research_os/sources/qualified-source-1.json",
                "qualified": True,
                "clocks": {
                    "public_time": "2026-10-01T10:00:00Z",
                    "available_time": "2026-10-01T10:05:00Z",
                    "capture_time": "2026-10-01T10:10:00Z",
                },
            }],
        }

    def test_existing_durable_proposal_ledger_is_the_only_admission_store(self):
        self.assertFalse(hasattr(intake, "ProposalLedger"))
        ledger = DurableProposalLedger()
        row = admit_proposal(self.raw(), ledger=ledger)
        self.assertEqual(ledger.snapshot(), [row])
        self.assertEqual(row["status"], "ELIGIBLE_FOR_DISCOVERY")
        self.assertEqual(row["authority"], AUTHORITY_STATE)
        self.assertFalse(row["outcome_accessed"])
        self.assertFalse(row["candidate_created"])
        self.assertEqual(admit_proposal(self.raw(), ledger=ledger), row)
        self.assertEqual(len(ledger.snapshot()), 1)

    def test_cohort_rename_cannot_reset_root_variant_or_exposure(self):
        ledger = DurableProposalLedger()
        first = admit_proposal(self.raw(cohort="cohort-a"), ledger=ledger)
        renamed = admit_proposal(self.raw(cohort="cohort-b"), ledger=ledger)
        self.assertEqual(first["root_hypothesis_id"], renamed["root_hypothesis_id"])
        self.assertEqual(first["variant_id"], renamed["variant_id"])
        self.assertEqual(first["cumulative_exposure_ids"], renamed["cumulative_exposure_ids"])
        self.assertEqual(renamed["status"], "DUPLICATE_OR_KNOWN")
        self.assertEqual(renamed["admission_disposition"], "REJECTED")
        self.assertIn("PRIOR_SCIENTIFIC_EXPOSURE_SAME_VARIANT", renamed["rejection_reasons"])

    def test_parameter_variant_keeps_root_and_charges_prior_exposure(self):
        ledger = DurableProposalLedger()
        first = admit_proposal(self.raw(parameters={"window": "fixed"}), ledger=ledger)
        variant = admit_proposal(self.raw(cohort="cohort-b", parameters={"window": "alternate"}), ledger=ledger)
        self.assertEqual(first["root_hypothesis_id"], variant["root_hypothesis_id"])
        self.assertNotEqual(first["variant_id"], variant["variant_id"])
        self.assertEqual(variant["novelty_disposition"], "PARAMETER_VARIANT")
        self.assertEqual(variant["admission_disposition"], "ELIGIBLE_FOR_DISCOVERY")
        self.assertTrue(set(first["cumulative_exposure_ids"]).issubset(variant["cumulative_exposure_ids"]))

    def test_unknown_root_dimension_stays_unknown_and_cannot_handoff(self):
        ledger = DurableProposalLedger()
        raw = self.raw()
        raw["actor_identity"] = "UNKNOWN"
        row = admit_proposal(raw, ledger=ledger)
        self.assertEqual(row["root_hypothesis_id"], "UNKNOWN")
        self.assertEqual(row["admission_disposition"], "REJECTED")
        with self.assertRaisesRegex(AdmissionError, "ONLY_ELIGIBLE"):
            discovery_handoff(row)

    def test_upstream_candidate_authority_and_outcome_fields_are_forbidden(self):
        cases = [
            ("candidate_id", "C-1"),
            ("experiment_id", "E-1"),
            ("economic_experiment_authorized", True),
            ("outcome_accessed", True),
            ("pnl", 1.0),
        ]
        for key, value in cases:
            raw = self.raw()
            raw[key] = value
            with self.subTest(key=key), self.assertRaises(AdmissionError):
                admit_proposal(raw, ledger=DurableProposalLedger())

    def test_cross_owner_linkage_is_sidecar_only_and_does_not_mutate_candidate(self):
        ledger = DurableProposalLedger()
        row = admit_proposal(self.raw(), ledger=ledger)
        handoff = discovery_handoff(row)
        self.assertFalse(handoff["candidate_created"])
        ri_input = research_intelligence_input(row, required_capability="institutional_flows", target_lane="market_discovery")
        self.assertNotIn("root_hypothesis_id", ri_input["identity"])
        decision = {"candidate_id": row["proposal_subject_id"], "action": "RUN_PRODUCER", "executable": True,
                    "scheduler_mutation": False}
        bound = bind_ri_decision(row, decision)
        candidate = {"hypothesis_id": "H-UST", "generation_id": "G-001", "claim": "fixture-only continuity binding"}
        before = deepcopy(candidate)
        sidecar = bind_candidate_continuity(bound, candidate)
        self.assertEqual(candidate, before)
        self.assertEqual(sidecar["root_hypothesis_id"], row["root_hypothesis_id"])
        self.assertEqual(sidecar["proposal_id"], row["proposal_id"])
        self.assertEqual(sidecar["variant_id"], row["variant_id"])
        self.assertFalse(sidecar["outcome_accessed"])
        self.assertEqual(sidecar["authority"], AUTHORITY_STATE)


if __name__ == "__main__":
    unittest.main()

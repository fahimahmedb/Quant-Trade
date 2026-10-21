from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import side_effect_zeroes
from research.research_os.multi_source_ideation_hardening import DurableProposalLedger, qualify_for_discovery


class DurableProposalLedgerTruthOperationalFirewallTests(unittest.TestCase):
    def base_row(self) -> dict:
        return {
            "proposal_id": "proposal-1",
            "status": "ELIGIBLE_FOR_DISCOVERY",
            "outcome_accessed": False,
            "economic_result": "NOT_OBSERVED",
            "scientific_verdict": "NOT_PERFORMED",
            "metadata": {"source": "bounded"},
        }

    def assert_rejected(self, patch: dict) -> None:
        ledger = DurableProposalLedger()
        row = self.base_row()
        row.update(patch)
        with self.assertRaises(ValueError):
            ledger.persist(row)

    def test_allowed_non_observation_sentinels_persist_unchanged(self):
        ledger = DurableProposalLedger()
        row = self.base_row()
        self.assertEqual(ledger.persist(row), "proposal-1")
        self.assertEqual(ledger.snapshot(), [row])
        self.assertEqual(ledger.persist(dict(row)), "proposal-1")
        self.assertEqual(ledger.snapshot(), [row])

    def test_identity_collision_is_immutable(self):
        ledger = DurableProposalLedger()
        ledger.persist(self.base_row())
        changed = self.base_row()
        changed["metadata"] = {"source": "changed"}
        with self.assertRaises(ValueError):
            ledger.persist(changed)

    def test_outcome_keys_are_rejected_recursively_and_case_insensitively(self):
        for key, value in (
            ("pnl", 1), ("PnL", 1), ("returns", [0.1]), ("sharpe", 2.0),
            ("price", 100), ("fills", [{"qty": 1}]), ("economic_result", "POSITIVE"),
            ("scientific_verdict", "VALIDATED"),
        ):
            with self.subTest(key=key):
                self.assert_rejected({"nested": {key: value}})

    def test_outcome_access_must_remain_false(self):
        self.assert_rejected({"outcome_accessed": True})
        self.assert_rejected({"nested": {"outcome_accessed": True}})

    def test_operational_identifiers_and_capabilities_are_rejected_recursively(self):
        forbidden = (
            "lease", "lease_id", "lease_owner", "heartbeat", "worker_owner", "retry_at",
            "commit_token", "scheduler_state", "oracle_state", "task_id", "ready_task",
            "candidate_id", "producer_id", "experiment_id", "scheduler", "oracle",
            "control_plane", "queue", "worker", "runtime_activation", "control_plane_mutation",
            "scheduler_mutation", "scientific_memory_mutation", "producer_executed",
        )
        for key in forbidden:
            with self.subTest(key=key):
                self.assert_rejected({"nested": {key: "forbidden"}})

    def test_only_passive_statuses_are_accepted(self):
        for status in ("READY", "LEASED", "RUNNING", "RETRY", "EXECUTED", "FINAL", "COMPLETE"):
            with self.subTest(status=status):
                self.assert_rejected({"status": status})

    def test_proposal_id_and_explicit_outcome_false_are_required(self):
        row = self.base_row()
        row.pop("proposal_id")
        with self.assertRaises(ValueError):
            DurableProposalLedger().persist(row)
        row = self.base_row()
        row.pop("outcome_accessed")
        with self.assertRaises(ValueError):
            DurableProposalLedger().persist(row)

    def test_discovery_qualification_remains_passive(self):
        proposal = {
            "artifact_kind": "IDEA_PROPOSAL",
            "context_snapshot_hash": "ctx",
            "payload": {"mechanism": "bounded"},
        }
        decision = qualify_for_discovery(
            proposal=proposal,
            context_snapshot_hash="ctx",
            memory={"classification": "NO_QUALIFIED_MATCH"},
            duplicate={"classification": "DISTINCT"},
            implementability={"admissible": True},
        )
        self.assertTrue(decision["eligible_for_discovery"])
        self.assertFalse(decision["ready_task_created"])
        self.assertFalse(decision["candidate_created"])
        self.assertTrue(all(value == 0 for value in side_effect_zeroes().values()))


if __name__ == "__main__":
    unittest.main()

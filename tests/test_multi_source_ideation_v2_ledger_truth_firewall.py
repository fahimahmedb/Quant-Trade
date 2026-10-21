from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation_hardening import DurableProposalLedger


class ProposalLedgerTruthFirewallTests(unittest.TestCase):
    def test_passive_sentinels_are_allowed(self):
        ledger = DurableProposalLedger()
        row = {
            "proposal_id": "p",
            "status": "ELIGIBLE_FOR_DISCOVERY",
            "outcome_accessed": False,
            "scientific_verdict": "NOT_PERFORMED",
            "economic_result": "NOT_OBSERVED",
        }
        self.assertEqual(ledger.persist(row), "p")
        self.assertEqual(ledger.snapshot(), [row])

    def test_observed_truth_is_rejected_recursively(self):
        forbidden = (
            {"nested": {"pnl": 1.0}},
            {"nested": {"outcome_accessed": True}},
            {"nested": {"scientific_verdict": "PASS"}},
            {"nested": {"economic_result": "PROFITABLE"}},
        )
        for index, payload in enumerate(forbidden):
            with self.subTest(index=index):
                with self.assertRaises(ValueError):
                    DurableProposalLedger().persist({"proposal_id": f"p-{index}", **payload})


if __name__ == "__main__":
    unittest.main()

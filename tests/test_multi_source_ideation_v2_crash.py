from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation_hardening import DurableProposalLedger


class ProposalLedgerCrashTests(unittest.TestCase):
    def test_rehydrate_multiple_rows_preserves_exact_records(self):
        rows=[
            {"proposal_id":"a","status":"ELIGIBLE_FOR_DISCOVERY","context_snapshot_hash":"h1"},
            {"proposal_id":"b","status":"REVIEW_REQUIRED","context_snapshot_hash":"h2"},
        ]
        first=DurableProposalLedger()
        for row in rows: first.persist(row)
        restored=DurableProposalLedger(first.snapshot())
        self.assertEqual(restored.snapshot(),first.snapshot())


if __name__ == "__main__": unittest.main()

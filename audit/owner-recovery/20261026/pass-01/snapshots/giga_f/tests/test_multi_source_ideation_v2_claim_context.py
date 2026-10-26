from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation_hardening import SourceClaimLedger


class ClaimContextIsolationTests(unittest.TestCase):
    def test_same_source_can_be_independently_claimed_in_new_frozen_context(self):
        ledger=SourceClaimLedger()
        a=ledger.claim(source_identity="packet:x",context_snapshot_hash="h1",policy_kind="SYSTEMATIC_COVERAGE")
        b=ledger.claim(source_identity="packet:x",context_snapshot_hash="h2",policy_kind="DIVERGENT_EXPLORATION")
        self.assertNotEqual(a["claim_id"],b["claim_id"]); self.assertEqual(len(ledger.snapshot()),2)


if __name__ == "__main__": unittest.main()

from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation_hardening import SourceClaimLedger


class ClaimNoConsumptionTests(unittest.TestCase):
    def test_claim_lifecycle_never_marks_source_scientifically_consumed(self):
        for terminal in ("RELEASED","TRANSFERRED"):
            ledger=SourceClaimLedger(); c=ledger.claim(source_identity="s",context_snapshot_hash="h",policy_kind="SYSTEMATIC_COVERAGE")
            self.assertFalse(c["scientifically_consumed"])
            self.assertFalse(ledger.transition(c["claim_id"],terminal)["scientifically_consumed"])


if __name__ == "__main__": unittest.main()

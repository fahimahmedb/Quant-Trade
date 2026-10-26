from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation_hardening import SourceClaimLedger


class ClaimTerminalTests(unittest.TestCase):
    def test_terminal_claim_cannot_change_terminal_kind(self):
        ledger=SourceClaimLedger(); c=ledger.claim(source_identity="s",context_snapshot_hash="h",policy_kind="SYSTEMATIC_COVERAGE")
        ledger.transition(c["claim_id"],"RELEASED")
        with self.assertRaises(ValueError): ledger.transition(c["claim_id"],"TRANSFERRED")

    def test_same_terminal_transition_is_idempotent(self):
        ledger=SourceClaimLedger(); c=ledger.claim(source_identity="s",context_snapshot_hash="h",policy_kind="SYSTEMATIC_COVERAGE")
        a=ledger.transition(c["claim_id"],"TRANSFERRED"); b=ledger.transition(c["claim_id"],"TRANSFERRED")
        self.assertEqual(a,b)


if __name__ == "__main__": unittest.main()

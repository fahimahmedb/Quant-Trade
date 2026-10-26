from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation_hardening import SourceClaimLedger


class SourceClaimIdentityTests(unittest.TestCase):
    def test_policy_is_bound_into_claim_id(self):
        a=SourceClaimLedger().claim(source_identity="s",context_snapshot_hash="h",policy_kind="SYSTEMATIC_COVERAGE")
        b=SourceClaimLedger().claim(source_identity="s",context_snapshot_hash="h",policy_kind="DIVERGENT_EXPLORATION")
        self.assertNotEqual(a["claim_id"],b["claim_id"])


if __name__ == "__main__": unittest.main()

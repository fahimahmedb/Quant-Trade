from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation_hardening import SourceClaimLedger

class ClaimNoExpiryTests(unittest.TestCase):
    def test_passive_claim_has_no_lease_expiry_or_heartbeat(self):
        c=SourceClaimLedger().claim(source_identity="s",context_snapshot_hash="h",policy_kind="SYSTEMATIC_COVERAGE")
        for forbidden in ("expires_at","lease_expiry","heartbeat","retry_at","worker_owner"): self.assertNotIn(forbidden,c)

if __name__ == "__main__": unittest.main()

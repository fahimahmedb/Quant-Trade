from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation_hardening import qualify_for_discovery

class SeedNoProposalChecksTests(unittest.TestCase):
    def test_seed_routes_to_synthesis_before_proposal_level_checks(self):
        got=qualify_for_discovery(proposal={"artifact_kind":"IDEATION_SEED","context_snapshot_hash":"h"},context_snapshot_hash="h",memory={"classification":"KNOWN_EXACT_NEGATIVE"},duplicate={"classification":"EXACT_DUPLICATE"},implementability={"admissible":False})
        self.assertEqual(got["decision"],"NEEDS_DISCOVERY_SYNTHESIS"); self.assertTrue(got["eligible_for_discovery"])

if __name__ == "__main__": unittest.main()

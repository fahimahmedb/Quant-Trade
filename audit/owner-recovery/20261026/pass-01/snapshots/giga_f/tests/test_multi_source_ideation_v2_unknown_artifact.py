from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation_hardening import qualify_for_discovery

class UnknownArtifactTests(unittest.TestCase):
    def test_unknown_artifact_kind_is_not_discovery_eligible(self):
        got=qualify_for_discovery(proposal={"artifact_kind":"CANDIDATE","context_snapshot_hash":"h"},context_snapshot_hash="h",memory={},duplicate={},implementability={})
        self.assertEqual(got["decision"],"NEEDS_DISCOVERY_SYNTHESIS"); self.assertFalse(got["eligible_for_discovery"])

if __name__ == "__main__": unittest.main()

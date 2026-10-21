from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import raw_artifact


class ArtifactContractTests(unittest.TestCase):
    def test_proposal_and_seed_terminal_kind_pairing_is_strict(self):
        with self.assertRaises(ValueError): raw_artifact(policy_kind="DIVERGENT_EXPLORATION",status="PROPOSAL_EMITTED",context_snapshot_hash="h",artifact_kind="IDEATION_SEED")
        with self.assertRaises(ValueError): raw_artifact(policy_kind="DIVERGENT_EXPLORATION",status="SEED_EMITTED",context_snapshot_hash="h",artifact_kind="IDEA_PROPOSAL")


if __name__ == "__main__": unittest.main()

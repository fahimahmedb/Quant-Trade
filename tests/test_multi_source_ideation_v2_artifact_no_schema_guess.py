from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation import raw_artifact

class ArtifactNoSchemaGuessTests(unittest.TestCase):
    def test_raw_artifact_contains_only_bounded_contract_fields(self):
        a=raw_artifact(policy_kind="SYSTEMATIC_COVERAGE",status="NO_PROPOSAL",context_snapshot_hash="h")
        self.assertEqual(set(a),{"policy_kind","status","context_snapshot_hash","artifact_kind","payload","reason"})

if __name__ == "__main__": unittest.main()

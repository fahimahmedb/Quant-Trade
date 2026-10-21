from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation import raw_artifact

class RawArtifactCopyTests(unittest.TestCase):
    def test_payload_is_defensively_copied(self):
        payload={"nested":{"x":1}}
        a=raw_artifact(policy_kind="SYSTEMATIC_COVERAGE",status="SEED_EMITTED",context_snapshot_hash="h",artifact_kind="IDEATION_SEED",payload=payload)
        payload["nested"]["x"]=2
        self.assertEqual(a["payload"]["nested"]["x"],1)

if __name__ == "__main__": unittest.main()

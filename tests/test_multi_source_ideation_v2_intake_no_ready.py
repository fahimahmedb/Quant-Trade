from __future__ import annotations
import unittest
from research.research_os.multi_source_ideation import intake

class IntakeNoReadyTests(unittest.TestCase):
    def test_core_intake_never_returns_ready(self):
        p={"artifact_kind":"IDEA_PROPOSAL","context_snapshot_hash":"h"}; got=intake(artifact=p,memory_check={"classification":"NO_QUALIFIED_MATCH"},duplicate={"classification":"DISTINCT"},implementability={"admissible":True},current_context_hash="h")
        self.assertEqual(got["decision"],"ELIGIBLE_FOR_DISCOVERY"); self.assertNotEqual(got["decision"],"READY")

if __name__ == "__main__": unittest.main()

from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import intake


class IntakeNegativeTests(unittest.TestCase):
    def test_known_exact_negative_suppresses_proposal(self):
        p={"artifact_kind":"IDEA_PROPOSAL","context_snapshot_hash":"h"}
        got=intake(artifact=p,memory_check={"classification":"KNOWN_EXACT_NEGATIVE"},duplicate={"classification":"DISTINCT"},implementability={"admissible":True},current_context_hash="h")
        self.assertEqual(got["decision"],"NOT_ELIGIBLE"); self.assertFalse(got["eligible_for_discovery"])

    def test_exact_duplicate_suppresses_proposal(self):
        p={"artifact_kind":"IDEA_PROPOSAL","context_snapshot_hash":"h"}
        got=intake(artifact=p,memory_check={"classification":"NO_QUALIFIED_MATCH"},duplicate={"classification":"EXACT_DUPLICATE"},implementability={"admissible":True},current_context_hash="h")
        self.assertEqual(got["decision"],"NOT_ELIGIBLE")


if __name__ == "__main__": unittest.main()

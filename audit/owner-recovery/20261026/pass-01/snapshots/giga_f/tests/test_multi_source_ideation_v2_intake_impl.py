from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation_hardening import qualify_for_discovery


class IntakeImplementabilityTests(unittest.TestCase):
    def test_nonimplementable_proposal_is_not_eligible(self):
        got=qualify_for_discovery(proposal={"artifact_kind":"IDEA_PROPOSAL","context_snapshot_hash":"h"},context_snapshot_hash="h",memory={"classification":"NO_QUALIFIED_MATCH"},duplicate={"classification":"DISTINCT"},implementability={"admissible":False})
        self.assertEqual(got["decision"],"NOT_ELIGIBLE"); self.assertFalse(got["eligible_for_discovery"])


if __name__ == "__main__": unittest.main()

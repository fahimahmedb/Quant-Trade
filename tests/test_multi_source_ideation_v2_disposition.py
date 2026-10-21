from __future__ import annotations

import unittest

from research.research_os.ideation_cycle import proposal_disposition


class ProposalDispositionTests(unittest.TestCase):
    def test_disposition_preserves_review_required(self):
        got=proposal_disposition(proposal_id="p",intake_decision={"decision":"REVIEW_REQUIRED","eligible_for_discovery":False},lineage={"classification":"UNKNOWN"},duplicate={"classification":"UNKNOWN"},implementability={"admissible":True})
        self.assertEqual(got["decision"],"REVIEW_REQUIRED"); self.assertFalse(got["operational_admission"])
        self.assertFalse(got["outcome_accessed"])

    def test_unknown_disposition_cannot_be_silently_persisted(self):
        with self.assertRaises(ValueError): proposal_disposition(proposal_id="p",intake_decision={"decision":"READY","eligible_for_discovery":True},lineage={},duplicate={},implementability={})


if __name__ == "__main__": unittest.main()

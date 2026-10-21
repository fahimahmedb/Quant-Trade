from __future__ import annotations

import unittest

from research.research_os.ideation_cycle import proposal_disposition


class DispositionOutcomeFirewallTests(unittest.TestCase):
    def test_eligible_disposition_has_no_scientific_or_economic_result(self):
        d=proposal_disposition(proposal_id="p",intake_decision={"decision":"ELIGIBLE_FOR_DISCOVERY","eligible_for_discovery":True},lineage={},duplicate={},implementability={"admissible":True})
        self.assertEqual(d["scientific_verdict"],"NOT_PERFORMED"); self.assertEqual(d["economic_result"],"NOT_OBSERVED"); self.assertFalse(d["outcome_accessed"])


if __name__ == "__main__": unittest.main()

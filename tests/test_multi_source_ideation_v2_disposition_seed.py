from __future__ import annotations
import unittest
from research.research_os.ideation_cycle import proposal_disposition

class DispositionSeedTests(unittest.TestCase):
    def test_seed_synthesis_disposition_is_not_operational_admission(self):
        d=proposal_disposition(proposal_id="seed",intake_decision={"decision":"NEEDS_DISCOVERY_SYNTHESIS","eligible_for_discovery":True},lineage={},duplicate={},implementability={})
        self.assertTrue(d["eligible_for_discovery"]); self.assertFalse(d["operational_admission"]); self.assertEqual(d["scientific_verdict"],"NOT_PERFORMED")

if __name__ == "__main__": unittest.main()

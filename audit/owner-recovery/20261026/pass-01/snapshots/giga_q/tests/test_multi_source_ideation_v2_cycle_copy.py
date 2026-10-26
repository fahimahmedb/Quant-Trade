from __future__ import annotations
import unittest
from research.research_os.ideation_cycle import proposal_disposition

class DispositionCopyTests(unittest.TestCase):
    def test_disposition_defensively_copies_evidence(self):
        lineage={"classification":"NO_QUALIFIED_MATCH","nested":{"x":1}}
        d=proposal_disposition(proposal_id="p",intake_decision={"decision":"ELIGIBLE_FOR_DISCOVERY","eligible_for_discovery":True},lineage=lineage,duplicate={"classification":"DISTINCT"},implementability={"admissible":True})
        lineage["nested"]["x"]=2; self.assertEqual(d["memory_lineage"]["nested"]["x"],1)

if __name__ == "__main__": unittest.main()

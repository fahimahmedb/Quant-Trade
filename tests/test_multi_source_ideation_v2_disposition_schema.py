from __future__ import annotations
import unittest
from research.research_os.ideation_cycle import proposal_disposition

class DispositionSchemaTests(unittest.TestCase):
    def test_disposition_schema_version_is_explicit(self):
        d=proposal_disposition(proposal_id="p",intake_decision={"decision":"NOT_ELIGIBLE","eligible_for_discovery":False},lineage={},duplicate={},implementability={})
        self.assertEqual(d["schema_version"],"ideation-disposition-v2")

if __name__ == "__main__": unittest.main()

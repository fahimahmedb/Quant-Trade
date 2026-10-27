"""Isolated replay of latest-C0 semantic-confirmation invariant on target adapter."""
import json,unittest
from research.research_os.expansion.scientific_adjudication import (
 bind_independence_ref, validate_independence_ref,
)
from tests.test_wave2_c2_scientific_adjudication import Wave2C2ScientificAdjudicationTests,independence_record
class CurrentSemanticConfirmationAttack(unittest.TestCase):
 def test_unproven_semantic_review_cannot_count_as_independent_confirmation(self):
  case=Wave2C2ScientificAdjudicationTests();case.setUp()
  record=independence_record();ref=bind_independence_ref(case.factory,record)
  validate_independence_ref(ref,case.factory)
  result=case.adjudicate(independence_ref=ref)
  print(json.dumps({'record':record,'ref':ref,'adjudication':result},indent=2))
  self.assertTrue(ref['structural_independence_proven'])
  self.assertEqual(ref['status'],'PASS')
  self.assertEqual(ref['semantic_diverse_review'],'NOT_PROVEN_NO_SEMANTIC_PASS_GRANTED')
  self.assertEqual(ref['independent_confirmation_count'],0,
   'CURRENT_INVARIANT: structural reconstruction with explicitly unproven semantic review inflated independent confirmation count')
if __name__=='__main__':unittest.main()

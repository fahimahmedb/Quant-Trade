"""Direct C0 refs cannot launder synthetic outcome fields through valid selfhashes."""
from copy import deepcopy
import unittest
from research.research_os.expansion import scientific_adjudication as c0
from research.research_os.scientific_store import sha256_json
from tests import test_wave2_c2_scientific_adjudication as fixtures

class DirectRefMembraneTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.Wave2C2ScientificAdjudicationTests()
        self.f.setUp()

    def forged(self, value, key='return_series', sequence=list, hash_key='ref_hash'):
        ref = deepcopy(value)
        ref['audit'] = {'nested': sequence([{key: ['SYNTHETIC_NO_REAL_OUTCOMES']}])}
        ref[hash_key] = sha256_json({k:v for k,v in ref.items() if k != hash_key})
        return ref

    def test_all_direct_reference_validators_reject_all_existing_forbidden_aliases(self):
        f = self.f
        cases = [(f.factory, lambda r:c0.validate_factory_ref(r)),
                 (f.cross, lambda r:c0.validate_cross_examination_ref(r,f.factory)),
                 (f.validator, lambda r:c0.validate_validator_ref(r,f.factory)),
                 (f.red_team, lambda r:c0.validate_red_team_ref(r,f.factory,f.validator)),
                 (c0.bind_independence_ref(f.factory,fixtures.independence_record()),lambda r:c0.validate_independence_ref(r,f.factory))]
        for original, validate in cases:
            for key in c0._impl._FORBIDDEN_OUTCOME_KEYS:
                for sequence in (list,tuple):
                    ref=self.forged(original,' '+key.upper()+' ',sequence)
                    before=deepcopy(ref)
                    with self.subTest(key=key,sequence=sequence), self.assertRaisesRegex(c0.ScientificAdjudicationError,'outcome-bearing'):
                        validate(ref)
                    self.assertEqual(ref,before)

    def test_public_and_inner_composition_reject_injected_independence_ref(self):
        f=self.f
        ref=self.forged(c0.bind_independence_ref(f.factory,fixtures.independence_record()))
        for compose in (c0.adjudicate_scientific_candidate,c0._impl.adjudicate_scientific_candidate):
            with self.subTest(compose=compose),self.assertRaisesRegex(c0.ScientificAdjudicationError,'outcome-bearing'):
                compose(f.factory,cross_examination_ref=f.cross,validator_ref=f.validator,red_team_ref=f.red_team,independence_ref=ref)

    def test_negative_ref_and_final_result_membranes(self):
        f=self.f
        negative=c0.bind_qualified_negative_ref(f.factory,fixtures.negative_record(f.factory))
        with self.assertRaisesRegex(c0.ScientificAdjudicationError,'outcome-bearing'):
            c0.validate_qualified_negative_ref(self.forged(negative),f.factory)
        result=f.adjudicate()
        with self.assertRaisesRegex(c0.ScientificAdjudicationError,'outcome-bearing'):
            c0.validate_adjudication(self.forged(result,hash_key='adjudication_hash'))

    def test_clean_refs_keep_identity_unknowns_and_zero_semantic_count(self):
        f=self.f
        ref=c0.bind_independence_ref(f.factory,fixtures.independence_record())
        before=deepcopy(ref)
        result=f.adjudicate(independence_ref=ref)
        self.assertEqual(ref,before)
        self.assertEqual(result['independent_confirmation_count'],0)
        self.assertEqual(result['profitability_status'],'UNKNOWN')
        self.assertFalse(result['economic_identity_created'])
        self.assertEqual(result['raw_outcomes_consumed'],0)

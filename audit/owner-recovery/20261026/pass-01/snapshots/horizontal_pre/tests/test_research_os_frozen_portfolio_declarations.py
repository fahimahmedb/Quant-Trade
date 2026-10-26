"""An existing freeze feeds structural declarations without qualifying facts."""
from copy import deepcopy
import unittest

from research.research_os.expansion.final_shape import (
    assess_implementability, economic_identity_v1, freeze_experiment_envelope,
)
from research.research_os.expansion.economic_test_readiness_v1 import AUTHORITY, READY, economic_test_readiness
from research.research_os.expansion.portfolio_v2 import portfolio_diagnostics_v2, structural_identity
from research.research_os.scientific_store import sha256_json
from research.research_os.tests.test_economic_readiness_integration import fixture, legacy
from research.research_os.tests.test_economic_identity_portfolio_readiness import identity as peer_identity
from tests.test_research_os_documentary_portfolio_scope import SOURCES, identity as documentary_identity


def declared_identity(package=None):
    p = deepcopy(package or fixture())
    output = p['engine_output']
    protocol = p['runner_meta']['frozen_protocol']
    implementation = assess_implementability(output, p['implementability_meta'])
    envelope = freeze_experiment_envelope(output, implementation, {
        'dataset_provenance': {'protocol': protocol, 'sources': p['sources']},
        'implementability_declaration': implementation,
    })
    return economic_identity_v1(output, p.get('identity_meta', {}), frozen_envelope=envelope), envelope


class FrozenPortfolioDeclarationTests(unittest.TestCase):
    def test_actual_readiness_preserves_exact_frozen_expression_and_candidate_provenance(self):
        p = fixture()
        before = deepcopy(p)
        result = economic_test_readiness(p, legacy=legacy())
        self.assertEqual(result['status'], READY, result['block_reasons'])
        expression = p['runner_meta']['frozen_protocol']['economic_expression']
        fields = result['identity']['fields']
        for name, key in (('instrument', 'instrument'), ('universe', 'universe'),
                          ('timing_clock', 'entry_clock'), ('horizon', 'horizon')):
            self.assertEqual(fields[name]['value'], expression[key])
            self.assertEqual(fields[name]['status'], 'DECLARED')
            evidence = fields[name]['declaration_evidence']
            self.assertEqual(evidence['status'], 'DECLARED_ONLY')
            self.assertEqual(evidence['candidate_hash'], sha256_json(p['engine_output']['candidate']))
            self.assertEqual(evidence['protocol_hash'], result['experiment_plan']['plan']['protocol_hash'])
            self.assertFalse(evidence['source_factual_qualification'])
        self.assertNotEqual(fields['horizon']['value'], p['engine_output']['candidate']['horizon'])
        self.assertEqual(result['authority'], AUTHORITY)
        self.assertFalse(result['outcome_accessed'])
        self.assertEqual(p, before)

    def test_portfolio_consumes_declared_clock_for_same_exposure_review(self):
        p = fixture()
        p['identity_meta'] = {'payer': 'fixture-payer'}
        peer = peer_identity('PEER', payer='fixture-payer',
            mechanism=p['engine_output']['candidate']['mechanism'],
            timing_clock=p['runner_meta']['frozen_protocol']['economic_expression']['entry_clock'])
        before = deepcopy([p, peer])
        result = economic_test_readiness(p, legacy=legacy(), peer_identities=[peer])
        self.assertEqual(result['status'], 'BLOCK')
        pair = result['portfolio']['pairwise'][0]['economic_structure']
        self.assertEqual(pair['classification'], 'HIGH_STRUCTURAL_OVERLAP_REVIEW')
        self.assertEqual(pair['dimensions']['timing_clock'], 1.0)
        self.assertEqual(result['portfolio']['readiness_blocking_review_pairs'][0]['basis'], 'EXPLICIT_REVIEW')
        self.assertEqual(result['portfolio']['empirical_correlation'], 'UNAVAILABLE')
        self.assertEqual(result['portfolio']['marginal_portfolio_contribution'], 'NOT_ESTIMATED')
        self.assertEqual([p, peer], before)

    def test_documentary_facts_and_declared_structure_keep_distinct_ceilings(self):
        for key in SOURCES:
            with self.subTest(engine=key):
                original = documentary_identity(key)
                p = fixture()
                p['engine_output'] = deepcopy(original['documentary_basis'])
                p['runner_meta']['frozen_protocol']['decision_map'] = p['engine_output']['candidate']['decision_map']
                declared, envelope = declared_identity(p)
                projected = structural_identity(declared)
                self.assertEqual(declared['asset'], original['asset'])
                self.assertEqual(declared['horizon'], 'UNKNOWN')
                self.assertEqual(declared['identity_provenance'], original['identity_provenance'])
                field = projected['fields']['instrument']
                self.assertEqual(field['status'], 'DECLARED')
                self.assertEqual(field['documentary_evidence']['status'],
                                 original['identity_provenance']['field_support']['asset']['status'])
                self.assertFalse(field['declaration_evidence']['source_factual_qualification'])
                self.assertEqual(field['provenance']['protocol_hash'], envelope['protocol_hash'])
                self.assertEqual(projected['fields']['economic_exposure']['status'], 'UNKNOWN')
                tampered = deepcopy(declared)
                tampered['asset'] = 'OTHER'
                with self.assertRaises(ValueError):
                    structural_identity(tampered)

    def test_foreign_stale_or_partially_rebound_declarations_fail_closed(self):
        p = fixture()
        value, envelope = declared_identity(p)
        for mutation in ('hash', 'foreign_candidate', 'expression', 'implementation', 'opened'):
            wrong = deepcopy(envelope)
            payload = wrong['protocol_payload']
            if mutation == 'hash':
                wrong['protocol_hash'] = 'a' * 64
            elif mutation == 'foreign_candidate':
                payload['candidate']['claim'] = 'foreign same-generation claim'
            elif mutation == 'expression':
                payload['dataset_provenance']['protocol']['economic_expression']['instrument'] = 'OTHER'
            elif mutation == 'implementation':
                payload['implementability_declaration']['status'] = 'BLOCK'
            else:
                wrong['outcome_opened'] = True
            if mutation != 'hash':
                wrong['protocol_hash'] = sha256_json(payload)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                economic_identity_v1(p['engine_output'], {}, frozen_envelope=wrong)
        wrong = deepcopy(value)
        wrong['frozen_declaration']['candidate_hash'] = 'a' * 64
        with self.assertRaises(ValueError):
            portfolio_diagnostics_v2([wrong])
        wrong = deepcopy(value)
        wrong['generation_id'] = 'OTHER'
        with self.assertRaises(ValueError):
            structural_identity(wrong)
        disguised = fixture()
        disguised['engine_output']['synthetic_only'] = False
        blocked = economic_test_readiness(disguised, legacy=legacy())
        self.assertEqual(blocked['status'], 'BLOCK')
        self.assertIn('FIXTURE_SOURCE_REQUIRES_SYNTHETIC_SCOPE', blocked['block_reasons'])

    def test_missing_horizon_stays_unknown_and_structured_clock_remains_literal(self):
        p = fixture()
        expression = p['implementability_meta']['economic_expression']
        del expression['horizon']  # An explicit exit clock remains sufficient.
        expression['entry_clock'] = {'relation': 'AFTER_INFORMATION', 'clock_id': 'fixture-clock'}
        protocol = p['runner_meta']['frozen_protocol']
        protocol['economic_expression'] = deepcopy(expression)
        protocol['entry_definition'] = deepcopy(expression['entry_clock'])
        value, _ = declared_identity(p)
        fields = structural_identity(value)['fields']
        self.assertEqual(fields['horizon']['status'], 'UNKNOWN')
        self.assertEqual(fields['horizon']['value'], 'UNKNOWN')
        self.assertEqual(fields['timing_clock']['value'], expression['entry_clock'])
        self.assertEqual(fields['timing_clock']['status'], 'DECLARED')

    def test_identity_owns_declaration_and_projection_does_not_mutate_it(self):
        value, envelope = declared_identity()
        before = deepcopy(value)
        envelope['protocol_payload']['candidate']['claim'] = 'changed caller object'
        result = structural_identity(value)
        result['fields']['instrument']['value'] = 'changed projection'
        self.assertEqual(value, before)
        self.assertEqual(structural_identity(value)['fields']['instrument']['value'], 'SYNTHETIC_TEST_INSTRUMENT')


if __name__ == '__main__':
    unittest.main()

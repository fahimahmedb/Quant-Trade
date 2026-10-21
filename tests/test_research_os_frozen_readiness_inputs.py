"""Independent validation binds real composed projections to their frozen body."""
from copy import deepcopy
import unittest
from unittest.mock import patch

from research.research_os.expansion import economic_test_readiness_v1 as compose
from research.research_os.expansion.validation_readiness import validate_economic_test_readiness, READY
from research.research_os.expansion.final_shape import assess_implementability, freeze_experiment_envelope
from research.research_os.scientific_store import sha256_json
from research.research_os.tests.factory_infrastructure_fixture import rebind_factory_infrastructure
from research.research_os.tests.test_economic_readiness_integration import fixture, legacy


class FrozenReadinessInputTests(unittest.TestCase):
    def bundle(self, package=None):
        captured = []
        original = compose.validator_economic_readiness_v3
        def capture(*, readiness_bundle):
            captured.append(deepcopy(readiness_bundle))
            return original(readiness_bundle=readiness_bundle)
        with patch.object(compose, 'validator_economic_readiness_v3', side_effect=capture):
            result = compose.economic_test_readiness(package or fixture(), legacy=legacy())
        self.assertEqual(result['status'], READY, result['block_reasons'])
        self.assertTrue(all(v is False for v in result['authority'].values()))
        return captured[0]

    def assert_projection_block(self, bundle):
        before = deepcopy(bundle)
        result = validate_economic_test_readiness(bundle)
        self.assertEqual(result['status'], 'BLOCK')
        self.assertIn('FROZEN_INPUT_BINDING_FAILED', [r['code'] for r in result['block_reasons']])
        self.assertEqual(result['checks']['protocol_freeze']['status'], 'PASS')
        self.assertEqual(result['checks']['reproducibility_binding']['status'], 'PASS')
        self.assertFalse(result['economic_test_authorized'])
        self.assertFalse(result['outcome_access_authorized'])
        self.assertEqual(bundle, before)
        return result

    def test_composed_readiness_freezes_the_actual_implementability_declaration(self):
        bundle = self.bundle()
        frozen = bundle['protocol']['protocol_payload']['implementability_declaration']
        self.assertEqual(bundle['implementability']['declaration_hash'], sha256_json(frozen))
        self.assertEqual(validate_economic_test_readiness(bundle)['status'], READY)

    def test_local_projection_rehashes_do_not_repair_a_changed_frozen_intent(self):
        baseline = self.bundle()
        for field in ('candidate', 'clock', 'universe', 'economic_expression', 'implementability',
                      'cost_model', 'capacity', 'multiplicity', 'trial_accounting'):
            with self.subTest(field=field):
                bundle = deepcopy(baseline)
                if field == 'candidate':
                    bundle[field]['claim'] = 'Changed outside frozen candidate'
                    digest = sha256_json(bundle[field])
                    bundle['candidate_hash'] = digest
                    bundle['protocol']['candidate_hash'] = digest
                    bundle['reproducibility']['binding_payload']['candidate_hash'] = digest
                    bundle['reproducibility']['binding_hash'] = sha256_json(bundle['reproducibility']['binding_payload'])
                elif field == 'clock':
                    bundle[field]['data_cutoff'] = '2026-10-15T10:10:00Z'
                elif field == 'universe':
                    bundle[field]['definition_hash'] = sha256_json({'different': 'universe'})
                elif field == 'economic_expression':
                    bundle[field]['spec']['instrument_rule'] = 'DIFFERENT-EXPRESSION'
                    bundle[field]['expression_hash'] = sha256_json(bundle[field]['spec'])
                elif field in ('cost_model', 'capacity'):
                    bundle[field]['model_id'] = 'DIFFERENT-MODEL'
                    bundle[field]['declaration_hash'] = sha256_json({'different': field})
                elif field == 'implementability':
                    bundle[field]['declaration_hash'] = sha256_json({'different': 'implementation'})
                elif field == 'multiplicity':
                    bundle[field]['method'] = 'different declared method'
                else:
                    bundle[field]['observed_attempt_count'] += 1
                result = self.assert_projection_block(bundle)
                self.assertTrue(all(v['status'] == 'PASS' for k, v in result['checks'].items()
                                    if k not in {'frozen_input_binding', 'experiment_infrastructure'}), result['checks'])

    def test_source_projection_cannot_be_swapped_even_with_rebound_reproducibility(self):
        baseline = self.bundle()
        for field in ('manifest_hash', 'snapshot_hash', 'source_id', 'available_at', 'route_available_at', 'revision_policy'):
            with self.subTest(field=field):
                bundle = deepcopy(baseline)
                sources = bundle['sources']
                row = sources['pit_metadata'][0]
                if field == 'manifest_hash':
                    sources[field] = sha256_json({'different': 'manifest'})
                elif field == 'snapshot_hash':
                    digest = sha256_json({'different': 'snapshot'})
                    sources['snapshot_hashes'] = [digest]
                    row['snapshot_hash'] = digest
                    bundle['reproducibility']['binding_payload']['source_snapshot_hashes'] = [digest]
                    bundle['reproducibility']['binding_hash'] = sha256_json(bundle['reproducibility']['binding_payload'])
                else:
                    row[field] = ('2026-10-15T09:30:00Z' if field.endswith('_at') else 'DIFFERENT')
                result = self.assert_projection_block(bundle)
                self.assertTrue(all(v['status'] == 'PASS' for k, v in result['checks'].items()
                                    if k not in {'frozen_input_binding', 'experiment_infrastructure'}), result['checks'])

    def test_missing_frozen_sources_protocol_or_implementation_is_not_inferred(self):
        baseline = self.bundle()
        for field in ('dataset_provenance', 'implementability_declaration'):
            bundle = deepcopy(baseline)
            del bundle['protocol']['protocol_payload'][field]
            bundle['protocol']['protocol_hash'] = sha256_json(bundle['protocol']['protocol_payload'])
            bundle['reproducibility']['binding_payload']['protocol_hash'] = bundle['protocol']['protocol_hash']
            bundle['reproducibility']['binding_hash'] = sha256_json(bundle['reproducibility']['binding_payload'])
            self.assert_projection_block(bundle)

    def test_pit_row_order_and_explicit_content_aliases_do_not_invent_trial_counts(self):
        package = fixture()
        source = deepcopy(package['sources'][0])
        source['route']['route_id'] = 'FIXTURE-ALIAS'
        package['sources'].append(source)
        package['runner_meta']['dataset_manifest_hash'] = sha256_json(package['sources'])
        bundle = self.bundle(package)
        bundle['sources']['pit_metadata'].reverse()
        rebind_factory_infrastructure(bundle)
        result = validate_economic_test_readiness(bundle)
        self.assertEqual(result['status'], READY, result['block_reasons'])
        self.assertEqual(bundle['trial_accounting']['effective_trials_status'], 'UNKNOWN')
        self.assertIsNone(bundle['trial_accounting']['estimated_effective_trials'])

    def test_optional_envelope_declaration_preserves_default_and_owns_a_copy(self):
        package = fixture()
        implementation = assess_implementability(package['engine_output'], package['implementability_meta'])
        original = freeze_experiment_envelope(package['engine_output'], implementation, {})
        self.assertNotIn('implementability_declaration', original['protocol_payload'])
        declared = freeze_experiment_envelope(package['engine_output'], implementation,
                                              {'implementability_declaration': implementation})
        self.assertNotEqual(original['protocol_hash'], declared['protocol_hash'])
        frozen = deepcopy(declared)
        implementation['status'] = 'CHANGED_AFTER_FREEZE'
        self.assertEqual(declared, frozen)
        self.assertEqual(declared['protocol_hash'], sha256_json(declared['protocol_payload']))

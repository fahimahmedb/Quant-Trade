"""Declared generation/Validator models must obey their frozen epoch policy."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from research.research_os.expansion.v2_core import (
    CLOSED_AUTHORITY, V2ContractError, assert_model_allowed, build_epoch_manifest, build_frozen_export_intent,
)
from research.research_os.expansion.v2_pipeline import run_pre_outcome_pipeline


class EpochModelAdmissionTests(unittest.TestCase):
    def bundle(self):
        return json.loads((Path(__file__).parent / 'fixtures/oracle_v2_core_fixture.json').read_text())

    def assert_block_before_export(self, bundle, code):
        before = deepcopy(bundle)
        with patch('research.research_os.expansion.v2_pipeline.build_frozen_export_intent',
                   wraps=build_frozen_export_intent) as export:
            with self.assertRaisesRegex(V2ContractError, code):
                run_pre_outcome_pipeline(bundle)
            export.assert_not_called()
        self.assertEqual(bundle, before)

    def test_generation_and_validator_outside_epoch_policy_block_actual_export(self):
        for actor, field in (('trial', 'model_identity'), ('validator', 'validator_model')):
            bundle = self.bundle()
            bundle[actor][field] = 'outside-the-epoch-model-set'
            bundle['validator'].pop('validator_hash', None)
            with self.subTest(actor=actor):
                self.assert_block_before_export(bundle, 'MODEL_OUTSIDE_EPOCH_POLICY')

    def test_non_attributable_model_list_entries_do_not_define_an_epoch(self):
        for value in (None, '', ' ', True, False, 0, 1, [], {}, 'UNKNOWN', ' unknown ', 'UNRESOLVED'):
            bundle = self.bundle()
            bundle['epoch']['allowed_model_set'] = [value]
            # Matching malformed actor values cannot manufacture policy permission.
            bundle['trial']['model_identity'] = value
            bundle['validator']['validator_model'] = value
            with self.subTest(model=value):
                self.assert_block_before_export(bundle, 'EPOCH_INVALID_IDENTIFIER:allowed_model')
                with self.assertRaisesRegex(V2ContractError, 'EPOCH_INVALID_IDENTIFIER:allowed_model'):
                    build_epoch_manifest(bundle['epoch'])

    def test_direct_admission_and_both_pipeline_actors_require_literal_identifiers(self):
        for value in (None, '', ' ', True, False, 0, 1, [], {}, 'UNKNOWN', 'UNRESOLVED'):
            # Direct admission must not accept a malformed value by equality alone.
            with self.subTest(model=value), self.assertRaisesRegex(V2ContractError, 'MODEL_INVALID_IDENTIFIER'):
                assert_model_allowed({'allowed_model_set': [value]}, value)
            for actor, field in (('trial', 'model_identity'), ('validator', 'validator_model')):
                bundle = self.bundle()
                bundle[actor][field] = value
                with self.subTest(actor=actor, model=value):
                    self.assert_block_before_export(bundle, 'MODEL_INVALID_IDENTIFIER')

    def test_explicitly_declared_in_set_models_work_without_pit_or_independence_upgrade(self):
        for actor, field in (('trial', 'model_identity'), ('validator', 'validator_model')):
            bundle = self.bundle()
            bundle['epoch']['allowed_model_set'].append('SYNTHETIC_DECLARED_LOCAL_MODEL')
            bundle[actor][field] = 'SYNTHETIC_DECLARED_LOCAL_MODEL'
            before = deepcopy(bundle)
            result = run_pre_outcome_pipeline(bundle)
            self.assertEqual(result['status'], 'READY_FOR_AUTHORIZED_ECONOMIC_TEST_ONLY')
            self.assertEqual(result['authority'], CLOSED_AUTHORITY)
            self.assertFalse(result['economic_claim_authorized'])
            self.assertEqual(bundle['leakage_classification']['model_pit'], 'NOT_PROVABLE')
            self.assertEqual(bundle, before)

    def test_existing_valid_epoch_and_qualified_receipt_remain_exactly_unchanged(self):
        bundle = self.bundle()
        before = deepcopy(bundle)
        epoch = build_epoch_manifest(bundle['epoch'])
        self.assertEqual(epoch['epoch_manifest_hash'], '8486b35bb1558efca9d33cbe74e331fa191227f7c458b213d3d95c385e759457')
        assert_model_allowed(epoch, bundle['trial']['model_identity'])
        assert_model_allowed(epoch, bundle['validator']['validator_model'])
        result = run_pre_outcome_pipeline(bundle)
        self.assertEqual(result, run_pre_outcome_pipeline(bundle))
        self.assertEqual(result['receipt_hash'], '48ec56afa0be00bcd198c38a37b49c89f2b0d00d05b7f055346e887f7b2480e8')
        self.assertEqual(result['authority'], CLOSED_AUTHORITY)
        self.assertEqual(bundle, before)


if __name__ == '__main__':
    unittest.main()

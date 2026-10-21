"""A valid trial hash does not establish temporal membership in its epoch."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from research.research_os.expansion.v2_core import (
    CLOSED_AUTHORITY, V2ContractError, assert_trial_epoch_window, build_epoch_manifest,
)
from research.research_os.expansion.v2_pipeline import run_pre_outcome_pipeline
from tests import test_research_os_native_trial_lineage as native


class TrialEpochWindowTests(unittest.TestCase):
    def bundle(self):
        return json.loads((Path(__file__).parent / 'fixtures/oracle_v2_core_fixture.json').read_text())

    def test_actual_pipeline_blocks_invalid_generation_before_export_without_mutation(self):
        for generated in ('2026-10-19T00:00:00Z', '2026-10-27T01:00:00Z',
                          '2026-10-28T00:00:00Z', 'not-a-timestamp',
                          '2026-10-20T01:10:00', None, True, {}, []):
            with self.subTest(generated=generated):
                bundle = self.bundle()
                bundle['trial']['generated_at'] = generated
                before = deepcopy(bundle)
                with patch('research.research_os.expansion.v2_pipeline.build_frozen_export_intent') as export:
                    with self.assertRaisesRegex(V2ContractError, 'TRIAL_.*(TIME|WINDOW)'):
                        run_pre_outcome_pipeline(bundle)
                    export.assert_not_called()
                self.assertEqual(bundle, before)

    def test_rehashed_native_trial_blocks_before_each_challenge_stage_and_retrieval(self):
        case = native.NativeTrialLineageTests()
        for generated, reason in (
                ('2026-10-19T00:00:00Z', 'V2_TRIAL_OUTSIDE_EPOCH_RESEARCH_WINDOW'),
                ('2026-12-31T00:00:00Z', 'V2_TRIAL_OUTSIDE_EPOCH_RESEARCH_WINDOW'),
                ('not-a-timestamp', 'V2_INVALID_TRIAL_EPOCH_TIME'),
                ('2026-10-20T02:00:00', 'V2_INVALID_TRIAL_EPOCH_TIME')):
            for stage in ('independent_validation', 'cross_examination', 'red_team',
                          'claim_restriction', 'integration_handoff'):
                with self.subTest(generated=generated, stage=stage):
                    snapshot, task = native.fixture()
                    snapshot.values[native.TRIAL]['generated_at'] = generated
                    native.rehash(snapshot.values[native.TRIAL])
                    case.assert_native_block(snapshot, task, reason, stage)

    def test_half_open_window_uses_instants_and_preserves_valid_hash_goldens(self):
        bundle = self.bundle()
        before = deepcopy(bundle)
        for generated in ('2026-10-20T01:00:00Z', '2026-10-20T03:00:00+02:00',
                          '2026-10-27T00:59:59.999999Z'):
            with self.subTest(generated=generated):
                assert_trial_epoch_window(bundle['epoch'], dict(bundle['trial'], generated_at=generated))
        for generated in ('2026-10-20T02:59:59.999999+02:00', '2026-10-27T03:00:00+02:00'):
            with self.assertRaisesRegex(V2ContractError, 'TRIAL_OUTSIDE_EPOCH_RESEARCH_WINDOW'):
                assert_trial_epoch_window(bundle['epoch'], dict(bundle['trial'], generated_at=generated))
        result = run_pre_outcome_pipeline(bundle)
        self.assertEqual(result['receipt_hash'], '48ec56afa0be00bcd198c38a37b49c89f2b0d00d05b7f055346e887f7b2480e8')
        self.assertEqual(result['epoch_manifest_hash'], build_epoch_manifest(bundle['epoch'])['epoch_manifest_hash'])
        self.assertEqual(result['authority'], CLOSED_AUTHORITY)
        self.assertFalse(result['outcome_accessed'])
        self.assertEqual(bundle, before)

    def test_malformed_missing_empty_reversed_or_naive_windows_fail_closed(self):
        bundle = self.bundle()
        start, end = bundle['epoch']['research_window'].values()
        for window in (None, [], 'UNKNOWN', {}, {'start': start}, {'end': end},
                       {'start': end, 'end': start}, {'start': start, 'end': start},
                       {'start': 'bad', 'end': end},
                       {'start': '2026-10-20T01:00:00', 'end': end}):
            with self.subTest(window=window):
                changed = deepcopy(bundle)
                changed['epoch']['research_window'] = window
                with patch('research.research_os.expansion.v2_pipeline.build_frozen_export_intent') as export:
                    with self.assertRaisesRegex(V2ContractError, 'TRIAL_.*(TIME|WINDOW)'):
                        run_pre_outcome_pipeline(changed)
                    export.assert_not_called()
        epoch = deepcopy(bundle['epoch'])
        del epoch['research_window']
        with self.assertRaisesRegex(V2ContractError, 'INVALID_TRIAL_EPOCH_TIME'):
            assert_trial_epoch_window(epoch, bundle['trial'])
        trial = deepcopy(bundle['trial'])
        del trial['generated_at']
        with self.assertRaisesRegex(V2ContractError, 'INVALID_TRIAL_EPOCH_TIME'):
            assert_trial_epoch_window(bundle['epoch'], trial)


if __name__ == '__main__':
    unittest.main()

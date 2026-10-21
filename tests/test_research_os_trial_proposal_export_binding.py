"""Trial labels cannot export a Candidate absent from generated proposals."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from research.research_os.expansion.v2_core import (
    CLOSED_AUTHORITY, V2ContractError, assert_trial_proposal_binding, build_candidate,
    build_frozen_export_intent, build_validator_result,
)
from research.research_os.expansion.v2_pipeline import run_pre_outcome_pipeline
from tests import test_research_os_v2_worker_integration as native


class TrialProposalExportBindingTests(unittest.TestCase):
    def bundle(self):
        return json.loads((Path(__file__).parent / 'fixtures/oracle_v2_core_fixture.json').read_text())

    def rebind_validator(self, bundle):
        candidate = build_candidate(bundle['candidate'])
        bundle['validator'] = build_validator_result(dict(bundle['validator'], candidate_hash=candidate['candidate_hash']))
        return candidate

    def assert_block_before_export(self, bundle):
        before = deepcopy(bundle)
        with patch('research.research_os.expansion.v2_pipeline.build_frozen_export_intent',
                   wraps=build_frozen_export_intent) as export:
            with self.assertRaisesRegex(V2ContractError, 'TRIAL_.*BINDING_MISMATCH'):
                run_pre_outcome_pipeline(bundle)
            export.assert_not_called()
        self.assertEqual(bundle, before)

    def test_actual_pipeline_requires_an_attributed_generated_proposal(self):
        original = self.bundle()['trial']['generated_proposals'][0]
        variants = [[{'id': 'UNATTRIBUTED'}], [None, False, 'P1'],
                    [dict(original, hypothesis_id='OTHER')], [dict(original, generation_id='OTHER')],
                    [dict(original, candidate_hash='a' * 64)]]
        for proposals in variants:
            bundle = self.bundle()
            bundle['trial']['generated_proposals'] = proposals
            with self.subTest(proposals=proposals):
                self.assert_block_before_export(bundle)

    def test_changed_same_generation_candidate_with_fresh_validator_cannot_reuse_old_proposal(self):
        bundle = self.bundle()
        old_hash = bundle['trial']['generated_proposals'][0]['candidate_hash']
        bundle['candidate']['claim'] = 'a changed same-generation scientific claim'
        candidate = self.rebind_validator(bundle)
        self.assertNotEqual(candidate['candidate_hash'], old_hash)
        self.assertEqual(bundle['validator']['candidate_hash'], candidate['candidate_hash'])
        self.assert_block_before_export(bundle)

    def test_valid_generic_replay_retains_accounting_and_closed_authority(self):
        bundle = self.bundle()
        before = deepcopy(bundle)
        result = run_pre_outcome_pipeline(bundle)
        self.assertEqual(result, run_pre_outcome_pipeline(bundle))
        self.assertEqual(result['status'], 'READY_FOR_AUTHORIZED_ECONOMIC_TEST_ONLY')
        self.assertEqual(result['authority'], CLOSED_AUTHORITY)
        self.assertFalse(result['outcome_accessed'])
        self.assertEqual(len(bundle['trial']['generated_proposals']), 2)
        self.assertEqual(len(bundle['trial']['discarded_proposals']), 1)
        self.assertEqual(bundle['trial']['generated_proposals'][0]['candidate_hash'], result['candidate_hash'])
        self.assertEqual(bundle, before)

    def test_source_proposal_hash_and_v2_projection_hash_remain_distinct(self):
        case = native.V2WorkerIntegrationTests()
        candidate = case.v2_candidate()
        trial = case.v2_trial(candidate)
        before = deepcopy([candidate, trial])
        assert_trial_proposal_binding(candidate, trial)
        self.assertNotEqual(candidate['candidate_hash'], candidate['evidence_manifest']['source_candidate_hash'])
        wrong = deepcopy(trial)
        wrong['generated_proposals'][0]['candidate_hash'] = candidate['candidate_hash']
        with self.assertRaisesRegex(V2ContractError, 'TRIAL_PROPOSAL_BINDING_MISMATCH'):
            assert_trial_proposal_binding(candidate, wrong)
        self.assertEqual([candidate, trial], before)
        # Exercise the same source-reference mode through the pure entrypoint.
        bundle = self.bundle()
        bundle['candidate']['evidence_manifest'].update(
            source_candidate_hash=candidate['evidence_manifest']['source_candidate_hash'],
            documentary_packet_hash=candidate['evidence_manifest']['documentary_packet_hash'])
        bundle['trial']['source_packet_hash'] = candidate['evidence_manifest']['documentary_packet_hash']
        bundle['trial']['generated_proposals'][0]['candidate_hash'] = candidate['evidence_manifest']['source_candidate_hash']
        self.rebind_validator(bundle)
        result = run_pre_outcome_pipeline(bundle)
        self.assertEqual(result['authority'], CLOSED_AUTHORITY)
        self.assertEqual(result['status'], 'READY_FOR_AUTHORIZED_ECONOMIC_TEST_ONLY')
        bundle['trial']['source_packet_hash'] = '0' * 64
        self.assert_block_before_export(bundle)

    def test_partial_or_invalid_source_bindings_cannot_fall_back_to_generic_proposal(self):
        for field in ('source_candidate_hash', 'documentary_packet_hash'):
            for value in (None, '', True, 'UNKNOWN', [], {}, 'a' * 64):
                bundle = self.bundle()
                bundle['candidate']['evidence_manifest'][field] = value
                candidate = self.rebind_validator(bundle)
                # Even a freshly attributed V2 hash cannot repair missing source facts.
                bundle['trial']['generated_proposals'][0]['candidate_hash'] = candidate['candidate_hash']
                with self.subTest(field=field, value=value):
                    self.assert_block_before_export(bundle)


if __name__ == '__main__':
    unittest.main()

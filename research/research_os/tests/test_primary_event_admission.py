"""Primary Event admission is an offline factual build, never an economic test."""
import json
import unittest
from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

from research.research_os.engines.builtin import ENGINE_REGISTRY
from research.research_os.engines.protocol import EngineContext, EngineContractError, validate_engine_output
from research.research_os.expansion.canonical_spine import run_canonical_spine
from research.research_os.expansion.source_adapters_v1 import (
    apple_dividend_packet, capture_apple_dividend_announcements,
)
from research.research_os.tests.test_work_build_depth import execution_plan, repin

BASE = Path(__file__).resolve().parents[1]


class PrimaryEventAdmissionTests(unittest.TestCase):
    def source(self):
        return json.loads((BASE / 'sources/apple_dividend_announcements.json').read_text())

    def output(self, source=None):
        return ENGINE_REGISTRY['event_document'].run(source or self.source(), EngineContext('EVENT', synthetic_only=False))

    def test_actual_capture_derives_distribution_comparison_without_guidance_or_surprise(self):
        source = self.source()
        output = self.output(source)
        validate_engine_output(output)
        candidate = output['candidate']
        self.assertEqual(candidate['documentary_evidence']['measurements'], {
            'previous_declared_distribution':'0.25', 'current_declared_distribution':'0.26',
            'year_over_year_declared_change':'0.01', 'year_over_year_declared_change_fraction':'0.04'})
        self.assertEqual(len(output['source_refs']), 2)
        self.assertTrue(candidate['hypothesis_id'].startswith('DOC-EVENT-'))
        self.assertNotIn('guidance', candidate['claim'])
        self.assertIn('not consecutive payments', candidate['claim'])
        self.assertIn('corrected or superseded', candidate['falsification_scope'])
        self.assertEqual(candidate['horizon'], 'UNQUALIFIED')
        self.assertEqual(candidate['observation_authorization'], 'NOT_AUTHORIZED')
        self.assertEqual(source['freeze_time'], source['documentary_packet']['available_at'])
        # Capture order differs from announcement order: the later capture bounds both.
        self.assertEqual(source['freeze_time'], source['documentary_packet']['capture']['records'][0]['captured_at'])

    def test_amounts_determine_direction_and_identity_for_a_new_receipt(self):
        source = self.source()
        original = self.output(source)
        records = deepcopy(source['documentary_packet']['capture']['records'])
        records[1].update(declared_amount_per_share='0.24', capture_excerpt='cash dividend of $0.24 per share', raw_sha256='f'*64)
        # Counterfactual receipt for parser testing; never persisted as real evidence.
        source['documentary_packet'] = apple_dividend_packet(records)
        changed = self.output(source)
        self.assertEqual(changed['candidate']['documentary_evidence']['measurements']['year_over_year_declared_change'], '-0.01')
        self.assertNotEqual(original['candidate']['claim'], changed['candidate']['claim'])
        self.assertNotEqual(original['candidate']['hypothesis_id'], changed['candidate']['hypothesis_id'])

    def test_repin_does_not_admit_inconsistent_source_period_unit_clock_or_outcome(self):
        mutations = [
            lambda p:p['facts'].update(current_distribution='0.27'),
            lambda p:p.update(period='CONSECUTIVE_QUARTERS'),
            lambda p:p.update(unit='USD_annualized'),
            lambda p:p.update(issuer_id='OTHER'),
            lambda p:p.update(event_kind='GUIDANCE_REVISION'),
            lambda p:p.update(published_at='2025-05-01T00:00:00Z'),
            lambda p:p.update(available_at='2025-05-01T00:00:00Z'),
            lambda p:p['capture'].update(comparison_basis='IMMEDIATE_PRIOR_PAYMENT'),
            lambda p:p['capture']['records'][0].update(source_url='https://example.com/'),
            lambda p:p['capture']['records'][0].update(raw_sha256='missing'),
            lambda p:p['capture']['records'][0].update(captured_at='2026-10-15T18:06:31'),
            lambda p:p['capture']['records'][0].update(announcement='FY2025_Q2_RELEASE'),
            lambda p:p['capture']['records'][0].update(declared_amount_per_share='NaN'),
            lambda p:p['capture']['records'][0].update(capture_excerpt='cash dividend of $0.30 per share'),
            lambda p:p['capture']['records'][0].update(price_effect='positive'),
            lambda p:p['capture'].update(realized_return='0.1'),
            lambda p:p['capture'].update(records=[]),
        ]
        for i, mutate in enumerate(mutations):
            with self.subTest(mutation=i):
                source = self.source()
                mutate(source['documentary_packet'])
                repin(source)
                with self.assertRaises(EngineContractError):
                    self.output(source)
        source = self.source()
        source['freeze_time'] = '2026-01-01T00:00:00Z'
        with self.assertRaises(EngineContractError):
            self.output(source)

    def test_cannot_drop_prior_source_or_relabel_as_synthetic(self):
        output = self.output()
        for mutate in (lambda o:o.update(synthetic_only=True), lambda o:o['source_refs'].pop(0)):
            changed = deepcopy(output)
            mutate(changed)
            with self.assertRaises(EngineContractError):
                validate_engine_output(changed)
        with self.assertRaises(EngineContractError):
            ENGINE_REGISTRY['event_document'].run(self.source(), EngineContext('WRONG_MODE'))

    def test_raw_capture_digest_and_excerpt_are_checked_before_admission(self):
        captured = json.loads((BASE / 'sources/apple_dividend_announcements_capture.json').read_text())
        with TemporaryDirectory() as directory:
            paths = [Path(directory)/str(i) for i in range(2)]
            for path in paths:
                path.write_text('unrelated HTML')
            with self.assertRaises(ValueError):
                capture_apple_dividend_announcements(captured, paths)

    def test_offline_execution_replays_without_economic_outcomes(self):
        inputs = [{'engine_key':'event_document', 'source':self.source()}]
        runner, plan = execution_plan(inputs)
        with TemporaryDirectory() as directory:
            result = runner.execute(plan, inputs, Path(directory))
            self.assertEqual(result, runner.execute(plan, inputs, Path(directory)))
            self.assertEqual(len(list(Path(directory).glob('*.completed.json'))), 1)
        self.assertEqual(result['evidence_class'], 'DOCUMENTARY')
        self.assertEqual(result['economic_result'], 'NOT_OBSERVED')
        self.assertFalse(result['outcome_accessed'])

    def test_canonical_keeps_unqualified_economics_blocked_and_replays(self):
        source = self.source()
        hid = self.output(source)['candidate']['hypothesis_id']
        configuration = json.loads((BASE / 'simulations/aggressive_architecture_fixture.json').read_text())
        configuration['sources']['event_document'] = source
        configuration['base_time'] = source['freeze_time']
        configuration['implementability'][hid] = {'source_available':True, 'pit_feasible':True,
            'expression_feasible':False, 'cost_model_feasible':False, 'capacity_observable':False}
        configuration['experiments'][hid] = {'dataset_provenance':{'source_ref':source['source_ref'],
            'capture_hash':source['documentary_packet']['content_hash']}, 'code_version':'event-admission.v1',
            'cost_model_version':'UNQUALIFIED', 'pit_controls_declared':True,
            'leakage_controls_declared':True, 'multiplicity_accounting_declared':False}
        configuration['economic_identity'][hid] = {'asset':'AAPL', 'payer':'UNKNOWN', 'beta':'UNKNOWN',
            'capacity':'UNKNOWN', 'liquidity':'UNKNOWN', 'tail_exposure':'UNKNOWN'}
        task = json.loads((BASE / 'simulations/canonical_spine_task.json').read_text())
        task['inputs'].update(engine_key='event_document', evidence_mode='DOCUMENTARY')
        task['required_capability'] = 'event_document'
        task['authority']['scope'] = 'DOCUMENTARY_SOURCE_QUALIFICATION_ONLY'
        task['allowed_actions'].append('DOCUMENTARY_RESEARCH')
        task['lease']['claimed_at'] = source['freeze_time']
        task['lease']['expires_at'] = (datetime.fromisoformat(source['freeze_time']) + timedelta(hours=1)).isoformat()
        with TemporaryDirectory() as directory:
            result = run_canonical_spine(BASE, configuration, task, checkpoint_dir=Path(directory))
            replay = run_canonical_spine(BASE, configuration, task, checkpoint_dir=Path(directory))
            self.assertEqual(result, replay)
            self.assertFalse(list(Path(directory).glob('*.completed.json')))
        self.assertEqual(result['validation']['status'], 'BLOCK')
        self.assertEqual(result['forward_registration']['readiness'], 'NOT_READY')
        self.assertIn('BLOCK_COST_MODEL', result['red_team']['negative_rights'])
        self.assertIn('BLOCK_CAPACITY', result['red_team']['negative_rights'])
        self.assertFalse(any(result['authority'].values()))


if __name__ == '__main__':
    unittest.main()

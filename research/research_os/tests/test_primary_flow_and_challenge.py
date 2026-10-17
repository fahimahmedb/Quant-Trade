"""Actual captured input integrity and deterministic challenge, not alpha validation."""
import json
import unittest
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from research.research_os.engines.builtin import ENGINE_REGISTRY
from research.research_os.engines.protocol import EngineContext, EngineContractError
from research.research_os.expansion.source_adapters_v1 import capture_sec_t1_faq
from research.research_os.expansion.canonical_depth_v1 import execute_documentary_depth
from research.research_os.expansion.final_shape import freeze_experiment_envelope
from research.research_os.expansion.validation_v2 import validator_diagnostics_v2
from research.research_os.legacy import LegacyKnowledgeBase
from research.research_os.scientific_store import sha256_json
from research.research_os.tests.test_work_build_depth import repin

BASE = Path(__file__).resolve().parents[1]
PRIMARY = {'fundamental':'apple_fy2025_statement_cells.json',
           'event_document':'apple_dividend_announcements.json',
           'institutional_flow':'sec_t1_staff_faq.json'}


def source_for(key):
    return json.loads((BASE / 'sources' / PRIMARY[key]).read_text())


class PrimaryFlowTests(unittest.TestCase):
    def output(self, source=None):
        return ENGINE_REGISTRY['institutional_flow'].run(source or source_for('institutional_flow'),
                                                        EngineContext('FLOW', synthetic_only=False))

    def test_constraint_is_not_a_measured_flow_or_binding_rule(self):
        output = self.output()
        candidate = output['candidate']
        self.assertEqual(candidate['documentary_evidence']['measurements'], {
            'standard_settlement_business_days':'1', 'constrained_share':'UNKNOWN', 'directional_flow':'UNKNOWN'})
        self.assertTrue(candidate['hypothesis_id'].startswith('DOC-FLOW-'))
        self.assertIn('nonbinding', candidate['claim'])
        self.assertIn('exempt', candidate['falsification_scope'])
        self.assertIn('agreed extension', candidate['falsification_scope'])
        self.assertEqual(LegacyKnowledgeBase.load(BASE).screen_candidate(candidate)['status'], 'NO_EXACT_LEGACY_CONFLICT')

    def test_rule_scope_and_capture_cannot_be_relabelled_or_backdated(self):
        mutations = [lambda p:p.update(actor='all investors'),
                     lambda p:p.update(instrument='all securities'),
                     lambda p:p.update(horizon='1d trade'),
                     lambda p:p.update(period='CURRENT_BINDING_RULE'),
                     lambda p:p.update(unit='calendar_days'),
                     lambda p:p['facts'].update(standard_settlement_business_days='2'),
                     lambda p:p['facts'].update(constrained_quantity='100'),
                     lambda p:p['capture'].update(document_kind='BINDING_RULE'),
                     lambda p:p['capture']['excerpts'].update(cycle='T+2'),
                     lambda p:p['capture'].update(raw_sha256='not-a-digest'),
                     lambda p:p.update(published_at='2024-03-27T00:00:00Z'),
                     lambda p:p['capture'].update(future_outcome='buy'),
                     lambda p:p['capture'].update(retrieved_at='2099-01-01T00:00:00Z')]
        for i, mutate in enumerate(mutations):
            with self.subTest(mutation=i):
                source = source_for('institutional_flow')
                mutate(source['documentary_packet'])
                repin(source)
                with self.assertRaises(EngineContractError):
                    self.output(source)

    def test_capture_refuses_a_number_without_actor_exception_or_status_context(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'not-the-faq.html'
            path.write_text('one business day after the trade date')
            with self.assertRaises(ValueError):
                capture_sec_t1_faq(path, retrieved_at='2026-10-15T00:00:00Z')


class ActualDocumentaryChallengeTests(unittest.TestCase):
    def args(self, key, directory):
        source = source_for(key)
        output = ENGINE_REGISTRY[key].run(source, EngineContext('CHALLENGE', synthetic_only=False))
        # Deliberately optimistic metadata isolates validator checks; it is a test
        # fixture, not a finding that these real candidates are implementable.
        envelope = freeze_experiment_envelope(output, {'status':'PASS'}, {'code_version':'CHALLENGE_ONLY'})
        depth = execute_documentary_depth(output, envelope, Path(directory))
        envelope['dry_run_execution'] = depth
        return dict(engine_output=output, validation_v1={'independent_from_producer':True,
            'validator':'challenge-validator', 'producer_engine':output['engine_id'], 'implementability_status':'PASS'},
            source_qualifications=[depth['source_qualification']], envelope=envelope,
            dry_run_plan=depth['dry_run_plan'], executed_dry_run=depth['executed_dry_run'],
            trial_record={'observed_attempt_count':0,'effective_trials_status':'UNKNOWN','estimated_effective_trials':None},
            experiment_meta={'multiplicity_accounting_declared':True})

    def test_actual_artifacts_reconstruct_and_negative_rights_survive_repinning(self):
        for key in PRIMARY:
            with self.subTest(engine=key), TemporaryDirectory() as directory:
                args = self.args(key, directory)
                diagnostics = validator_diagnostics_v2(**args)
                self.assertEqual(diagnostics['status'], 'BLOCK')
                self.assertEqual(diagnostics['checks']['documentary_evidence_bound']['status'], 'PASS')
                self.assertEqual(diagnostics['checks']['documentary_dossier_bound']['status'], 'PASS')
                self.assertIn('documentary_dossier_sufficient', diagnostics['critical_failures'])
                mutations = [
                    ('engine_output', lambda o:o['candidate'].update(claim='profitable alpha')),
                    ('engine_output', lambda o:o['candidate'].update(falsification_scope='')),
                    ('engine_output', lambda o:o['candidate'].pop('documentary_evidence')),
                    ('engine_output', lambda o:o['candidate'].update(documentary_evidence='missing')),
                    ('engine_output', lambda o:o['candidate'].update(documentary_evidence={'packet':'invalid'})),
                    ('engine_output', lambda o:o.update(engine_id='invented-producer')),
                    ('validation_v1', lambda v:v.update(validator=args['engine_output']['engine_id'])),
                    ('source_qualifications', lambda v:v[0]['canonical_route'].update(availability_start='2024-01-01T00:00:00Z')),
                    ('source_qualifications', lambda v:v[0]['canonical_route'].update(revision_policy='UNKNOWN')),
                    ('source_qualifications', lambda v:v[0].update(route_hash='forged')),
                    ('trial_record', lambda v:v.update(effective_trials_status='KNOWN',estimated_effective_trials=-1)),
                    ('executed_dry_run', lambda v:v.update(economic_result='ALPHA_VALIDATED')),
                    ('dry_run_plan', lambda v:v['plan'].update(protocol_hash='another-protocol')),
                    ('dry_run_plan', lambda v:v['plan'].update(dataset_manifest_hash='another-dataset')),
                ]
                for field, mutate in mutations:
                    changed = deepcopy(args)
                    mutate(changed[field])
                    # Repin public hashes so failure demonstrates semantic binding.
                    if field == 'engine_output':
                        changed['envelope'] = freeze_experiment_envelope(changed[field], {'status':'PASS'}, {'code_version':'CHALLENGE_ONLY'})
                    if field == 'dry_run_plan':
                        changed[field]['execution_plan_hash'] = sha256_json(changed[field]['plan'])
                    if field == 'executed_dry_run':
                        changed[field]['execution_receipt_hash'] = sha256_json({k:v for k,v in changed[field].items() if k != 'execution_receipt_hash'})
                    with self.subTest(field=field):
                        diagnostics = validator_diagnostics_v2(**changed)
                        self.assertEqual(diagnostics['status'], 'BLOCK')
                        if field in {'engine_output', 'source_qualifications'}:
                            self.assertIn('documentary_evidence_bound', diagnostics['critical_failures'])
                        if field == 'executed_dry_run':
                            self.assertIn('executed_documentary_transform', diagnostics['critical_failures'])

    def test_missing_disconfirmation_is_a_critical_failure_even_without_documentary_evidence(self):
        args = {'engine_output':ENGINE_REGISTRY['quant'].run({'source_ref':'synthetic://test'},EngineContext('TEST')),
                'validation_v1':{}, 'source_qualifications':[], 'envelope':{}, 'dry_run_plan':{},
                'trial_record':{}, 'experiment_meta':{}}
        args['engine_output']['candidate']['falsification_scope'] = ''
        self.assertIn('falsification_scope_present', validator_diagnostics_v2(**args)['critical_failures'])


if __name__ == '__main__':
    unittest.main()

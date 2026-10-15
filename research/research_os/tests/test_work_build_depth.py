"""Adversarial coverage of real offline execution; all input evidence is synthetic."""
import json
import unittest
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from research.research_os.engines.builtin import ENGINE_REGISTRY
from research.research_os.engines.protocol import EngineContext, EngineContractError
from research.research_os.expansion.archaeology import EdgeArchaeologyEngine
from research.research_os.scientific_store import sha256_json
from research.research_os.expansion.experiment_runner import DryRunExperimentRunner
from research.research_os.expansion.persistent_state import read_immutable_json
from research.research_os.expansion.canonical_spine import run_canonical_spine, ENGINE_CAPABILITIES
from research.research_os.expansion.forward_v2 import ForwardRegistryV2, build_forward_contract_v2
from research.research_os.expansion.portfolio_v2 import portfolio_diagnostics_v2
from research.research_os.expansion.validation_v2 import validator_diagnostics_v2
from research.research_os.engines.decay import decay_monitor

BASE = Path(__file__).resolve().parents[1]


def sources():
    return json.loads((BASE / 'simulations/documentary_inputs_fixture.json').read_text())['sources']


def repin(source):
    packet = source['documentary_packet']
    packet['content_hash'] = sha256_json({k: v for k, v in packet.items() if k != 'content_hash'})


def execution_plan(inputs):
    runner = DryRunExperimentRunner()
    plan = runner.plan(
        {'experiment_id':'EXEC-DOC', 'status':'FROZEN_READY_NO_OUTCOME', 'protocol_hash':'synthetic-protocol', 'outcome_opened':False},
        [{'status':'PASS', 'outcome_accessed':False, 'route_hash':item['source']['documentary_packet']['content_hash']} for item in inputs],
        {'dataset_manifest_hash':sha256_json(inputs), 'code_hash':runner.execution_code_hash(),
         'environment_hash':runner.execution_environment_hash(), 'seed':0, 'declared_metrics':['DOCUMENTARY_FACTS_V1']},
    )
    return runner, plan


class DocumentaryEngineTests(unittest.TestCase):
    def run_engine(self, family, source=None):
        engine = EdgeArchaeologyEngine() if family == 'archaeology' else ENGINE_REGISTRY[family]
        return engine.run(source or sources()[family], EngineContext('WORK-DEPTH'))

    def test_statement_numbers_determine_candidate_and_free_cash_flow(self):
        source = sources()['fundamental']
        before = self.run_engine('fundamental', source)
        source['documentary_packet']['facts']['capital_expenditure'] = '25'
        repin(source)
        after = self.run_engine('fundamental', source)
        self.assertEqual(before['candidate']['documentary_evidence']['measurements']['free_cash_flow'], '12')
        self.assertEqual(after['candidate']['documentary_evidence']['measurements']['free_cash_flow'], '-7')
        self.assertNotEqual(before['candidate']['claim'], after['candidate']['claim'])

    def test_event_revision_direction_changes_from_inputs(self):
        source = sources()['event_document']
        positive = self.run_engine('event_document', source)
        source['documentary_packet']['facts'].update(current_low='60', current_high='80')
        repin(source)
        negative = self.run_engine('event_document', source)
        self.assertEqual(positive['candidate']['documentary_evidence']['measurements']['guidance_change'], '20')
        self.assertEqual(negative['candidate']['documentary_evidence']['measurements']['guidance_change'], '-30')

    def test_constraint_engines_compute_coverage_without_outcomes(self):
        for key in ('quant', 'institutional_flow', 'archaeology'):
            output = self.run_engine(key)
            self.assertEqual(output['candidate']['documentary_evidence']['measurements']['constrained_share'], '0.1')
            self.assertTrue(output['synthetic_only'])
            self.assertEqual(output['candidate']['observation_authorization'], 'NOT_AUTHORIZED')

    def test_tamper_unknown_outcome_fields_and_nonfinite_values_are_rejected(self):
        mutations = [
            lambda p: p['facts'].update(revenue='999'),  # no repin: tamper
            lambda p: p.update(realized_return=0.5),
            lambda p: p['facts'].update(revenue='NaN'),
            lambda p: p.update(period=''),
            lambda p: p.update(revision_status='UNKNOWN'),
            lambda p: p.update(available_at='2026-10-16T10:00:00Z'),
            lambda p: p.update(published_at='2026-10-14T10:00:00'),
            lambda p: p.update(evidence_class='CAPTURED_DOCUMENT'),
        ]
        for i, mutation in enumerate(mutations):
            with self.subTest(mutation=i):
                source = sources()['fundamental']
                mutation(source['documentary_packet'])
                if i:
                    repin(source)
                with self.assertRaises(EngineContractError):
                    self.run_engine('fundamental', source)

    def test_conflicting_guidance_and_ineligible_population_are_rejected(self):
        for key, facts in [('event_document', {'current_low':'150', 'current_high':'100'}),
                           ('institutional_flow', {'constrained_quantity':'1001'})]:
            source = sources()[key]
            source['documentary_packet']['facts'].update(facts)
            repin(source)
            with self.assertRaises(EngineContractError):
                self.run_engine(key, source)


class ExecutedDryRunTests(unittest.TestCase):
    def setUp(self):
        self.inputs = [{'engine_key':k, 'source':v} for k, v in sources().items()]
        self.runner, self.plan = execution_plan(self.inputs)

    def test_execute_restart_and_replay_use_one_immutable_completion(self):
        with TemporaryDirectory() as directory:
            result = self.runner.execute(self.plan, self.inputs, Path(directory))
            replay = DryRunExperimentRunner().execute(self.plan, self.inputs, Path(directory))
            self.assertEqual(result, replay)
            self.assertEqual(result['state'], 'EXECUTED_DRY_RUN')
            self.assertEqual(len(result['records']), 5)
            self.assertEqual(len(list(Path(directory).glob('*.completed.json'))), 1)
            self.assertFalse(result['outcome_accessed'])

    def test_interrupt_after_prepare_recovers_without_false_completion(self):
        with TemporaryDirectory() as directory:
            with patch.object(ENGINE_REGISTRY['fundamental'], 'run', side_effect=RuntimeError('interrupted')):
                with self.assertRaises(RuntimeError):
                    self.runner.execute(self.plan, self.inputs, Path(directory))
            self.assertEqual(len(list(Path(directory).glob('*.prepared.json'))), 1)
            self.assertEqual(len(list(Path(directory).glob('*.completed.json'))), 0)
            recovered = self.runner.execute(self.plan, self.inputs, Path(directory))
            self.assertEqual(recovered['state'], 'EXECUTED_DRY_RUN')

    def test_mismatched_inputs_code_environment_and_blocked_plan_rejected(self):
        for field in ('dataset_manifest_hash', 'code_hash', 'environment_hash'):
            changed = deepcopy(self.plan)
            changed['plan'][field] = 'wrong'
            changed['execution_plan_hash'] = sha256_json(changed['plan'])
            with TemporaryDirectory() as directory, self.assertRaises(ValueError):
                self.runner.execute(changed, self.inputs, Path(directory))
        changed = deepcopy(self.plan)
        changed['status'] = 'BLOCK'
        with self.assertRaises(ValueError):
            self.runner.replay(changed)

    def test_completed_checkpoint_tampering_rejected_on_replay(self):
        with TemporaryDirectory() as directory:
            self.runner.execute(self.plan, self.inputs, Path(directory))
            path = next(Path(directory).glob('*.completed.json'))
            record = json.loads(path.read_text())
            record['payload']['state'] = 'FAKE'
            path.write_text(json.dumps(record))
            with self.assertRaises(ValueError):
                self.runner.execute(self.plan, self.inputs, Path(directory))


def canonical(engine_key, directory=None, override=None):
    fixture = json.loads((BASE / 'simulations/aggressive_architecture_fixture.json').read_text())
    fixture['sources'][engine_key] = sources()[engine_key]
    task = json.loads((BASE / 'simulations/canonical_spine_task.json').read_text())
    task['inputs']['engine_key'] = engine_key
    task['required_capability'] = ENGINE_CAPABILITIES[engine_key]
    return run_canonical_spine(BASE, fixture, task,
                               legacy_ledger_path=BASE / 'legacy/LEGACY_RESEARCH_LEDGER.imported.json',
                               checkpoint_dir=Path(directory) if directory else None,
                               candidate_override_hypothesis_id=override)


class CanonicalExecutedDepthTests(unittest.TestCase):
    def test_executed_documents_flow_through_original_spine_and_persist(self):
        for key in ('fundamental', 'event_document', 'quant', 'archaeology'):
            with self.subTest(engine=key), TemporaryDirectory() as directory:
                first = canonical(key, directory)
                replay = canonical(key, directory)
                self.assertEqual(first, replay)
                self.assertEqual(first['validation']['status'], 'PASS')
                self.assertEqual(first['documentary_depth']['execution_status'], 'EXECUTED_DRY_RUN')
                self.assertEqual(first['forward_registration']['readiness'], 'READY_AWAITING_OWNER_AUTHORITY')
                self.assertTrue(first['scientific_ledger']['verified'])
                self.assertEqual(len({r['receipt_id'] for r in first['worker_receipts']}), len(first['worker_receipts']))
                self.assertEqual(read_immutable_json(next(Path(directory).glob('*.canonical.json'))), first)
                self.assertFalse(any(first['authority'].values()))

    def test_plan_only_and_flow_blocker_cannot_be_promoted(self):
        planned = canonical('fundamental')
        self.assertEqual(planned['validation']['status'], 'BLOCK')
        self.assertIn('executed_documentary_transform', planned['validation']['critical_failures'])
        self.assertEqual(planned['forward_registration']['readiness'], 'NOT_READY')
        with TemporaryDirectory() as directory:
            flow = canonical('institutional_flow', directory)
            self.assertEqual(flow['validation']['status'], 'BLOCK')
            self.assertIn('BLOCK_COST_MODEL', flow['red_team']['negative_rights'])
            self.assertIn('BLOCK_CAPACITY', flow['red_team']['negative_rights'])
            self.assertEqual(flow['forward_registration']['readiness'], 'NOT_READY')
            self.assertFalse(list(Path(directory).glob('*.completed.json')))

    def test_independent_validator_rejects_producer_protocol_and_receipt_forgery(self):
        with TemporaryDirectory() as directory:
            result = canonical('fundamental', directory)
            metadata = json.loads((BASE / 'simulations/aggressive_architecture_fixture.json').read_text())['experiments']['SYN-FUND-001']
            depth = result['documentary_depth']
            args = dict(engine_output=result['candidate'], validation_v1=result['validation'],
                        source_qualifications=[depth['source_qualification']], envelope=result['experiment_envelope'],
                        dry_run_plan=depth['dry_run_plan'], trial_record=result['trial_ledger'][0],
                        experiment_meta=metadata, executed_dry_run=depth['executed_dry_run'])
            self.assertEqual(validator_diagnostics_v2(**args)['status'], 'PASS')
            for field, mutate in [
                ('validation_v1', lambda v: v.update(validator=result['candidate']['engine_id'])),
                ('envelope', lambda v: v['protocol_payload']['candidate'].update(claim='rewritten')),
                ('executed_dry_run', lambda v: v['records'][0]['candidate'].update(claim='forged')),
                ('trial_record', lambda v: v.update(observed_attempt_count=-1)),
                ('source_qualifications', lambda v: v[0].update(point_in_time_qualified=False)),
            ]:
                changed = deepcopy(args)
                mutate(changed[field])
                self.assertEqual(validator_diagnostics_v2(**changed)['status'], 'BLOCK')

    def test_exact_legacy_duplicate_stops_before_runner(self):
        ledger = json.loads((BASE / 'legacy/LEGACY_RESEARCH_LEDGER.imported.json').read_text())
        hid = next(r['HYPOTHESIS_ID'] for r in ledger['records'] if r.get('HYPOTHESIS_ID') not in (None, '', 'UNKNOWN'))
        with TemporaryDirectory() as directory, patch.object(DryRunExperimentRunner, 'execute', side_effect=AssertionError('downstream ran')):
            result = canonical('fundamental', directory, hid)
        self.assertFalse(result['downstream_executed'])
        self.assertEqual(result['status'], 'BLOCKED_EXACT_LEGACY_DUPLICATE')

    def test_restart_cannot_silently_replace_a_frozen_generation(self):
        with TemporaryDirectory() as directory:
            canonical('fundamental', directory)
            changed = sources()
            changed['fundamental']['documentary_packet']['facts']['revenue'] = '250'
            repin(changed['fundamental'])
            with patch(__name__ + '.sources', return_value=changed), self.assertRaises(ValueError):
                canonical('fundamental', directory)


class ForwardAndPortfolioTests(unittest.TestCase):
    def contract(self):
        return build_forward_contract_v2({'prospective_contract_id':'C1', 'hypothesis_id':'H1', 'generation_id':'G1',
                                         'protocol_hash':'pinned', 'readiness':'READY_AWAITING_OWNER_AUTHORITY'},
                                        t0='2026-10-16T00:00:00Z', observation_scope={'asset':'SYN'})

    def test_forward_save_reload_and_unauthorized_ingestion(self):
        registry = ForwardRegistryV2()
        registry.register(self.contract())
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'forward.json'
            registry.save(path)
            restored = ForwardRegistryV2.load(path)
            self.assertEqual(restored.snapshot(), registry.snapshot())
            for _ in range(2):
                with self.assertRaises(PermissionError):
                    restored.validate_observation_candidate('C1', {'observation_id':'O1', 'observed_at':'2026-10-17T00:00:00Z', 'scope':{'asset':'SYN'}})
            self.assertEqual(restored.snapshot()['observation_count'], 0)

    def test_forward_hash_generation_alias_and_forged_authority_rejected(self):
        registry = ForwardRegistryV2()
        contract = self.contract()
        registry.register(contract)
        mutated = deepcopy(contract)
        mutated['t0'] = '2026-10-18T00:00:00Z'
        with self.assertRaises(ValueError):
            registry.register(mutated)
        alias = self.contract()
        alias['contract_id'] = 'ALIAS'
        fields = ('contract_id','hypothesis_id','generation_id','protocol_hash','t0','observation_scope','material_change_requires_new_generation')
        alias['contract_hash'] = sha256_json({k:alias[k] for k in fields})
        with self.assertRaises(ValueError):
            registry.register(alias)
        forged = self.contract()
        forged['state'] = 'AUTHORIZED_FOR_EXACT_SCOPE'
        with self.assertRaises(PermissionError):
            ForwardRegistryV2().register(forged)

    def test_unknown_exposures_never_mean_diversification(self):
        identities = [{'hypothesis_id':hid, 'generation_id':'G1', 'payer':'UNKNOWN'} for hid in ('A','B')]
        portfolio = portfolio_diagnostics_v2(identities)
        pair = portfolio['pairwise'][0]
        self.assertEqual(pair['classification'], 'INSUFFICIENT_EVIDENCE')
        self.assertEqual(pair['overlap_score_interval'], [0.0, 1.0])
        self.assertEqual(portfolio['structural_novelty'], {'A':'UNKNOWN','B':'UNKNOWN'})
        with self.assertRaises(ValueError):
            portfolio_diagnostics_v2([identities[0], identities[0]])

    def test_shared_mechanism_and_factors_are_visible_with_identity_provenance(self):
        a = {'hypothesis_id':'A', 'generation_id':'G1', 'mechanism':'forced-sale','payer':'index-tracker',
             'asset':'SYN', 'horizon':'1d','liquidity':'thin','tail_exposure':'gap','economic_tags':['liquidity','equity_beta']}
        b = {**a, 'hypothesis_id':'B'}
        pair = portfolio_diagnostics_v2([a,b])['pairwise'][0]
        self.assertEqual(pair['classification'], 'HIGH_STRUCTURAL_OVERLAP')
        self.assertEqual(pair['structural_overlap_score'], 1.0)
        self.assertEqual(pair['identity_hashes'], [sha256_json(a),sha256_json(b)])

    def test_decay_stays_inactive_and_refuses_forged_activation(self):
        result = decay_monitor({'registrations':[]})
        self.assertEqual(result['observations_consumed'], 0)
        with self.assertRaises(RuntimeError):
            decay_monitor({'prospective_observation_authorized':True,'registrations':[{'observation_started':True}]})


if __name__ == '__main__':
    unittest.main()

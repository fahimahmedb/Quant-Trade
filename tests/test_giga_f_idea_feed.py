"""GIGA F adversarial qualification; fixture inputs, real Git CAS and Oracle leases."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import timedelta
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from research.research_os.idea_feed.contracts import seed, novelty, AUTHORITY
from research.research_os.idea_feed.registry import SeedRegistry, JOURNAL
from research.research_os.idea_feed.sources import generate, read_source
from research.research_os.idea_feed.feeder import POLICY, health, replenish, derive_request
from research.research_os.idea_feed.intake import process_policies, discovery_from_proposal
from research.research_os.expansion.v2_core import canonical_hash
from research.research_os.model_backend import BackendUnavailable
from research.research_os.github_state import PREFIX, StateConflict
from research.research_os.oracle_worker import ResearchOSWorker
from research.research_os.worker_stages import CanonicalStageExecutor
from research.research_os.tests import test_oracle_worker as worker_harness
from research.research_os.tests.test_oracle_worker import LocalStore, git, RELEASE

BASE=Path('research/research_os')
AT='2026-10-24T00:00:00Z'


def source(n=2):
    return json.loads((BASE/'sources'/f'giga_f_fixture_f{n}.json').read_text())


def draft(n=2):
    return generate(source(n),at=AT,cohort='test',budget=4)[0]


class FixtureModel:
    model='deterministic-fixture-model'
    def healthcheck(self): return {'status':'PASS','model':self.model,'runtime':'fixture'}
    def generate_structured(self,prompt,schema): return {'questions':['Could the fixture constraint be falsified?']}


class RegistryTests(unittest.TestCase):
    def test_duplicate_reordered_json_and_replay_do_not_inflate_roots(self):
        r=SeedRegistry(); p=draft(); a=r.enrol(p,AT)
        b=r.enrol(dict(reversed(list(p.items()))),AT)
        self.assertEqual(a,b); self.assertEqual(len(r.seeds()),1)
        p['source_version']='v2'; duplicate=r.enrol(p,AT)
        self.assertEqual(duplicate['state'],'DUPLICATE')
        self.assertEqual(duplicate['root_hypothesis_id'],a['root_hypothesis_id'])
        self.assertEqual(SeedRegistry(r.document()).metrics(),r.metrics())

    def test_parameter_variant_different_text_and_economic_distinctness(self):
        r=SeedRegistry(); p=draft(); a=r.enrol(p,AT)
        p['parameters']={'window':3}; b=r.enrol(p,AT)
        self.assertEqual(b['state'],'VARIANT'); self.assertEqual(a['root_hypothesis_id'],b['root_hypothesis_id'])
        p['question']='A differently worded question about the same mechanism'
        p['parameters']={}; c=r.enrol(p,AT)
        self.assertEqual(c['novelty'],'UNKNOWN_REVIEW_REQUIRED')
        self.assertNotEqual(c['root_hypothesis_id'],a['root_hypothesis_id'])
        p['actor']='different actor'; d=r.enrol(p,AT)
        self.assertEqual(d['novelty'],'ECONOMICALLY_DISTINCT')
        self.assertNotEqual(a['root_hypothesis_id'],d['root_hypothesis_id'])
        p=draft(); p['universe']='transfer universe'
        self.assertEqual(r.enrol(p,AT)['novelty'],'STRUCTURAL_TRANSFER')

    def test_unknown_mechanism_and_contamination_stay_visible_after_restart(self):
        p=draft(); p.update(mechanism_family='UNKNOWN',mechanism_state='UNKNOWN',prior_exposure_state='CONTAMINATED')
        r=SeedRegistry(); row=r.enrol(p,AT)
        self.assertEqual(row['state'],'PENDING_CONFIRMATION')
        r.expose(row['root_hypothesis_id'],'HISTORICAL_RESULT_CONSULTED','paper:known-future-result',AT,'CONTAMINATED')
        restarted=SeedRegistry(r.document()); self.assertEqual(restarted.document(),r.document())
        result=process_policies(r,cycle_id='empty',at=AT,research_decision={'action':'NO_ACTION'})
        self.assertEqual(result['proposals'],[])

    def test_outcome_authority_and_candidate_injection_are_rejected_recursively(self):
        for key in ('pnl','sharpe','candidate_id','scheduler_mutation','live_trading_authorized','effect_size','economic_pass'):
            p=draft(); p['parameters']={'nested':{key:1}}
            with self.subTest(key=key),self.assertRaises(ValueError): seed(p)

    def test_later_contamination_blocks_previously_eligible_proposals(self):
        r=SeedRegistry(); row=r.enrol(draft(),AT)
        proposals=process_policies(r,cycle_id='before-exposure',at=AT,research_decision={'action':'NO_ACTION'})['proposals']
        r.expose(row['root_hypothesis_id'],'PAPER_SEEN','future-published-result',AT,'CONTAMINATED')
        with self.assertRaisesRegex(ValueError,'CONTAMINATED'):
            discovery_from_proposal(r,proposal_id=proposals[0]['proposal_id'],research_decision={},at=AT)

    def test_variant_cannot_claim_a_new_root_or_rewrite_parent(self):
        r=SeedRegistry(); first=r.enrol(draft(),AT)
        p=draft(); p['parameters']={'threshold':2}
        variant=r.enrol(p,AT)
        self.assertEqual(variant['root_hypothesis_id'],first['root_hypothesis_id'])
        self.assertEqual(r.metrics()['fixture-F2|test']['ROOT_HYPOTHESES_ENROLLED'],1)
        forged=r.document()
        for event in forged['events']:
            if event['kind']=='SEED_ENROLLED' and event['payload']['state']=='VARIANT':
                event['payload']['root_hypothesis_id']='invented-variant-root'
        previous=None
        for event in forged['events']:
            event['previous']=previous; event.pop('event_hash')
            event['event_hash']=canonical_hash(event); previous=event['event_hash']
        forged['head']=previous
        with self.assertRaisesRegex(ValueError,'ROOT_OR_VARIANT'): SeedRegistry(forged)

        p=draft(); p['parent_seed']=first['seed']['seed_id']; p['actor']='different actor'
        with self.assertRaisesRegex(ValueError,'DISTINCT_IDENTITY'): r.enrol(p,AT)
        p=draft(); p['root_hypothesis_id']='invented-root'
        with self.assertRaisesRegex(ValueError,'SCHEMA'): r.enrol(p,AT)

    def test_bad_availability_malformed_seed_and_partial_write(self):
        malformed=source(); malformed['published_at']=123
        with self.assertRaisesRegex(ValueError,'INVALID_TIMESTAMP'):
            generate(malformed,at=AT,cohort='malformed',budget=1)
        p=draft(); p['published_at']='2026-10-25T00:00:00Z'
        with self.assertRaisesRegex(ValueError,'AVAILABILITY'): seed(p)
        p=draft(); p['extra']='untrusted'
        with self.assertRaises(ValueError): seed(p)
        r=SeedRegistry(); r.enrol(draft(),AT); broken=r.document(); broken['events'][0]['payload']['seed']['source_id']='rewritten'
        with self.assertRaises(ValueError): SeedRegistry(broken)
        broken=r.document(); broken['events']=broken['events'][:-1]
        with self.assertRaises(ValueError): SeedRegistry(broken)

    def test_blocked_unexecuted_parked_reopening_are_not_negative(self):
        r=SeedRegistry(); sid=r.enrol(draft(),AT)['seed']['seed_id']
        r.transition(sid,'BLOCKED_DATA','missing licensed data',AT)
        r.transition(sid,'PARKED_TRIGGER','await data',AT)
        with self.assertRaisesRegex(ValueError,'REOPENING'): r.transition(sid,'PENDING_CONFIRMATION','retry',AT)
        r.transition(sid,'PENDING_CONFIRMATION','data restored',AT,reopening_reason='new data version')
        with self.assertRaisesRegex(ValueError,'AUTHORITY'): r.transition(sid,'KILLED_NO_EFFECT','no permission',AT)
        self.assertEqual(next(iter(r.metrics().values()))['KILLED'],0)

    def test_existing_documentary_connector_is_hash_qualified_and_unknown_stays_unknown(self):
        from research.research_os.idea_feed.sources import documentary_origin
        raw=json.loads((BASE/'sources/sec_t1_operative_rule.json').read_text())
        origin=documentary_origin(raw,source_id='captured-sec',source_version='v1',
            family='RULE_CONSTRAINT_EVENT',origin='SETTLEMENT_RULE',observed_at=AT)
        p=generate(origin,at=AT,cohort='captured-source-test',budget=1)[0]
        self.assertEqual(p['mechanism_family'],'UNKNOWN')
        self.assertEqual(p['evidence_mode'],'DOCUMENTARY')
        raw['documentary_packet']['content_hash']='stale'
        with self.assertRaisesRegex(ValueError,'QUALIFICATION'): documentary_origin(raw,
            source_id='captured-sec',source_version='v1',family='RULE_CONSTRAINT_EVENT',
            origin='SETTLEMENT_RULE',observed_at=AT)

    def test_llm_extraction_does_not_replace_origin_or_mechanism(self):
        raw=source(2); raw['discovery_method']='LLM_DOCUMENT_EXTRACTION'
        p=generate(raw,at=AT,cohort='axis-test',budget=1)[0]
        self.assertEqual(p['origin'],'INDEX_RULE_CHANGE')
        self.assertEqual(p['discovery_method'],'LLM_DOCUMENT_EXTRACTION')
        self.assertEqual(p['mechanism_state'],'HYPOTHESIS')
        raw['seed_fields']['candidate_id']='not allowed'
        with self.assertRaises(ValueError): generate(raw,at=AT,cohort='axis-test',budget=1)

    def test_federation_all_alternatives_and_bounded_empirical_denominator(self):
        r=SeedRegistry()
        for i in range(1,8):
            for p in generate(source(i),at=AT,cohort='test',budget=4,backend=FixtureModel()): r.enrol(p,AT)
        self.assertEqual(len({x['seed']['origin_family'] for x in r.seeds().values()}),7)
        m=r.metrics()['fixture-F3|test']
        self.assertEqual(m['ROOT_HYPOTHESES_ENROLLED'],1); self.assertEqual(m['VARIANTS_ENROLLED'],3)
        self.assertEqual(m['VARIANTS_TESTED'],0)
        for row in r.metrics().values():
            self.assertNotIn('FALSE_POSITIVE_RATE',row); self.assertEqual(row['ECONOMIC_PASS'],'UNKNOWN')
        bad=source(3); bad['search']['space']['window']=list(range(100))
        with self.assertRaisesRegex(ValueError,'BUDGET'): generate(bad,at=AT,cohort='test',budget=4)
        with self.assertRaisesRegex(BackendUnavailable,'GPT_OSS_LIVE=FALSE'): generate(source(7),at=AT,cohort='test',budget=4)

    def test_policies_reused_passive_ledger_and_discovery_gate(self):
        r=SeedRegistry()
        for i in (2,7):
            for p in generate(source(i),at=AT,cohort='test',budget=4,backend=FixtureModel()): r.enrol(p,AT)
        result=process_policies(r,cycle_id='policies',at=AT,research_decision={'action':'GENERATE_MECHANISM'})
        self.assertEqual(result['cycle']['status'],'BARRIER_COMPLETE')
        self.assertEqual(len(result['proposals']),3)
        self.assertEqual(result['cycle']['candidates_created'],0)
        self.assertEqual(result,process_policies(r,cycle_id='policies',at=AT,research_decision={}))
        proposal=result['proposals'][0]
        blocked=discovery_from_proposal(r,proposal_id=proposal['proposal_id'],research_decision=proposal['disposition'],at=AT,
            engine_key='quant',source={},run_id='GIGA-F-BLOCK',synthetic_only=True,discovery_facts={})
        self.assertFalse(blocked['producer_executed'])
        # Existing producer fixture verifies the canonical RI -> Discovery path with explicit fixture evidence.
        from research.research_os.tests.test_mega_b_discovery_chain import _decision,_facts,_quant_dossier_detail
        found=discovery_from_proposal(r,proposal_id=proposal['proposal_id'],research_decision=_decision(),at=AT,
            engine_key='quant',source={'source_ref':'fixture://giga-f/discovery'},run_id='GIGA-F-DISCOVERY',
            synthetic_only=True,discovery_facts=_facts(),dossier_detail=_quant_dossier_detail())
        self.assertEqual(found['status'],'READY_FOR_FACTORY')
        self.assertTrue(found['producer_executed']); self.assertFalse(found['outcome_accessed'])
        self.assertFalse(any(found['authority'].values()))


class CanonicalWorkerFeedTests(unittest.TestCase):
    def setUp(self):
        self.h=worker_harness.WorkerTests(); self.h.setUp()
        (self.h.base/'tasks'/self.h.task['task_id'].__add__('.json')).unlink()
        self.policy=json.loads((BASE/'runtime/IDEA_FEED_POLICY.json').read_text())
        self.policy['enabled']=True
        (self.h.base/'runtime/IDEA_FEED_POLICY.json').write_text(json.dumps(self.policy))
        git(self.h.seed,'add','.'); git(self.h.seed,'commit','-m','isolated fixture source feed')
        git(self.h.seed,'push',str(self.h.remote),'HEAD:refs/heads/recovery')

    def tearDown(self): self.h.tearDown()

    def worker(self,**kwargs):
        return ResearchOSWorker(self.h.store,release_sha=RELEASE,now=lambda:self.h.now,
                                executor=CanonicalStageExecutor(FixtureModel()),**kwargs)

    def registry(self):
        with self.h.store.snapshot() as s: return SeedRegistry.load(s)

    def test_autonomous_replenishment_all_origins_restart_and_backpressure(self):
        for _ in range(7):
            admitted=self.worker().wake(); self.assertEqual(admitted['status'],'DERIVED_ONE_READY_SOURCE_TASK')
            first=self.worker(lane='evidence_data').wake(); self.assertEqual(first['stage'],'source_ingestion')
            before=len(self.registry().seeds()); self.assertGreater(before,0)
            second=self.worker(lane='evidence_data').wake(); self.assertEqual(second['stage'],'policy_intake')
            self.assertEqual(len(self.registry().seeds()),before)
        r=self.registry(); self.assertEqual(len({x['seed']['origin_family'] for x in r.seeds().values()}),7)
        restarted=LocalStore(self.h.root/'restarted-cache',self.h.remote)
        with restarted.snapshot() as s: self.assertEqual(SeedRegistry.load(s).metrics(),r.metrics())
        config=deepcopy(self.policy); config['thresholds']['max_experiment_backlog']=1
        hp=health(r,[{'status':'READY','task_type':'ECONOMIC_EXPERIMENT'}],config,AT)
        self.assertEqual(hp['action'],'BACKPRESSURE')
        config['sources']=[]
        self.assertEqual(health(SeedRegistry(),[],config,AT)['action'],'BLOCK')

    def test_concurrent_replenishment_and_seed_ingestion_use_canonical_CAS(self):
        def request():
            try: return replenish(self.h.store,'2026-10-19T10:00:00Z')['status']
            except StateConflict: return 'CONFLICT'
        with ThreadPoolExecutor(max_workers=2) as pool: list(pool.map(lambda _:request(),range(2)))
        with self.h.store.snapshot() as s:
            self.assertEqual(sum(t['status']=='READY' for t in s.tasks()),1)
        def work(i):
            try: return self.worker(worker_id='writer'+str(i),lane='evidence_data').wake()['status']
            except StateConflict: return 'CONFLICT'
        with ThreadPoolExecutor(max_workers=2) as pool: list(pool.map(work,range(2)))
        roots=[r['root_hypothesis_id'] for r in self.registry().seeds().values()]
        self.assertEqual(len(set(roots)),1)

    def test_crash_partial_append_replay_and_silent_deletion_or_attribution_rewrite(self):
        self.worker().wake()
        def fault(point):
            if point=='after_execution': raise RuntimeError('injected process death')
        with self.assertRaises(RuntimeError): self.worker(lane='evidence_data',fault=fault).wake()
        self.assertEqual(len(self.registry().seeds()),0)
        self.h.now+=timedelta(seconds=601)
        self.worker(lane='evidence_data').wake()
        before=self.registry().document()
        self.assertGreater(len(before['events']),0)
        for alteration in ('delete','source'):
            with self.h.store.snapshot() as s:
                current=SeedRegistry.load(s).document()
                if alteration=='delete': current=SeedRegistry().document()
                else:
                    # Rehashing cannot authorize rewriting immutable source attribution.
                    current['events'][0]['payload']['seed']['source_id']='malicious-source'
                with self.assertRaises(ValueError):
                    self.h.store.commit(s,{JOURNAL:current},message='forbidden history rewrite')
        self.assertEqual(self.registry().document(),before)
        self.worker(lane='evidence_data').wake()
        self.assertEqual(len(self.registry().seeds()),3)
        self.worker(lane='evidence_data').wake()
        self.assertEqual(len(self.registry().seeds()),3)

    def test_configurable_health_and_compute_budget_fail_closed(self):
        policy=deepcopy(self.policy); policy['max_compute_units_per_cohort']=0
        with self.h.store.snapshot() as snapshot:
            self.assertEqual(derive_request(snapshot,policy,AT)['status'],'NOOP_BACKPRESSURE')
            from research.research_os.idea_feed.feeder import execute_stage
            request=derive_request(snapshot,self.policy,AT)['task']
            altered=deepcopy(request)
            altered['inputs']['idea_feed_request']['source']['max_seeds_per_request']+=1
            with self.assertRaisesRegex(ValueError,'OUTSIDE_QUALIFIED_POLICY'):
                execute_stage(snapshot,altered,'source_ingestion',AT,FixtureModel())
            altered=deepcopy(request); altered['task_id']='ALTERED-TASK-IDENTITY'
            with self.assertRaisesRegex(ValueError,'TASK_IDENTITY'):
                execute_stage(snapshot,altered,'source_ingestion',AT,FixtureModel())
        for key in ('research_capacity','validation_capacity','max_unprocessed'):
            policy=deepcopy(self.policy); policy['thresholds'][key]=0
            self.assertEqual(health(SeedRegistry(),[],policy,AT)['action'],'BACKPRESSURE')
        policy=deepcopy(self.policy); policy['authority']['outcome_accessed']=True
        with self.h.store.snapshot() as snapshot,self.assertRaisesRegex(ValueError,'AUTHORITY'):
            derive_request(snapshot,policy,AT)

    def test_stale_completion_and_source_timeout_retry_exhaustion(self):
        self.worker().wake()
        def advance(point):
            if point=='after_execution': self.h.now+=timedelta(seconds=601)
        with self.assertRaisesRegex(StateConflict,'LEASE_EXPIRED'):
            self.worker(lane='evidence_data',fault=advance).wake()
        self.assertEqual(len(self.registry().seeds()),0)
        with patch('research.research_os.idea_feed.feeder.generate',side_effect=BackendUnavailable('SOURCE_TIMEOUT')):
            for _ in range(3):
                result=self.worker(lane='evidence_data').wake(); self.h.now+=timedelta(minutes=6)
        self.assertEqual(result['status'],'BLOCKED')
        self.assertEqual(len(self.registry().seeds()),0)

    def test_unavailable_timeout_and_stale_source_are_explicit(self):
        with self.h.store.snapshot() as s:
            descriptor=self.policy['sources'][0]
            bad=deepcopy(descriptor); bad['content_hash']='stale'
            with self.assertRaisesRegex(ValueError,'STALE'): read_source(s,bad)
            bad=deepcopy(descriptor); bad['path']=PREFIX+'sources/missing.json'
            with self.assertRaisesRegex(BackendUnavailable,'SOURCE_UNAVAILABLE'): read_source(s,bad)
        self.worker().wake()
        with patch('research.research_os.idea_feed.feeder.generate',side_effect=BackendUnavailable('SOURCE_TIMEOUT')):
            result=self.worker(lane='evidence_data').wake()
        self.assertEqual(result['status'],'READY')
        self.assertEqual(len(self.registry().seeds()),0)
        self.h.now+=timedelta(minutes=6)
        self.worker(lane='evidence_data').wake()
        self.assertEqual(len(self.registry().seeds()),3)


if __name__=='__main__': unittest.main()

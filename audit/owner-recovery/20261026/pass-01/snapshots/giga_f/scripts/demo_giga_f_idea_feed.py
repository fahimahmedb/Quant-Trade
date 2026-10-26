#!/usr/bin/env python3
"""Deterministic GIGA F demonstration using disposable real Git remote + Oracle.

No market evidence, external feed, model runtime or economic test is claimed.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'src')]

from research.research_os.tests import test_oracle_worker as harness
from research.research_os.tests.test_mega_b_discovery_chain import _decision, _facts, _quant_dossier_detail
from research.research_os.idea_feed.contracts import AUTHORITY
from research.research_os.idea_feed.registry import SeedRegistry, JOURNAL
from research.research_os.idea_feed.feeder import POLICY, health
from research.research_os.idea_feed.intake import process_policies, discovery_from_proposal
from research.research_os.oracle_worker import ResearchOSWorker
from research.research_os.worker_stages import CanonicalStageExecutor


class FixtureModel:
    model='deterministic-fixture-model'
    def healthcheck(self): return {'status':'PASS','runtime':'fixture','model':self.model}
    def generate_structured(self,prompt,schema):
        return {'questions':['Can an alternative fixture-only mechanism explanation be falsified?']}


def demonstrate():
    h=harness.WorkerTests(); h.setUp()
    try:
        (h.base/'tasks'/f'{h.task["task_id"]}.json').unlink()
        policy=json.loads((h.base/'runtime/IDEA_FEED_POLICY.json').read_text()); policy['enabled']=True
        (h.base/'runtime/IDEA_FEED_POLICY.json').write_text(json.dumps(policy))
        harness.git(h.seed,'add','.'); harness.git(h.seed,'commit','-m','isolated deterministic feed configuration')
        harness.git(h.seed,'push',str(h.remote),'HEAD:refs/heads/recovery')
        def worker(lane='auto', fault=None):
            return ResearchOSWorker(h.store,release_sha=harness.RELEASE,lane=lane,now=lambda:h.now,
                executor=CanonicalStageExecutor(FixtureModel()),fault=fault)
        trace=[]
        for _ in range(7):
            admission=worker().wake(); assert admission['status']=='DERIVED_ONE_READY_SOURCE_TASK',admission
            first=worker('evidence_data').wake(); assert first['stage']=='source_ingestion'
            with h.store.snapshot() as snapshot:
                registry=SeedRegistry.load(snapshot)
                assert registry.seeds()
                assert not any(e['key']=='cycle:'+admission['task']['task_id'] for e in registry.events)
            second=worker('evidence_data').wake(); assert second['stage']=='policy_intake'
            trace.append({'source_id':admission['task']['inputs']['idea_feed_request']['source']['source_id'],
                          'ingestion_status':first['status'],'intake_status':second['status'],
                          'enrolled_before_selection':len(registry.seeds())})
        at=h.now.isoformat().replace('+00:00','Z')
        with h.store.snapshot() as snapshot:
            registry=SeedRegistry.load(snapshot)
            duplicate=deepcopy(next(r['seed'] for r in registry.seeds().values() if r['seed']['source_id']=='fixture-F2'))
            duplicate.pop('seed_id'); duplicate['source_version']='duplicate-fixture-v2'
            assert registry.enrol(duplicate,at)['state']=='DUPLICATE'
            cycle=process_policies(registry,cycle_id='GIGA-F-DEMO-SHARED',at=at,
                                   research_decision={'action':'GENERATE_MECHANISM'})
            assert len(cycle['proposals'])==3
            chosen=cycle['proposals'][0]
            blocked=discovery_from_proposal(registry,proposal_id=chosen['proposal_id'],
                research_decision=chosen['disposition'],at=at,engine_key='quant',source={},
                run_id='GIGA-F-DEMO-DENIED',synthetic_only=True,discovery_facts={})
            assert not blocked['producer_executed']
            # Qualified RI decision is a labeled deterministic test fixture, never source authority.
            result=discovery_from_proposal(registry,proposal_id=chosen['proposal_id'],
                research_decision=_decision(),at=at,selected_seed_refs=[chosen['seed_refs'][0]],
                engine_key='quant',source={'source_ref':'fixture://giga-f/existing-discovery'},
                run_id='GIGA-F-DEMO-CANDIDATE',synthetic_only=True,discovery_facts=_facts(),
                dossier_detail=_quant_dossier_detail())
            assert result['producer_executed'] and result['status']=='READY_FOR_FACTORY'
            assert not result['outcome_accessed'] and not any(result['authority'].values())
            h.store.commit(snapshot,{JOURNAL:registry.document()},message='Deterministic fixture duplicate and Discovery lineage')
        restarted=harness.LocalStore(h.root/'restart-cache',h.remote)
        with restarted.snapshot() as snapshot:
            after=SeedRegistry.load(snapshot)
            assert after.document()==registry.document()
            assert after.metrics()==registry.metrics()
        saturated=deepcopy(policy); saturated['thresholds']['max_experiment_backlog']=1
        pressure=health(after,[{'status':'READY','task_type':'ECONOMIC_EXPERIMENT'}],saturated,at)
        assert pressure['action']=='BACKPRESSURE'
        return {'evidence_scope':'DETERMINISTIC_FIXTURES_REAL_LOCAL_GIT_CAS',
            'market_evidence':False,'external_runtime_present':False,'GPT_OSS_LIVE':False,
            'model_blocker':'NO_EXTERNAL_LOCAL_RUNTIME_CONFIGURED; demonstration uses explicit test double',
            'origins':sorted({r['seed']['origin_family'] for r in after.seeds().values()}),
            'enrolled_seeds':len(after.seeds()),'root_hypotheses':len({r['root_hypothesis_id'] for r in after.seeds().values()}),
            'source_trace':trace,'source_yield_by_cohort':after.metrics(),
            'policies':cycle['cycle']['terminal_statuses'],'proposals':len(cycle['proposals']),
            'source_adapter_candidates_created':0,'canonical_discovery_status':result['status'],
            'unqualified_discovery_blocked':not blocked['producer_executed'],
            'autonomous_replenishment':True,'backpressure':pressure['action'],
            'restart_denominator_preserved':True,'journal_event_count':len(after.events),
            'authority':AUTHORITY}
    finally: h.tearDown()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--output',type=Path)
    args=parser.parse_args(); receipt=demonstrate(); encoded=json.dumps(receipt,indent=2,sort_keys=True)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(encoded)
    print(encoded,end='')

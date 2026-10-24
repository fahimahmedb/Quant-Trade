"""Frontier health and bounded source-work derivation for the EXISTING Oracle.

No timers, worker creation, leases or queue implementation live here. Oracle
owns admission; source execution is an ordinary fenced canonical worker stage.
"""
from collections import Counter
from copy import deepcopy

from ..github_state import PREFIX
from ..expansion.v2_core import canonical_hash
from ..model_backend import BackendUnavailable
from .contracts import AUTHORITY, clock
from .registry import SeedRegistry, JOURNAL
from .sources import read_source, generate
from .intake import process_policies

POLICY=PREFIX+'runtime/IDEA_FEED_POLICY.json'


def health(registry, tasks, policy, at):
    limits=policy['thresholds']
    for k in ('eligible_target','max_unprocessed','max_discovery_backlog','max_candidate_backlog',
              'max_experiment_backlog','research_capacity','validation_capacity','max_age_seconds',
              'min_source_diversity','min_mechanism_diversity'):
        if type(limits.get(k)) is not int or limits[k]<0: raise ValueError('INVALID_FRONTIER_THRESHOLD:'+k)
    if not 0<=limits['max_blocked_fraction']<=1 or not 0<=limits['max_duplicate_fraction']<=1:
        raise ValueError('INVALID_FRONTIER_FRACTION')
    seeds=registry.seeds(); states=registry.states()
    eligible=[r for sid,r in seeds.items() if states[sid] in {'SEED_REGISTERED','VARIANT'}
              and registry.exposure_state(r['root_hypothesis_id'])!='CONTAMINATED']
    processed={sid for row in registry.proposals().snapshot() for sid in row['seed_refs']}
    unprocessed=[r for r in eligible if r['seed']['seed_id'] not in processed]
    active=[t for t in tasks if t.get('status') in {'READY','CLAIMED'}]
    counts=Counter(t.get('task_type') for t in active)
    n=max(len(seeds),1)
    blocked=sum(s.startswith('BLOCKED') for s in states.values())/n
    duplicate=sum(r['state']=='DUPLICATE' for r in seeds.values())/n
    oldest=max(((clock(at)-clock(r['seed']['first_observed_at'])).total_seconds() for r in unprocessed),default=0)
    observation={'eligible_seeds':len(unprocessed),'unprocessed_seeds':len(seeds)-len(processed),
        'discovery_backlog':sum(counts[k] for k in ('QUANT_MECHANISM','EVENT_DOCUMENT','FUNDAMENTAL_RESEARCH','INSTITUTIONAL_FLOW')),
        'candidate_backlog':counts['VALIDATION']+counts['RED_TEAM'],'experiment_backlog':counts['ECONOMIC_EXPERIMENT'],
        'source_diversity':len({r['seed']['origin_family'] for r in unprocessed}),
        'mechanism_diversity':len({r['seed']['mechanism_family'] for r in unprocessed}-{'UNKNOWN'}),
        'oldest_seconds':oldest,'blocked_fraction':blocked,'duplicate_fraction':duplicate,
        'research_capacity':limits['research_capacity'],'validation_capacity':limits['validation_capacity'],
        'active_source_work':sum(bool(t.get('inputs',{}).get('idea_feed_request')) for t in active)}
    reasons=[]
    for value,limit in (('unprocessed_seeds','max_unprocessed'),('discovery_backlog','max_discovery_backlog'),
                        ('candidate_backlog','max_candidate_backlog'),('experiment_backlog','max_experiment_backlog')):
        if observation[value]>=limits[limit]: reasons.append(limit)
    if duplicate>limits['max_duplicate_fraction']: reasons.append('DUPLICATE_RATE')
    if not limits['research_capacity'] or not limits['validation_capacity']: reasons.append('INDEPENDENT_RESEARCH_CAPACITY')
    if reasons: action='BACKPRESSURE'
    elif not policy.get('sources'): action='BLOCK'; reasons=['ZERO_ADMISSIBLE_SOURCES']
    elif blocked>limits['max_blocked_fraction']: action='BLOCK'; reasons=['BLOCKED_FRACTION_REQUIRES_REPAIR']
    elif observation['active_source_work']: action='HOLD'; reasons=['SOURCE_WORK_ALREADY_ADMITTED']
    elif (len(unprocessed)<limits['eligible_target'] or observation['source_diversity']<limits['min_source_diversity']
          or observation['mechanism_diversity']<limits['min_mechanism_diversity'] or oldest>limits['max_age_seconds']):
        action='REPLENISH'; reasons=['FRONTIER_COVERAGE_OR_AGE']
    else: action='HOLD'; reasons=['HEALTHY_FRONTIER']
    return {'action':action,'reasons':reasons,'observation':observation,'thresholds':deepcopy(limits),
            'source_productivity':'UNKNOWN','authority':deepcopy(AUTHORITY)}


def derive_request(snapshot, policy, at):
    if policy.get('authority')!=AUTHORITY: raise ValueError('FEED_AUTHORITY_MUST_REMAIN_CLOSED')
    if policy.get('max_requests_per_wake')!=1 or policy.get('minimum_exploration_allocation')!=1:
        raise ValueError('BOUNDED_EXPLORATION_POLICY_REQUIRED')
    registry=SeedRegistry.load(snapshot)
    frontier=health(registry,snapshot.tasks(),policy,at)
    if frontier['action']!='REPLENISH':
        return {'status':'NOOP_BACKPRESSURE' if frontier['action']=='BACKPRESSURE' else frontier['action'],
                'frontier':frontier,'task':None}
    cohort=policy['cohort']; used=Counter()
    for e in registry.events:
        if e['kind']=='SOURCE_WORK_COMPLETED' and e['payload']['cohort']==cohort:
            used[e['payload']['source_id']]+=e['payload']['budget_charged']
    compute_limit=policy['max_compute_units_per_cohort']
    if type(compute_limit) is not int or compute_limit<0: raise ValueError('INVALID_COMPUTE_BUDGET')
    if sum(used.values())>=compute_limit:
        return {'status':'NOOP_BACKPRESSURE','frontier':frontier,'task':None,'reason':'COMPUTE_BUDGET_REACHED'}
    candidates=[]
    for source in policy['sources']:
        budget=source['budget']
        if type(budget) is not int or budget<1: raise ValueError('INVALID_SOURCE_BUDGET')
        charge=source['max_seeds_per_request']
        if type(charge) is not int or charge<1 or charge>budget: raise ValueError('INVALID_SOURCE_REQUEST_BOUND')
        if sum(used.values())+charge>compute_limit: continue
        if used[source['source_id']]+charge>budget: continue
        if any(t.get('inputs',{}).get('idea_feed_request',{}).get('source')==source
               and t.get('inputs',{}).get('idea_feed_request',{}).get('cohort')==cohort for t in snapshot.tasks()):
            continue  # Retries belong to the same canonical task, not a fresh hidden trial.
        if source['path'] not in snapshot.blobs: continue
        candidates.append(source)
    if not candidates: return {'status':'BLOCK','frontier':frontier,'task':None,'reason':'SOURCE_BUDGET_OR_AVAILABILITY_EXHAUSTED'}
    # Minimum exploration over all admissible sources, no historical performance allocation.
    selected=min(candidates,key=lambda s:(used[s['source_id']],s['source_id']))
    source=read_source(snapshot,selected,at)
    if source['source_id']!=selected['source_id'] or source['source_version']!=selected['source_version']:
        raise ValueError('STALE_SOURCE_VERSION_OR_IDENTITY')
    request={'cohort':cohort,'source':deepcopy(selected),'policy_hash':canonical_hash(policy),
             'frontier_hash':canonical_hash(frontier)}
    key=canonical_hash({'cohort':cohort,'source':selected,'policy':canonical_hash(policy)})
    task={'task_id':'IDEA-FEED-'+key[:24],'task_type':'SOURCE_QUALIFICATION','required_capability':'source_qualification',
        'status':'READY','priority':policy['priority'],'inputs':{'idea_feed_request':request},
        'allowed_actions':['source_ingestion','policy_intake'],
        'forbidden_actions':['economic outcomes','candidate creation','capital allocation','live trading'],
        'success_condition':'Register all bounded seeds before passive policy intake',
        'authority':{k:v for k,v in AUTHORITY.items() if k!='outcome_accessed'},
        'lease':{'generation':0,'owner':None,'claimed_at':None,'expires_at':None},'created_at':at}
    return {'status':'DERIVED_ONE_READY_SOURCE_TASK','task':task,'frontier':frontier}


def replenish(store, at):
    with store.snapshot() as snapshot:
        if POLICY not in snapshot.blobs: return None
        policy=snapshot.read(POLICY)
        if policy.get('enabled') is not True: return None
        try:
            result=derive_request(snapshot,policy,at)
        except (ValueError, KeyError, TypeError, BackendUnavailable) as exc:
            result={'status':'BLOCK','task':None,'reason':str(exc),'authority':deepcopy(AUTHORITY)}
        if result['task'] is None: return result
        task=result['task']; path=PREFIX+'tasks/'+task['task_id']+'.json'
        receipt=PREFIX+'receipts/idea-feed/'+task['task_id']+'.json'
        commit=store.commit(snapshot,{path:task,receipt:result},create_only=[path,receipt],
                            message='Bounded canonical idea-source replenishment')
        return {**result,'output_commit':commit}


def execute_stage(snapshot, task, stage, at, backend):
    request=task['inputs']['idea_feed_request']; policy=snapshot.read(POLICY)
    if canonical_hash(policy)!=request['policy_hash']: raise ValueError('STALE_SOURCE_POLICY')
    registry=SeedRegistry.load(snapshot)
    if stage=='source_ingestion':
        state=health(registry,[t for t in snapshot.tasks() if t['task_id']!=task['task_id']],policy,at)
        if state['action'] in {'BACKPRESSURE','BLOCK'}:
            return {'status':'NOOP_BACKPRESSURE','frontier':state},{},'COMPLETE'
        descriptor=request['source']; source=read_source(snapshot,descriptor,at)
        if source['source_version']!=descriptor['source_version'] or source['source_id']!=descriptor['source_id']:
            raise ValueError('STALE_SOURCE_VERSION_OR_IDENTITY')
        drafts=generate(source,at=at,cohort=request['cohort'],budget=descriptor['max_seeds_per_request'],backend=backend)
        if len(drafts)>descriptor['max_seeds_per_request']: raise ValueError('SOURCE_BUDGET_EXCEEDED')
        enrolled=[]
        for draft in drafts:
            row=registry.enrol(draft,at); enrolled.append(row['seed']['seed_id'])
            if draft['origin_family']=='MODEL_ASSISTED':
                prompt_ref=next(x for x in draft['uncertainty'] if x.startswith('PROMPT_HASH:'))
                registry.expose(row['root_hypothesis_id'],'MODEL_PROMPT',prompt_ref,at,
                    model_identity=getattr(backend,'model',type(backend).__name__),prompt_agent_family='idea-origin-v1')
        registry.append('SOURCE_WORK_COMPLETED',{'source_id':source['source_id'],'cohort':request['cohort'],
                        'budget_charged':descriptor['max_seeds_per_request'],'seed_refs':enrolled},at,
                        'source-work:'+task['task_id'])
        return {'status':'SEEDS_REGISTERED_BEFORE_SELECTION','seed_refs':enrolled},{JOURNAL:registry.document()},'CONTINUE'
    if stage=='policy_intake':
        if not any(e['key']=='source-work:'+task['task_id'] for e in registry.events):
            raise ValueError('SEEDS_MUST_BE_DURABLE_BEFORE_SELECTION')
        from ..research_intelligence import decide_candidate
        rows=list(registry.seeds().values())
        focal=rows[-1]; s=focal['seed']
        capabilities=snapshot.read(PREFIX+'runtime/CAPABILITY_REGISTRY.json')
        lanes=snapshot.read(PREFIX+'runtime/WORKFLOW_LANES.json')
        # RI consumes a research-question identity, not a canonical Candidate.
        decision=decide_candidate({'hypothesis_id':focal['root_hypothesis_id'],
            'identity':{'mechanism':s['mechanism_family'],'payer':s['possible_payer'],
                'constrained_actor':s['actor'],'timing_clock':s['clock'],'universe':s['universe'],
                'source_family':s['origin_family'],'evidence_identity':s['evidence_refs'][0]},
            'actions':[{'action':'ARCHAEOLOGY_LOOKUP','cost_units':0,'depth':'WIDE','is_falsifier':True}]},
            capability_registry=capabilities,workflow_lanes=lanes,
            authority={k:v for k,v in AUTHORITY.items() if k!='outcome_accessed'})
        result=process_policies(registry,cycle_id=task['task_id'],at=at,research_decision=decision,
            context={'capabilities':capabilities,'tasks':snapshot.tasks(),
                     'frontier':health(registry,snapshot.tasks(),policy,at)})
        return {'status':'PASSIVE_POLICIES_COMPLETE','cycle':result['cycle']},{JOURNAL:registry.document()},'COMPLETE'
    raise ValueError('UNSUPPORTED_FEED_STAGE')

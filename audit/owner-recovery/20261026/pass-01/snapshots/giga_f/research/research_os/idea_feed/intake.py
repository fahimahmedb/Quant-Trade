"""Seed registry -> existing A/B/C -> existing Proposal Ledger -> Discovery membrane."""
from copy import deepcopy

from ..expansion.v2_core import canonical_hash
from ..multi_source_ideation import build_context_snapshot, policy_a, policy_b
from ..multi_source_ideation_hardening import proposal_identity, qualify_for_discovery
from ..policy_c_safe import safe_policy_c
from ..ideation_cycle import raw_proposal_receipt, ideation_cycle
from ..discovery_chain import run_discovery_chain
from ..multi_source_ideation_bindings import information_value_from_research_intelligence
from .contracts import AUTHORITY


class RegisteredModelQuestions:
    """Policy C sees all already-enrolled alternatives; it cannot invent hidden roots."""
    backend_identity='registered-model-commentary'
    model_identity='registered-source-model'
    def __init__(self, rows): self.rows=rows
    def generate(self, mandate):
        return {'alternatives':[{'summary':r['seed']['question'],'seed_ref':r['seed']['seed_id']}
                                for r in self.rows[:5]],
                'selected_alternative_index':0,'selection_criteria':'DECLARED_ORDER_NO_OUTCOMES'}


def process_policies(registry, *, cycle_id, at, research_decision, context=None):
    prior=next((e for e in registry.events if e['key']=='cycle:'+cycle_id),None)
    if prior: return deepcopy(prior['payload'])
    rows=[r for sid,r in sorted(registry.seeds().items())
          if registry.states()[sid] in {'SEED_REGISTERED','VARIANT'}
          and registry.exposure_state(r['root_hypothesis_id'])!='CONTAMINATED']
    context=context or {}
    views={
        'memory_snapshot_ref':{'scope':'SEED_REGISTRY_EXPOSURE_ONLY','states':registry.states(),
            'exposures':[e for e in registry.events if e['kind']=='RESEARCH_EXPOSURE']},
        'ancestry_snapshot_ref':{sid:{k:r[k] for k in ('root_hypothesis_id','parent_seed','match','novelty')}
                                 for sid,r in registry.seeds().items()},
        'frontier_snapshot_ref':context.get('frontier',{'scope':'REGISTERED_QUESTIONS','eligible':len(rows)}),
        'evidence_snapshot_ref':{sid:r['seed']['evidence_refs'] for sid,r in registry.seeds().items()},
        'source_catalog_snapshot_ref':{sid:r['seed'] for sid,r in registry.seeds().items()},
        'capability_snapshot_ref':context.get('capabilities',{'status':'UNKNOWN_NOT_PROVIDED'}),
        'authority_snapshot_ref':AUTHORITY,
        'active_work_snapshot_ref':context.get('tasks',{'status':'UNKNOWN_NOT_PROVIDED'})}
    refs={k:canonical_hash(v) for k,v in views.items()}
    snapshot=build_context_snapshot(ideation_cycle_id=cycle_id,created_at=at,refs=refs,
                                   relevant_schema_versions={'idea_seed':'v1'})
    h=snapshot['context_snapshot_hash']
    a=policy_a(snapshot=snapshot,frontier_decision={'action':'GENERATE_MECHANISM','executable':bool(rows)},
               source_plan={'status':'SOURCE_SELECTED','source_identity':rows[0]['seed']['seed_id']} if rows else None)
    if 'executable' in research_decision:
        b=information_value_from_research_intelligence(snapshot=snapshot,decision=research_decision)
        # The canonical RI binding names its question handle candidate_id.
        # Keep that correlation passive under the Proposal Ledger firewall.
        if b['artifact_kind']:
            b['payload']['research_question_ref']=b['payload'].pop('candidate_id',None)
    else:
        b=policy_b(snapshot=snapshot,research_decision=research_decision)
    models=[r for r in rows if r['seed']['origin_family']=='MODEL_ASSISTED']
    c,model_receipt=safe_policy_c(snapshot=snapshot,backend=RegisteredModelQuestions(models) if models else None,
        mandate={'prompt_contract_version':'registered-seeds-only-v1','seed_registry_ref':refs['source_catalog_snapshot_ref']})
    artifacts=[a,b,c]
    eligible_ids={r['seed']['seed_id'] for r in rows}
    for artifact in artifacts:
        if artifact['artifact_kind']:
            artifact['payload']['registered_seed_refs']=sorted(eligible_ids)
    receipts=[raw_proposal_receipt(cycle_id=cycle_id,artifact=x,
                provenance={'seed_registry_head':registry.document()['head'],'source_kind':'FEDERATED_ORIGINS'}) for x in artifacts]
    cycle=ideation_cycle(cycle_id=cycle_id,context_snapshot=snapshot,artifacts=artifacts,receipts=receipts)
    ledger=registry.proposals()
    proposals=[]
    for artifact in artifacts:
        if not artifact['artifact_kind']: continue
        identity=proposal_identity(policy_kind=artifact['policy_kind'],context_snapshot_hash=h,
            payload=artifact['payload'],provenance={'registry_ref':refs['source_catalog_snapshot_ref']})
        disposition=qualify_for_discovery(proposal=artifact,context_snapshot_hash=h,
            memory={'classification':'UNKNOWN'},duplicate={'classification':'UNKNOWN'},implementability={'admissible':False})
        # Existing seed intake explicitly permits synthesis; it does not assert novelty/mechanism proof.
        if not eligible_ids: disposition={'eligible_for_discovery':False,'decision':'BLOCKED'}
        row={'proposal_id':identity['proposal_id'],'status':'ELIGIBLE_FOR_DISCOVERY' if disposition['eligible_for_discovery'] else disposition['decision'],
             'artifact':artifact,'context_snapshot_hash':h,'seed_refs':sorted(eligible_ids),
             'disposition':disposition,'scientific_verdict':'NOT_PERFORMED','economic_result':'NOT_OBSERVED','outcome_accessed':False}
        ledger.persist(row); proposals.append(row)
    result={'context':snapshot,'context_views':views,'cycle':cycle,'proposals':proposals,'model_receipt':model_receipt,
            'registered_seed_count':len(registry.seeds()),'gpt_oss_live':False,
            'model_blocker':'EXTERNAL_RUNTIME_NOT_CONFIGURED_OR_NOT_QUALIFIED'}
    registry.append('POLICY_CYCLE',result,at,'cycle:'+cycle_id)
    return result


def discovery_from_proposal(registry, *, proposal_id, research_decision, at, selected_seed_refs=None, **kwargs):
    row=next(r for r in registry.proposals().snapshot() if r['proposal_id']==proposal_id)
    if row['status']!='ELIGIBLE_FOR_DISCOVERY' or not row['seed_refs']:
        raise ValueError('PROPOSAL_NOT_ELIGIBLE')
    selected=selected_seed_refs or row['seed_refs']
    if not selected or not set(selected)<=set(row['seed_refs']):
        raise ValueError('DISCOVERY_SEED_SELECTION_OUTSIDE_PROPOSAL')
    if any(sid not in registry.seeds() for sid in row['seed_refs']):
        raise ValueError('UNREGISTERED_DISCOVERY_INPUT')
    if any(registry.exposure_state(registry.seeds()[sid]['root_hypothesis_id'])=='CONTAMINATED'
           or registry.states()[sid] not in {'SEED_REGISTERED','VARIANT'} for sid in row['seed_refs']):
        raise ValueError('STALE_OR_CONTAMINATED_PROPOSAL_REQUIRES_REQUALIFICATION')
    # No conversion of eligibility into RUN_PRODUCER: canonical RI gate stays intact.
    result=run_discovery_chain(research_decision,**kwargs)
    # Technical lineage only. No scientific verdict or outcome is imported.
    from ..scientific_store import sha256_json
    candidate=result.get('candidate')
    receipt={'proposal_id':proposal_id,'seed_refs':sorted(set(selected)),
             'status':result['status'],'candidate_hash':sha256_json(candidate) if candidate else None,
             'producer_executed':result['producer_executed'],'result_ref':canonical_hash(result)}
    registry.append('DISCOVERY_RECEIPT',receipt,at,'discovery:'+proposal_id+':'+kwargs['run_id'])
    return result

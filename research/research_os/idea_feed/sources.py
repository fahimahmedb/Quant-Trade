"""Seven question origins. Observation != edge; model commentary != evidence.

Readers consume pinned canonical packets; network acquisition remains in the
existing data/source qualification plane. No feed is simulated as external live data.
"""
from copy import deepcopy
import itertools
import json

from ..expansion.v2_core import canonical_hash
from ..github_state import PREFIX
from ..model_backend import BackendUnavailable, validate_structure
from .contracts import REQUIRED, FAMILIES, bounded, clock

QUESTIONS = {
 'REPLICATION': 'Can the external claim be {mode} under PIT reconstruction and realistic costs?',
 'RULE_CONSTRAINT_EVENT': 'Who may have to act under the observed rule, why, when, on what, under which constraint, and who may take the other side?',
 'BOUNDED_EMPIRICAL': 'Does the predeclared relation survive falsification within the declared search domain?',
 'FUNDAMENTAL_DOCUMENT': 'Does the documented change imply an expectation mismatch after identity, revision and availability reconstruction?',
 'INSTRUMENT_RELATIONSHIP': 'Does the contractual relationship explain the spread after financing, timing and implementation constraints?',
 'RISK_TRANSFER': 'Who demands immediacy, insurance, financing or hedging, and could compensation survive costs and capacity constraints?',
}
CLAIM_STATES = {'REPLICATION':'UNVERIFIED_EXTERNAL_CLAIM','RULE_CONSTRAINT_EVENT':'RULE_EXISTS_NOT_FORCED_FLOW',
 'BOUNDED_EMPIRICAL':'UNEXECUTED_SEARCH_PLAN','FUNDAMENTAL_DOCUMENT':'DOCUMENT_CHANGE_NOT_EDGE',
 'INSTRUMENT_RELATIONSHIP':'SPREAD_NOT_ARBITRAGE','RISK_TRANSFER':'RISK_PREMIUM_NOT_ALPHA',
 'MODEL_ASSISTED':'UNVERIFIED_MODEL_COMMENTARY'}
MODEL_SCHEMA={'type':'object','additionalProperties':False,'required':['questions'],'properties':{
 'questions':{'type':'array','minItems':1,'maxItems':5,'items':{'type':'string','minLength':1,'maxLength':1000}}}}


def read_source(snapshot, descriptor, at=None):
    path=descriptor['path']
    if not path.startswith(PREFIX+'sources/') or '..' in path.split('/'):
        raise ValueError('SOURCE_PATH_OUTSIDE_CANONICAL_PACKETS')
    if path not in snapshot.blobs: raise BackendUnavailable('SOURCE_UNAVAILABLE:'+path)
    raw=snapshot.read(path)
    if canonical_hash(raw)!=descriptor['content_hash']:
        raise ValueError('STALE_SOURCE_VERSION_OR_CONTENT')
    if descriptor.get('format')=='QUALIFIED_DOCUMENTARY':
        if not at: raise ValueError('DOCUMENTARY_OBSERVATION_CLOCK_REQUIRED')
        return documentary_origin(raw,source_id=descriptor['source_id'],source_version=descriptor['source_version'],
            family=descriptor['origin_family'],origin=descriptor['origin'],observed_at=at)
    return raw


def documentary_origin(packet, *, source_id, source_version, family, origin, observed_at):
    """Connector onto existing qualified documentary packets, without a second collector."""
    documentary=packet.get('documentary_packet', packet)
    if documentary.get('evidence_class')!='DOCUMENTARY':
        raise ValueError('DOCUMENTARY_CLASS_REQUIRED')
    from ..expansion.engine_dossiers_v1 import qualify_document_packet
    routes={'RULE_CONSTRAINT_EVENT':'INSTITUTIONAL_FLOW','FUNDAMENTAL_DOCUMENT':'FUNDAMENTAL'}
    if family not in routes: raise ValueError('UNSUPPORTED_DOCUMENTARY_FAMILY')
    qualification=qualify_document_packet(documentary,routes[family],observed_at)
    if qualification['status']!='PASS': raise ValueError('DOCUMENTARY_QUALIFICATION_FAILED')
    if not documentary.get('content_hash') or not documentary.get('available_at'):
        raise ValueError('QUALIFIED_DOCUMENTARY_PACKET_REQUIRED')
    published=documentary.get('published_at')
    if not published: raise ValueError('PUBLICATION_PROVENANCE_REQUIRED')
    return {'source_id':source_id,'source_version':source_version,'published_at':published,
            'available_at':documentary['available_at'],'origin_family':family,'origin':origin,
            'discovery_method':'DOCUMENT_EXTRACTION','evidence_mode':'DOCUMENTARY',
            'observation_ref':documentary['content_hash'],'observed_at':observed_at,'seed_fields':{}}


def generate(source, *, at, cohort, budget, backend=None):
    if not isinstance(source, dict): raise ValueError('MALFORMED_SOURCE_PAYLOAD')
    bounded(source)
    family=source.get('origin_family')
    if family not in FAMILIES or type(budget) is not int or budget<1:
        raise ValueError('INVALID_SOURCE_FAMILY_OR_BUDGET')
    if not clock(source['published_at']) <= clock(source['available_at']) <= clock(at):
        raise ValueError('SOURCE_AVAILABILITY_CONTRADICTION')
    if source.get('observed_at') and clock(source['observed_at'])>clock(at):
        raise ValueError('SOURCE_OBSERVATION_IN_FUTURE')
    if not source.get('observation_ref'): raise ValueError('SOURCE_OBSERVATION_REQUIRED')
    fields=source.get('seed_fields',{})
    writable={'mechanism_family','mechanism_state','universe','instruments','clock','horizon',
              'actor','constraint','possible_payer','possible_transfer','cost_concerns','capacity_concerns',
              'information_source','rule_structure','expected_direction','alternative_explanations',
              'uncertainty','required_data','question','prior_exposure_state','search_family'}
    if not isinstance(fields,dict) or set(fields)-writable: raise ValueError('SOURCE_FIELD_AUTHORITY_VIOLATION')
    p={k:'UNKNOWN' for k in REQUIRED}
    p.update({k:source[k] for k in ('source_id','source_version','published_at','available_at',
                                  'origin_family','origin','discovery_method','evidence_mode')})
    p.update(first_observed_at=at,evidence_refs=[source['observation_ref']],
             instruments=[],alternative_explanations=['UNKNOWN'],uncertainty=[CLAIM_STATES[family]],
             required_data=['PIT reconstruction','independent validation','cost and capacity observations'],
             cost_concerns=['UNKNOWN'],capacity_concerns=['UNKNOWN'],lineage=[],parent_seed=None,
             reopening_reason=None,cohort=cohort,research_budget=budget,search_family=source['source_id'],
             parameters={},mechanism_state='UNKNOWN',prior_exposure_state='UNKNOWN')
    p.update(deepcopy(fields))
    p['uncertainty']=list(dict.fromkeys(p['uncertainty']+[CLAIM_STATES[family]]))
    if family=='REPLICATION':
        modes=source.get('claim_questions',['reproduced','falsified','transferred','tested in a different period',
                                          'reconstructed point in time','challenged on costs','challenged on mechanism survival'])
        if not isinstance(modes,list) or not modes or len(modes)>budget:
            raise ValueError('CLAIM_QUESTION_BUDGET_EXCEEDED')
        return [{**deepcopy(p),'question':QUESTIONS[family].format(mode=str(mode)),
                 'parameters':{'claim_test':mode},'prior_exposure_state':'KNOWN_EXPOSURE'} for mode in modes]
    if family=='BOUNDED_EMPIRICAL':
        plan=source.get('search',{})
        if not plan.get('domain') or not plan.get('stop_condition') or not plan.get('family'):
            raise ValueError('DECLARED_SEARCH_DOMAIN_AND_STOP_REQUIRED')
        axes=plan.get('space')
        if not isinstance(axes,dict) or not axes or any(not isinstance(v,list) or not v for v in axes.values()):
            raise ValueError('INVALID_SEARCH_SPACE')
        n=1
        for values in axes.values(): n*=len(values)
        if n>budget: raise ValueError('VARIANT_BUDGET_EXCEEDED')
        # Every declared variant is enrolled before selection. Outcome execution remains closed.
        keys=sorted(axes)
        return [{**deepcopy(p),'question':fields.get('question',QUESTIONS[family]),
                 'search_family':plan['family'],'parameters':dict(zip(keys,values)),
                 'uncertainty':p['uncertainty']+['SEARCH_DOMAIN:'+str(plan['domain']),
                    'STOP_CONDITION:'+str(plan['stop_condition']), 'ECONOMIC_EXECUTION_NOT_AUTHORIZED']}
                for values in itertools.product(*(axes[k] for k in keys))]
    if family=='MODEL_ASSISTED':
        if backend is None: raise BackendUnavailable('GPT_OSS_LIVE=FALSE:LOCAL_MODEL_NOT_CONFIGURED')
        health=backend.healthcheck()
        prompt=json.dumps({'instruction':'Propose bounded falsifiable questions only. Model commentary is not evidence.',
                           'source_reference':source['observation_ref'],'context':fields},sort_keys=True)
        response=backend.generate_structured(prompt,MODEL_SCHEMA)
        validate_structure(response,MODEL_SCHEMA)
        bounded(response)
        if len(response['questions'])>budget: raise ValueError('MODEL_VARIANT_BUDGET_EXCEEDED')
        return [{**deepcopy(p),'question':q,'evidence_mode':'MODEL_COMMENTARY',
                 'prior_exposure_state':'UNKNOWN', 'parameters':{'model_alternative':i},
                 'uncertainty':p['uncertainty']+['MODEL_PROVENANCE:'+canonical_hash(health),
                                               'PROMPT_HASH:'+canonical_hash(prompt)]}
                for i,q in enumerate(response['questions'])]
    return [{**p,'question':fields.get('question',QUESTIONS[family])}]

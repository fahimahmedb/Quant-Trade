"""Append-only, hash-chained seed/exposure journal on canonical Git state.

All mutation is planned in memory and atomically published by GitHubStateStore.
No local authoritative database, deletion API, scheduler or outcome ingestion.
"""
from copy import deepcopy

from ..github_state import PREFIX
from ..expansion.v2_core import canonical_hash
from ..multi_source_ideation_hardening import DurableProposalLedger
from .contracts import STATES, AUTHORITY, seed, novelty, bounded, clock

JOURNAL = PREFIX + 'artifacts/idea-feed/journal.json'


class SeedRegistry:
    def __init__(self, document=None):
        incoming = deepcopy((document or {}).get('events', []))
        self.events = []
        previous = None
        seen_keys=set()
        for i, event in enumerate(incoming):
            body = {k:v for k,v in event.items() if k != 'event_hash'}
            if event['seq'] != i + 1 or event['previous'] != previous or canonical_hash(body) != event['event_hash']:
                raise ValueError('PARTIAL_OR_CORRUPT_SEED_JOURNAL')
            if event['key'] in seen_keys: raise ValueError('DUPLICATE_JOURNAL_EVENT_KEY')
            seen_keys.add(event['key'])
            previous = event['event_hash']
            self._validate_event(event)
            if event['kind']=='SEED_ENROLLED':
                checker=SeedRegistry(); checker.events=deepcopy(self.events)
                raw=dict(event['payload']['seed']); raw.pop('seed_id')
                if checker.enrol(raw,event['at'])!=event['payload']:
                    raise ValueError('ROOT_OR_VARIANT_ACCOUNTING_REWRITE_FORBIDDEN')
            self.events.append(event)
        if document is not None and document != self.document():
            raise ValueError('PARTIAL_OR_CORRUPT_SEED_JOURNAL')

    @classmethod
    def load(cls, snapshot):
        return cls(snapshot.read(JOURNAL) if JOURNAL in snapshot.blobs else None)

    def document(self):
        return {'schema_version':'idea-seed-journal-v1', 'events':deepcopy(self.events),
                'head':self.events[-1]['event_hash'] if self.events else None}

    def append(self, kind, payload, at, key):
        clock(at)
        for event in self.events:
            if event['key'] == key:
                if event['kind'] != kind or event['payload'] != payload:
                    raise ValueError('IMMUTABLE_EVENT_IDENTITY_COLLISION')
                return deepcopy(event)
        event = {'seq':len(self.events)+1, 'previous':self.document()['head'],
                 'kind':kind, 'payload':deepcopy(payload), 'at':at, 'key':key}
        event['event_hash'] = canonical_hash(event)
        self._validate_event(event)
        self.events.append(event)
        return deepcopy(event)

    @staticmethod
    def _validate_event(event):
        clock(event['at'])
        p=event['payload']; kind=event['kind']
        if kind=='SEED_ENROLLED':
            raw=dict(p['seed']); sid=raw.pop('seed_id')
            if seed(raw)['seed_id']!=sid or p['state'] not in STATES:
                raise ValueError('INVALID_SEED_ENROLMENT')
        elif kind=='POLICY_CYCLE':
            for row in p['proposals']: DurableProposalLedger().persist(row)
        elif kind=='STATE_TRANSITION':
            if p['state'] not in STATES: raise ValueError('INVALID_TRANSITION_STATE')
            if p['state'].startswith('KILLED') or p['state']=='PROMOTED':
                from ..expansion.scientific_adjudication import validate_adjudication
                validate_adjudication(p['qualified_disposition'])
        elif kind not in {'RESEARCH_EXPOSURE','SOURCE_WORK_COMPLETED','DISCOVERY_RECEIPT'}:
            raise ValueError('UNKNOWN_SEED_JOURNAL_EVENT')

    def seeds(self):
        return {e['payload']['seed']['seed_id']:deepcopy(e['payload']) for e in self.events if e['kind']=='SEED_ENROLLED'}

    def enrol(self, payload, at):
        s = seed(payload)
        if clock(s['first_observed_at']) > clock(at): raise ValueError('OBSERVATION_IN_FUTURE')
        known = self.seeds()
        if s['seed_id'] in known: return known[s['seed_id']]
        classification, match = 'ECONOMICALLY_DISTINCT', None
        priority = {'TEXTUAL_DUPLICATE':0, 'UNKNOWN_REVIEW_REQUIRED':1, 'PARAMETRIC_VARIANT':2,
                    'STRUCTURAL_TRANSFER':3, 'ECONOMICALLY_DISTINCT':4}
        for sid, row in known.items():
            level = novelty(s, row['seed'])
            if priority[level] < priority[classification]: classification, match = level, sid
        if not known and s['mechanism_family']=='UNKNOWN': classification='UNKNOWN_REVIEW_REQUIRED'
        parent = s['parent_seed']
        if parent and parent not in known: raise ValueError('UNKNOWN_PARENT_SEED')
        if parent and classification == 'ECONOMICALLY_DISTINCT':
            raise ValueError('DISTINCT_IDENTITY_CANNOT_CLAIM_VARIANT_PARENT')
        if classification in {'PARAMETRIC_VARIANT','TEXTUAL_DUPLICATE'}:
            parent = match
        # Unresolved novelty must not silently collapse the attempted-hypothesis
        # denominator. Pending roots are not claims of certified novelty.
        root = known[parent]['root_hypothesis_id'] if parent else 'root-' + s['seed_id']
        status = {'TEXTUAL_DUPLICATE':'DUPLICATE','PARAMETRIC_VARIANT':'VARIANT',
                  'UNKNOWN_REVIEW_REQUIRED':'PENDING_CONFIRMATION'}.get(classification,'SEED_REGISTERED')
        row = {'seed':s, 'root_hypothesis_id':root, 'parent_seed':parent,
               'novelty':classification, 'state':status, 'match':match,
               'variant_id':canonical_hash({'root':root,'parameters':s['parameters']}),
               'variant_count':int(status=='VARIANT')}
        self.append('SEED_ENROLLED', row, at, 'seed:'+s['seed_id'])
        self.expose(root, 'SOURCE_SEEN', s['source_id']+':'+s['source_version'], at,
                    s['prior_exposure_state'], evidence_refs=s['evidence_refs'])
        if s['origin_family']=='REPLICATION':
            self.expose(root,'PAPER_SEEN',s['evidence_refs'][0],at,'KNOWN_EXPOSURE',
                        publication_available_at=s['available_at'])
        return deepcopy(row)

    def transition(self, sid, state, reason, at, *, reopening_reason=None, qualified_disposition=None):
        if state not in STATES or not reason: raise ValueError('INVALID_SEED_TRANSITION')
        row=self.seeds()[sid]
        previous=self.states()[sid]
        if state in {'DUPLICATE','VARIANT','SEED_REGISTERED'}:
            raise ValueError('BIRTH_CLASSIFICATION_IMMUTABLE')
        if (previous.startswith('KILLED') or previous.startswith('PARKED')) and not reopening_reason:
            raise ValueError('REOPENING_REASON_REQUIRED')
        # This feed cannot manufacture scientific/economic dispositions.
        if state.startswith('KILLED') or state=='PROMOTED':
            if qualified_disposition is None: raise ValueError('DOWNSTREAM_SCIENTIFIC_AUTHORITY_REQUIRED')
            from ..expansion.scientific_adjudication import validate_adjudication
            validate_adjudication(qualified_disposition)
            expected='PROMOTE' if state=='PROMOTED' else 'KILL'
            if qualified_disposition['verdict']!=expected:
                raise ValueError('SCIENTIFIC_DISPOSITION_MISMATCH')
            receipts=[e['payload'] for e in self.events if e['kind']=='DISCOVERY_RECEIPT'
                      and sid in e['payload']['seed_refs']]
            if not any(r['candidate_hash']==qualified_disposition.get('candidate_hash') for r in receipts):
                raise ValueError('SCIENTIFIC_DISPOSITION_SEED_BINDING_MISSING')
        p={'seed_id':sid,'previous':previous,'state':state,'reason':reason,'reopening_reason':reopening_reason}
        if qualified_disposition is not None: p['qualified_disposition']=deepcopy(qualified_disposition)
        self.append('STATE_TRANSITION',p,at,canonical_hash({'p':p,'at':at}))

    def states(self):
        states={sid:r['state'] for sid,r in self.seeds().items()}
        for e in self.events:
            if e['kind']=='STATE_TRANSITION': states[e['payload']['seed_id']]=e['payload']['state']
        return states

    def expose(self, root, kind, reference, at, contamination='UNKNOWN', **metadata):
        if root not in {r['root_hypothesis_id'] for r in self.seeds().values()}:
            raise ValueError('EXPOSURE_ROOT_NOT_ENROLLED')
        if kind not in {'SOURCE_SEEN','PAPER_SEEN','HISTORICAL_RESULT_CONSULTED','DATASET_EXPOSED',
                        'PREVIOUS_EXPERIMENT','MODEL_PROMPT','PROVENANCE_GAP'}:
            raise ValueError('INVALID_EXPOSURE_KIND')
        if contamination not in {'UNKNOWN','KNOWN_EXPOSURE','CONTAMINATED'}: raise ValueError('INVALID_CONTAMINATION')
        bounded(metadata)
        p={'root_hypothesis_id':root,'kind':kind,'reference':reference,
           'contamination':contamination,'metadata':metadata}
        self.append('RESEARCH_EXPOSURE',p,at,canonical_hash({'exposure':p,'at':at}))

    def exposure_state(self, root):
        states={e['payload']['contamination'] for e in self.events if e['kind']=='RESEARCH_EXPOSURE'
                and e['payload']['root_hypothesis_id']==root}
        if 'CONTAMINATED' in states: return 'CONTAMINATED'
        if 'KNOWN_EXPOSURE' in states: return 'KNOWN_EXPOSURE'
        return 'UNKNOWN'

    def proposals(self):
        ledger=DurableProposalLedger()
        for e in self.events:
            if e['kind']=='POLICY_CYCLE':
                for row in e['payload']['proposals']: ledger.persist(row)
        return ledger

    def metrics(self):
        result={}
        states=self.states()
        for sid,r in self.seeds().items():
            s=r['seed']; key=s['source_id']+'|'+s['cohort']
            m=result.setdefault(key,{'source_id':s['source_id'],'cohort':s['cohort'],
                'SEEDS_GENERATED':0,'ROOT_HYPOTHESES_ENROLLED':0,'VARIANTS_ENROLLED':0,
                'VARIANTS_TESTED':0,'DUPLICATES':0,'CANDIDATES':0,'EXPERIMENTS':0,'BLOCKED':0,
                'KILLED':0,'PARKED':0,'PROMOTED':0,'EVIDENCE_PENDING':0,'mechanisms':set(),
                'roots':set(),'OOS_PASS':'UNKNOWN','PROSPECTIVE_PASS':'UNKNOWN','ECONOMIC_PASS':'UNKNOWN',
                'TIME_TO_DISCOVERY':'UNKNOWN','RESEARCH_COST':'UNKNOWN','REOPEN_REASON':[]})
            m['SEEDS_GENERATED']+=1
            if r['root_hypothesis_id']=='root-'+sid: m['roots'].add(r['root_hypothesis_id'])
            m['VARIANTS_ENROLLED']+=int(r['state']=='VARIANT')
            m['DUPLICATES']+=int(r['state']=='DUPLICATE')
            m['mechanisms'].add(s['mechanism_family'])
            state=states[sid]
            for metric,prefix in [('BLOCKED','BLOCKED'),('KILLED','KILLED'),('PARKED','PARKED')]:
                m[metric]+=int(state.startswith(prefix))
            m['EVIDENCE_PENDING']+=int(state=='PENDING_CONFIRMATION')
        for m in result.values():
            m['ROOT_HYPOTHESES_ENROLLED']=len(m.pop('roots'))
            m['UNIQUE_MECHANISMS']=len(m.pop('mechanisms')-{'UNKNOWN'})
        counted_candidates=set()
        for e in self.events:
            p=e['payload']
            if e['kind']=='DISCOVERY_RECEIPT' and p['candidate_hash']:
                for key in {self.seeds()[sid]['seed']['source_id']+'|'+self.seeds()[sid]['seed']['cohort']
                            for sid in p['seed_refs']}:
                    if (key,p['candidate_hash']) not in counted_candidates:
                        result[key]['CANDIDATES']+=1
                        counted_candidates.add((key,p['candidate_hash']))
            if e['kind']=='STATE_TRANSITION':
                s=self.seeds()[p['seed_id']]['seed']; m=result[s['source_id']+'|'+s['cohort']]
                if p.get('reopening_reason'): m['REOPEN_REASON'].append(p['reopening_reason'])
                m['PROMOTED']+=int(p['state']=='PROMOTED')
        return result


def guard_append(previous, current):
    """Storage membrane: even direct store callers cannot rewrite/delete seed history."""
    old=SeedRegistry(previous); new=SeedRegistry(current)
    if new.events[:len(old.events)] != old.events:
        raise ValueError('SEED_HISTORY_REWRITE_OR_DELETION_FORBIDDEN')

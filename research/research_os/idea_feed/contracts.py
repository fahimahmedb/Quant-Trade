"""Strict pre-outcome seed contracts; origin, mechanism and method are separate."""
from copy import deepcopy
from datetime import datetime, timezone
import json

from ..expansion.v2_core import canonical_hash
from ..multi_source_ideation import _reject_outcome_fields
from ..multi_source_ideation_hardening import DurableProposalLedger

AUTHORITY = {k: False for k in ('economic_experiment_authorized',
    'prospective_observation_authorized', 'real_capital_authorized',
    'live_trading_authorized', 'outcome_accessed')}
FAMILIES = ('REPLICATION', 'RULE_CONSTRAINT_EVENT', 'BOUNDED_EMPIRICAL',
            'FUNDAMENTAL_DOCUMENT', 'INSTRUMENT_RELATIONSHIP', 'RISK_TRANSFER', 'MODEL_ASSISTED')
STATES = {'SEED_REGISTERED', 'DUPLICATE', 'VARIANT', 'BLOCKED_DATA', 'BLOCKED_AUTHORITY',
          'PARKED_LOW_POWER', 'PARKED_TRIGGER', 'KILLED_NO_EFFECT', 'KILLED_COSTS',
          'KILLED_CAPACITY', 'KILLED_LEAKAGE', 'PROMOTED', 'PENDING_CONFIRMATION'}
IDENTITY = ('actor', 'mechanism_family', 'information_source', 'universe', 'instruments',
            'clock', 'horizon', 'constraint', 'possible_transfer', 'rule_structure')
REQUIRED = {'source_id', 'source_version', 'published_at', 'available_at', 'first_observed_at',
    'evidence_refs', 'origin_family', 'origin', 'discovery_method', 'mechanism_family',
    'mechanism_state', 'universe', 'instruments', 'clock', 'horizon', 'question',
    'expected_direction', 'alternative_explanations', 'uncertainty', 'required_data',
    'actor', 'constraint', 'possible_payer', 'possible_transfer', 'cost_concerns',
    'capacity_concerns', 'information_source', 'rule_structure', 'cohort', 'research_budget',
    'search_family', 'parameters', 'parent_seed', 'lineage', 'reopening_reason',
    'prior_exposure_state', 'evidence_mode'}


def clock(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('TIMEZONE_REQUIRED')
    return parsed.astimezone(timezone.utc)


def bounded(value):
    # Reject NaN, arbitrary objects, outcome and operational authority at every depth.
    json.dumps(value, allow_nan=False)
    _reject_outcome_fields(value)
    DurableProposalLedger._reject_operational_keys(value)
    def check(v):
        if isinstance(v, dict):
            for k, child in v.items():
                if k.strip().lower().endswith('_authorized') or k.strip().lower() in {
                    'outcome_accessed', 'scientific_verdict', 'economic_result', 'performance',
                    'effect_size', 'observed_effect', 'oos_pass', 'economic_pass', 'prospective_pass'}:
                    raise ValueError('AUTHORITY_OR_RESULT_FIELD_FORBIDDEN:' + k)
                check(child)
        elif isinstance(v, list):
            for child in v: check(child)
    check(value)


def normalized(value):
    if isinstance(value, str): return ' '.join(value.lower().split())
    if isinstance(value, list): return sorted((normalized(x) for x in value), key=str)
    if isinstance(value, dict): return {k: normalized(v) for k, v in value.items()}
    return value


def seed(payload):
    if not isinstance(payload, dict) or set(payload) != REQUIRED:
        raise ValueError('SEED_SCHEMA_FIELDS_MISMATCH')
    bounded(payload)
    p = deepcopy(payload)
    lists={'evidence_refs','instruments','alternative_explanations','uncertainty','required_data',
           'cost_concerns','capacity_concerns','lineage'}
    scalars=REQUIRED-lists-{'research_budget','parameters','parent_seed','reopening_reason'}
    if any(not isinstance(p[k],str) or not p[k].strip() for k in scalars):
        raise ValueError('INVALID_SEED_SCALAR')
    if any(p[k] is not None and not isinstance(p[k],str) for k in ('parent_seed','reopening_reason')):
        raise ValueError('INVALID_SEED_LINEAGE_REFERENCE')
    if p['origin_family'] not in FAMILIES or p['mechanism_state'] not in {
            'UNKNOWN', 'HYPOTHESIS', 'DOCUMENTED_UNVERIFIED'}:
        raise ValueError('INVALID_ORIGIN_OR_MECHANISM_STATE')
    if p['mechanism_family'] == 'UNKNOWN' and p['mechanism_state'] != 'UNKNOWN':
        raise ValueError('UNKNOWN_MECHANISM_MUST_REMAIN_UNKNOWN')
    for k in ('source_id','source_version','origin','discovery_method','question','cohort','search_family'):
        if not isinstance(p[k], str) or not p[k].strip() or p[k] == 'UNKNOWN':
            raise ValueError('MISSING_SEED_IDENTITY:' + k)
    for k in ('evidence_refs','instruments','alternative_explanations','uncertainty',
              'required_data','cost_concerns','capacity_concerns','lineage'):
        if not isinstance(p[k], list) or any(not isinstance(x,str) or not x.strip() for x in p[k]):
            raise ValueError('INVALID_SEED_LIST:' + k)
    if not p['evidence_refs'] or not p['uncertainty'] or not p['required_data']:
        raise ValueError('SEED_PROVENANCE_AND_UNCERTAINTY_REQUIRED')
    if p['evidence_mode'] not in {'DETERMINISTIC_FIXTURE', 'DOCUMENTARY', 'MODEL_COMMENTARY'}:
        raise ValueError('INVALID_EVIDENCE_MODE')
    if type(p['research_budget']) is not int or p['research_budget'] < 1:
        raise ValueError('INVALID_RESEARCH_BUDGET')
    if p['prior_exposure_state'] not in {'UNKNOWN','KNOWN_EXPOSURE','CONTAMINATED'}:
        raise ValueError('INVALID_EXPOSURE_STATE')
    if not isinstance(p['parameters'], dict): raise ValueError('INVALID_PARAMETERS')
    if not clock(p['published_at']) <= clock(p['available_at']) <= clock(p['first_observed_at']):
        raise ValueError('SOURCE_AVAILABILITY_CONTRADICTION')
    # Source attribution and scientific content are immutable, including birth cohort.
    p['seed_id'] = canonical_hash(p)
    return p


def novelty(current, previous):
    a, b = normalized(current), normalized(previous)
    if all(a[k] == b[k] for k in IDENTITY):
        if a['parameters'] != b['parameters']:
            return 'PARAMETRIC_VARIANT'
        if a['question'] == b['question']:
            return 'TEXTUAL_DUPLICATE'
        return 'UNKNOWN_REVIEW_REQUIRED'
    if all(a[k] == b[k] for k in ('actor','mechanism_family','constraint','possible_transfer','rule_structure')):
        if a['mechanism_family'] != 'unknown': return 'STRUCTURAL_TRANSFER'
    if any(a[k] != 'unknown' and b[k] != 'unknown' and a[k] != b[k]
           for k in ('actor','mechanism_family','constraint','possible_transfer','rule_structure')):
        return 'ECONOMICALLY_DISTINCT'
    return 'UNKNOWN_REVIEW_REQUIRED'

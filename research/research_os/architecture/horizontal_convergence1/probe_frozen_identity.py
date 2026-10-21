"""Reproduce a handoff finding using existing metadata-only fixtures.

This is diagnostic evidence, not a test that grants readiness or a production
path. No market data, model, network, persistent research write or outcome is used.
Run from any directory with Python 3.12; stdout is the factual probe receipt.
"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]

from research.research_os.expansion.economic_test_readiness_v1 import economic_test_readiness
from research.research_os.expansion.portfolio_v2 import structural_identity
from research.research_os.tests.test_economic_readiness_integration import fixture, legacy


def probe():
    package = fixture()
    result = economic_test_readiness(package, legacy=legacy())
    protocol = result['experiment_plan']['frozen_protocol']
    expression = protocol['economic_expression']
    direct = structural_identity({
        'hypothesis_id': 'HANDOFF-REPRESENTATION-PROBE', 'generation_id': 'G1',
        'instrument': expression['instrument'], 'universe': expression['universe'],
        'timing_clock': expression['entry_clock'], 'horizon': expression['horizon'],
    })
    fields = result['identity']['fields']
    return {
        'finding': 'CROSS_AXIS_FINDING', 'finding_id': 'L001', 'owner': 'LONGITUDINAL',
        'base_sha': '97165db2faa3300cef1f23de0045ed93d25eb9cb',
        'from_module': 'EXPERIMENT_INFRASTRUCTURE_FROZEN_PROTOCOL',
        'to_module': 'ECONOMIC_IDENTITY_PORTFOLIO',
        'entrypoint': 'economic_test_readiness', 'readiness_status': result['status'],
        'upstream_frozen_expression': expression, 'upstream_frozen_clock': protocol['clock'],
        'returned_identity': {k: fields[k] for k in ('instrument', 'universe', 'timing_clock', 'horizon')},
        'direct_consumer_representation': {k: direct['fields'][k] for k in ('instrument', 'universe', 'timing_clock', 'horizon')},
        'instrument_lost': fields['instrument']['value'] != expression['instrument'],
        'universe_lost': fields['universe']['value'] != expression['universe'],
        'horizon_differs_from_frozen_declaration': fields['horizon']['value'] != expression['horizon'],
        'clock_unresolved': fields['timing_clock']['status'] == 'UNKNOWN',
        'authority': result['authority'], 'outcome_accessed': False,
        'scope': 'METADATA_ONLY_DIAGNOSTIC_NOT_QUALIFICATION_OR_NEW_ECONOMIC_TRUTH',
    }


if __name__ == '__main__':
    print(json.dumps(probe(), sort_keys=True, indent=2))

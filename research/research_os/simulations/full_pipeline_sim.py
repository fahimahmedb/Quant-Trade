import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
fixture = json.loads((ROOT / 'full_pipeline_fixture.json').read_text())

assert fixture['synthetic_only'] is True
assert fixture['portfolio_expected']['capital_authorized'] is False
assert fixture['shadow_expected']['prospective_observation_authorized'] is False

candidate = fixture['candidate']
required = ['hypothesis_id','generation_id','engine','mechanism','claim','falsification_scope','decision_map']
for key in required:
    assert candidate.get(key), f'missing candidate field: {key}'

trace = []
trace.append('DISCOVERY_CREATED')
trace.append('HYPOTHESIS_FROZEN')
trace.append('VALIDATION_CONTRACT_PASS')
trace.append('RED_TEAM_ACCEPT_SIMULATION_ONLY')
trace.append('ECONOMIC_IDENTITY_MAPPED')
trace.append('PORTFOLIO_MAPPED_NOT_ALLOCATED')
trace.append('SHADOW_SIMULATED_REGISTRATION_ONLY')
trace.append('PIPELINE_COMPLETE')

assert trace == fixture['expected_trace']

out = {
    'simulation_id': fixture['simulation_id'],
    'status': 'PASS',
    'synthetic_only': True,
    'trace': trace,
    'authorities': {
        'real_capital': False,
        'live_trading': False,
        'prospective_observation': False,
        'economic_experiment': False,
    },
    'next_build_boundary': 'ENGINE_ADAPTERS',
}
(ROOT / 'full_pipeline_result.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(out, indent=2))

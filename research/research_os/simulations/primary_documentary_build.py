"""Replay captured primary facts through existing stages; no economic experiment.

Run with ``python -m research.research_os.simulations.primary_documentary_build
--checkpoint-dir /tmp/primary-build --output /tmp/primary-build-summary.json``.
Checkpoint directories pin generations and must not be reused for changed inputs.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path

from research.research_os.engines.builtin import ENGINE_REGISTRY
from research.research_os.engines.protocol import EngineContext
from research.research_os.expansion.canonical_spine import run_canonical_spine, ENGINE_CAPABILITIES
from research.research_os.expansion.experiment_runner import DryRunExperimentRunner
from research.research_os.expansion.persistent_state import write_immutable_json
from research.research_os.expansion.portfolio_v2 import portfolio_diagnostics_v2
from research.research_os.scientific_store import sha256_json

PRIMARY_SOURCES = {
    'fundamental':'apple_fy2025_statement_cells.json',
    'event_document':'apple_dividend_announcements.json',
    'institutional_flow':'sec_t1_operative_rule.json',
}


def documentary_case(base: Path, engine_key: str):
    source = json.loads((base / 'sources' / PRIMARY_SOURCES[engine_key]).read_text())
    output = ENGINE_REGISTRY[engine_key].run(source, EngineContext('PRIMARY-BUILD', synthetic_only=False))
    hid = output['candidate']['hypothesis_id']
    configuration = json.loads((base / 'simulations/aggressive_architecture_fixture.json').read_text())
    configuration['run_id'] = f'PRIMARY-DOCUMENTARY-BUILD-{engine_key}'
    configuration['sources'][engine_key] = source
    configuration['base_time'] = source['freeze_time']
    configuration['implementability'][hid] = {
        'source_available':True, 'pit_feasible':True, 'expression_feasible':False,
        'cost_model_feasible':False, 'capacity_observable':False,
    }
    configuration['experiments'][hid] = {
        'dataset_provenance':{'source_refs':output['source_refs'], 'capture_hash':source['documentary_packet']['content_hash']},
        'code_version':'primary-documentary-build.v1', 'cost_model_version':'UNQUALIFIED',
        'pit_controls_declared':True, 'leakage_controls_declared':True,
        'multiplicity_accounting_declared':False,
    }
    configuration['economic_identity'][hid] = {
        'asset':'AAPL' if engine_key != 'institutional_flow' else 'UNKNOWN',
        'payer':'UNKNOWN', 'beta':'UNKNOWN', 'capacity':'UNKNOWN',
        'liquidity':'UNKNOWN', 'tail_exposure':'UNKNOWN',
    }
    task = json.loads((base / 'simulations/canonical_spine_task.json').read_text())
    task['task_id'] = f'PRIMARY-DOCUMENTARY-BUILD-{engine_key}'
    task['task_type'] = output['engine_family']
    task['inputs'].update(engine_key=engine_key, evidence_mode='DOCUMENTARY')
    task['required_capability'] = ENGINE_CAPABILITIES[engine_key]
    task['authority']['scope'] = 'DOCUMENTARY_SOURCE_QUALIFICATION_ONLY'
    task['success_condition'] = 'Preserve captured facts, Legacy-first ordering and unqualified economic blockers.'
    task['allowed_actions'].append('DOCUMENTARY_RESEARCH')
    task['lease'].update(owner='offline-documentary-build', claimed_at=source['freeze_time'],
        expires_at=(datetime.fromisoformat(source['freeze_time']) + timedelta(hours=1)).isoformat())
    task['created_at'] = task['updated_at'] = source['freeze_time']
    return source, output, configuration, task


def run_primary_documentary_build(base: Path, checkpoint_dir: Path):
    checkpoint_dir = Path(checkpoint_dir)
    inputs, summaries, identities, qualifications = [], [], [], []
    for key in PRIMARY_SOURCES:
        source, output, configuration, task = documentary_case(base, key)
        directory = checkpoint_dir / key
        canonical = run_canonical_spine(base, configuration, task, checkpoint_dir=directory)
        replay = run_canonical_spine(base, configuration, task, checkpoint_dir=directory)
        if canonical != replay:
            raise ValueError('canonical replay differs')
        if canonical['legacy']['screen']['status'] != 'NO_EXACT_LEGACY_CONFLICT':
            raise ValueError('primary documentary build requires explicit Legacy resolution')
        if canonical['validation']['status'] != 'BLOCK' or canonical['forward_registration']['readiness'] != 'NOT_READY':
            raise ValueError('unqualified documentary economics cannot be promoted')
        if any(canonical['authority'].values()):
            raise PermissionError('build authority changed')
        identity = canonical['economic_identity']
        identities.append(identity)
        qualifications.append(canonical['documentary_depth']['source_qualification'])
        inputs.append({'engine_key':key, 'source':source})
        summaries.append({
            'engine_key':key, 'hypothesis_id':output['candidate']['hypothesis_id'],
            'source_file':f'sources/{PRIMARY_SOURCES[key]}', 'source_refs':output['source_refs'],
            'source_hash':source['documentary_packet']['content_hash'],
            'candidate_hash':sha256_json(output['candidate']), 'identity_hash':sha256_json(identity),
            'dossier':canonical['documentary_depth']['dossier'],
            'validation_diagnostics':canonical['validation'], 'red_team_diagnostics':canonical['red_team'],
            'claim':output['candidate']['claim'], 'falsification_scope':output['candidate']['falsification_scope'],
            'measurements':output['candidate']['documentary_evidence']['measurements'],
            'canonical_fingerprint':canonical['canonical_fingerprint'], 'canonical_replay':'IDENTICAL',
            'scientific_ledger_verified':canonical['scientific_ledger']['verified'],
            'stage_order':canonical['stage_order'], 'legacy_screen':canonical['legacy']['screen'],
            'implementability':canonical['implementability'], 'validation':canonical['validation']['status'],
            'critical_failures':canonical['validation']['critical_failures'],
            'red_team_negative_rights':canonical['red_team']['negative_rights'],
            'forward_readiness':canonical['forward_registration']['readiness'],
            'canonical_economic_transform_executed':canonical['documentary_depth']['execution_status'],
        })
    # Separate factual transform protocol. This is not the canonical economic
    # experiment, which remains unfrozen because implementability is blocked.
    protocol = {'scope':'DOCUMENTARY_FACT_TRANSFORMS_ONLY', 'input_hash':sha256_json(inputs),
                'metrics':['DOCUMENTARY_FACTS_V1'], 'economic_experiment':False}
    envelope = {'experiment_id':'PRIMARY-FACT-TRANSFORM-ONLY', 'status':'FROZEN_READY_NO_OUTCOME',
                'protocol_hash':sha256_json(protocol), 'outcome_opened':False}
    runner = DryRunExperimentRunner()
    plan = runner.plan(envelope, qualifications, {'dataset_manifest_hash':sha256_json(inputs),
        'code_hash':runner.execution_code_hash(), 'environment_hash':runner.execution_environment_hash(),
        'seed':0, 'declared_metrics':['DOCUMENTARY_FACTS_V1']})
    result = runner.execute(plan, inputs, checkpoint_dir / 'fact_transforms')
    if result != runner.execute(plan, inputs, checkpoint_dir / 'fact_transforms'):
        raise ValueError('fact transform replay differs')
    return {
        'build_profile':'primary-documentary-build.v1', 'evidence_class':'DOCUMENTARY',
        'scope':'OFFLINE_BUILD_PROOF_NOT_SCIENTIFIC_EDGE_VALIDATION',
        'candidates':summaries, 'economic_identities':identities,
        'portfolio':portfolio_diagnostics_v2(identities),
        'fact_transform_protocol':protocol, 'fact_transform_plan':plan,
        'fact_transform_execution':{k:v for k,v in result.items() if k != 'records'},
        'fact_transform_replay':'IDENTICAL', 'economic_result':'NOT_OBSERVED',
        'limitations':[
            'Current captures do not establish historical point-in-time availability.',
            'Raw digests and public-source receipts are not publisher signatures.',
            'Official 2025 CFR rule edition is pinned; current legal status and individual applicability remain unqualified. The historical SEC staff FAQ remains nonbinding.',
            'Declared distributions are year-over-year announcements, not consecutive payments or consensus surprise.',
            'Shared AAPL issuer and equity-beta thesis tags do not establish empirical exposure or return correlation.',
            'No eligible flow population, actual funding pressure, payer, tradable horizon, costs or capacity qualified.',
            'Builder regression tests and deterministic validators are not independent scientific validation.',
        ],
        'authority':dict(task['authority'], scope='OFFLINE_DOCUMENTARY_BUILD_ONLY'),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checkpoint-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = run_primary_documentary_build(Path(__file__).resolve().parents[1], args.checkpoint_dir)
    write_immutable_json(args.output, report)
    print(json.dumps({'candidate_count':len(report['candidates']),
                      'fact_transform_replay':report['fact_transform_replay'],
                      'forward_readiness':[r['forward_readiness'] for r in report['candidates']]}))


if __name__ == '__main__':
    main()

"""CP038 rebuilt: serialized frozen-contract admission, not hash validity alone."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
from unittest.mock import patch

import pytest

from research.research_os.expansion.experiment_runner import (
    BINDING_MISMATCH_ERRORS, DryRunExperimentRunner, FROZEN_PROTOCOL_FIELDS,
    FrozenExperimentBindingError,
)
from research.research_os.scientific_store import sha256_json
from research.research_os.tests.test_experiment_runner_frozen_protocol import fixture
from research.research_os.tests.test_work_build_depth import execution_plan, sources


def frozen():
    envelope, qualifications, meta = fixture()
    runner = DryRunExperimentRunner()
    return runner, runner.plan(envelope, qualifications, meta), envelope, qualifications, meta


def rehash(plan):
    """Recompute every self-hash; this deliberately supplies no trusted origin."""
    body = plan['frozen_protocol']
    bindings = DryRunExperimentRunner._binding_hashes(body)
    plan['binding_hashes'] = deepcopy(bindings)
    plan['plan']['binding_hashes'] = deepcopy(bindings)
    plan['plan']['frozen_protocol_hash'] = sha256_json(body)
    plan['execution_plan_hash'] = sha256_json(plan['plan'])
    receipt = plan['pre_outcome_receipt']
    receipt.update(binding_hashes=deepcopy(bindings),
                   frozen_protocol_hash=plan['plan']['frozen_protocol_hash'],
                   execution_plan_hash=plan['execution_plan_hash'])
    receipt['receipt_hash'] = sha256_json({k: v for k, v in receipt.items() if k != 'receipt_hash'})
    return plan


@pytest.mark.parametrize('attempts', [None, False, True, -1, -10**80, 0.0, 1.5, '0', [], {}])
def test_reconstructed_multiplicity_cannot_bypass_initial_freeze_contract(attempts):
    runner, plan, envelope, qualifications, meta = frozen()
    meta['frozen_protocol']['observed_attempt_count'] = attempts
    initial = runner.plan(envelope, qualifications, meta)
    assert initial['status'] == 'BLOCK'
    assert 'FROZEN_PROTOCOL_OBSERVED_ATTEMPT_COUNT_INVALID' in initial['blockers']
    plan['frozen_protocol']['observed_attempt_count'] = attempts
    rehash(plan)
    for action in (lambda: runner.replay(json.loads(json.dumps(plan))),
                   lambda: runner.verify_bindings(plan, envelope, qualifications, meta)):
        with pytest.raises(ValueError, match='FROZEN_PROTOCOL_OBSERVED_ATTEMPT_COUNT_INVALID'):
            action()


@pytest.mark.parametrize('field', FROZEN_PROTOCOL_FIELDS)
def test_serialized_missing_declarations_are_not_rehabilitated_by_valid_hashes(field):
    runner, plan, envelope, qualifications, meta = frozen()
    del meta['frozen_protocol'][field]
    assert runner.plan(envelope, qualifications, meta)['status'] == 'BLOCK'
    del plan['frozen_protocol'][field]
    rehash(plan)
    with pytest.raises(ValueError, match='FROZEN_PROTOCOL_.*(MISSING|INVALID)'):
        runner.replay(json.loads(json.dumps(plan)))


@pytest.mark.parametrize('version', [None, '', 'pre-outcome-frozen-protocol.v0',
                                     'pre-outcome-frozen-protocol.v99', False])
def test_embedded_version_cannot_disagree_with_declared_supported_version(version):
    runner, plan, *_ = frozen()
    plan['frozen_protocol']['freeze_version'] = version
    rehash(plan)
    with pytest.raises(ValueError, match='FROZEN_PROTOCOL_VERSION'):
        runner.replay(plan)


@pytest.mark.parametrize('field,foreign', [
    ('protocol_hash', 'foreign-protocol'), ('code_hash', 'foreign-code'),
    ('environment_hash', 'foreign-environment'), ('seed', 1729),
    ('source_route_hashes', ['foreign-route']),
])
@pytest.mark.parametrize('side', ['plan', 'frozen_protocol'])
def test_rehashed_internal_duplicate_identity_must_agree(field, foreign, side):
    runner, plan, *_ = frozen()
    plan[side][field] = foreign
    rehash(plan)
    with pytest.raises(ValueError, match='FROZEN_PLAN_.*BINDING_MISMATCH'):
        runner.replay(plan)


def test_replay_returns_identity_of_checked_snapshot_under_caller_mutation():
    runner, plan, *_ = frozen()
    expected = runner.replay(deepcopy(plan))
    check = runner._assert_pre_outcome_closed
    calls = []

    def change_after_receipt_check(value, **kwargs):
        check(value, **kwargs)
        calls.append(value)
        if kwargs.get('require_authority_fields'):
            plan['experiment_id'] = 'FOREIGN-AFTER-CHECK'

    with patch.object(runner, '_assert_pre_outcome_closed', side_effect=change_after_receipt_check):
        actual = runner.replay(plan)
    assert len(calls) == 2
    assert actual == expected


def test_verify_cannot_swap_validated_plan_after_replay_to_match_changed_source():
    runner, plan, envelope, qualifications, meta = frozen()
    changed = deepcopy(qualifications)
    changed[0]['snapshot_hash'] = 'foreign-snapshot'
    replacement = runner.plan(envelope, changed, meta)
    replay = runner.replay

    def replay_then_swap(checked):
        result = replay(checked)
        plan.clear()
        plan.update(deepcopy(replacement))
        return result

    with patch.object(runner, 'replay', side_effect=replay_then_swap):
        with pytest.raises(FrozenExperimentBindingError, match=BINDING_MISMATCH_ERRORS['source']):
            runner.verify_bindings(plan, envelope, changed, meta)


@pytest.mark.parametrize('attempts', [False, -1, '0'])
def test_invalid_reconstructed_freeze_is_denied_before_any_execution_checkpoint(tmp_path, attempts):
    inputs = [{'engine_key': 'fundamental', 'source': sources()['fundamental']}]
    runner, plan = execution_plan(inputs)
    envelope, qualifications, meta = fixture()
    # Build a frozen documentary plan without changing its actual executable binding.
    meta.update({k: plan['plan'][k] for k in ('dataset_manifest_hash', 'code_hash', 'environment_hash', 'seed', 'declared_metrics')})
    plan = runner.plan(envelope, qualifications, meta)
    plan['frozen_protocol']['observed_attempt_count'] = attempts
    rehash(plan)
    with pytest.raises(ValueError, match='FROZEN_PROTOCOL_OBSERVED_ATTEMPT_COUNT_INVALID'):
        runner.execute(json.loads(json.dumps(plan)), inputs, tmp_path)
    assert not list(tmp_path.iterdir())


@pytest.mark.parametrize('attempts', [0, 1, 10**80])
def test_valid_huge_counts_roundtrip_retry_and_parallel_read_are_stable(attempts):
    runner, _, envelope, qualifications, meta = frozen()
    meta['frozen_protocol']['observed_attempt_count'] = attempts
    plan = runner.plan(envelope, qualifications, meta)
    restored = json.loads(json.dumps(plan, sort_keys=True))
    expected = runner.replay(restored)
    with ThreadPoolExecutor(max_workers=4) as pool:
        assert list(pool.map(runner.replay, [restored] * 12)) == [expected] * 12
    assert runner.verify_bindings(restored, envelope, qualifications, meta)['status'] == 'FROZEN_BINDINGS_MATCH'
    assert plan == restored
    assert all(v is False for k, v in restored['pre_outcome_receipt'].items() if k.endswith('_authorized'))


def test_consistent_self_hash_rewrite_is_not_claimed_to_be_authenticated_origin():
    runner, plan, envelope, qualifications, meta = frozen()
    for target in (plan['frozen_protocol'], plan['plan']):
        target['seed'] = 1729
    rehash(plan)
    assert runner.replay(plan)['status'] == 'REPLAY_MATCH'
    with pytest.raises(FrozenExperimentBindingError, match='CODE_ENVIRONMENT_BINDING_MISMATCH'):
        runner.verify_bindings(plan, envelope, qualifications, meta)


def test_opaque_legacy_plan_remains_replayable_without_inventing_a_frozen_protocol():
    runner, _, envelope, qualifications, meta = frozen()
    del meta['frozen_protocol']
    envelope.pop('protocol_payload')
    envelope['protocol_hash'] = 'opaque-legacy-reference'
    plan = runner.plan(envelope, qualifications, meta)
    assert runner.replay(json.loads(json.dumps(plan)))['status'] == 'REPLAY_MATCH'
    assert plan['frozen_protocol_capability'] == 'LEGACY_DRY_RUN_ONLY'
    assert 'pre_outcome_receipt' not in plan


@pytest.mark.parametrize('side', ['plan', 'frozen_protocol'])
def test_duplicate_identity_comparison_uses_serialized_types_not_python_numeric_equality(side):
    runner, plan, *_ = frozen()
    assert type(plan['plan']['seed']) is int
    plan[side]['seed'] = float(plan[side]['seed'])
    rehash(plan)
    with pytest.raises(ValueError, match='FROZEN_PLAN_SEED_BINDING_MISMATCH'):
        runner.replay(plan)


def test_reconstructed_freeze_cannot_drop_outer_version_marker():
    runner, plan, *_ = frozen()
    del plan['plan']['frozen_protocol_version']
    rehash(plan)
    with pytest.raises(ValueError, match='FROZEN_PROTOCOL_VERSION'):
        runner.replay(plan)


@pytest.mark.parametrize('mode', ['LIVE', 'UNKNOWN', None, False])
def test_rehashed_execution_mode_cannot_claim_dry_run_replay(mode):
    runner, plan, *_ = frozen()
    plan['plan']['execution_mode'] = mode
    rehash(plan)
    with pytest.raises(ValueError, match='DRY_RUN_EXECUTION_MODE_REQUIRED'):
        runner.replay(plan)


def remove_frozen_representation(plan):
    plan.pop('frozen_protocol')
    plan.pop('pre_outcome_receipt')
    plan['binding_hashes'] = None
    plan['frozen_protocol_capability'] = 'LEGACY_DRY_RUN_ONLY'
    for name in ('frozen_protocol_version', 'frozen_protocol_hash', 'binding_hashes'):
        del plan['plan'][name]
    plan['execution_plan_hash'] = sha256_json(plan['plan'])


@pytest.mark.parametrize('retained_claim', ['version', 'frozen_hash', 'payload_bindings',
                                           'outer_bindings', 'capability', 'receipt'])
def test_partial_frozen_state_cannot_be_misread_as_opaque_legacy(retained_claim):
    runner, original, *_ = frozen()
    plan = deepcopy(original)
    remove_frozen_representation(plan)
    if retained_claim == 'version':
        plan['plan']['frozen_protocol_version'] = original['plan']['frozen_protocol_version']
    elif retained_claim == 'frozen_hash':
        plan['plan']['frozen_protocol_hash'] = original['plan']['frozen_protocol_hash']
    elif retained_claim == 'payload_bindings':
        plan['plan']['binding_hashes'] = original['plan']['binding_hashes']
    elif retained_claim == 'outer_bindings':
        plan['binding_hashes'] = original['binding_hashes']
    elif retained_claim == 'capability':
        plan['frozen_protocol_capability'] = 'READY'
    else:
        plan['pre_outcome_receipt'] = original['pre_outcome_receipt']
    plan['execution_plan_hash'] = sha256_json(plan['plan'])
    with pytest.raises(ValueError, match='FROZEN_PROTOCOL_REQUIRED|PRE_OUTCOME_RECEIPT_WITHOUT_FROZEN_PROTOCOL'):
        runner.replay(json.loads(json.dumps(plan)))


@pytest.mark.parametrize('capability', ['LEGACY_DRY_RUN_ONLY', 'BLOCKED', 'UNKNOWN'])
def test_frozen_body_cannot_carry_a_contradictory_capability_state(capability):
    runner, plan, *_ = frozen()
    plan['frozen_protocol_capability'] = capability
    with pytest.raises(ValueError, match='FROZEN_PROTOCOL_CAPABILITY_MISMATCH'):
        runner.replay(plan)


def test_fully_removed_freeze_requires_external_rebinding_to_claim_frozen_identity():
    runner, plan, envelope, qualifications, meta = frozen()
    remove_frozen_representation(plan)
    assert runner.replay(plan)['status'] == 'REPLAY_MATCH'
    with pytest.raises(FrozenExperimentBindingError, match='FROZEN_PROTOCOL_NOT_PRESENT'):
        runner.verify_bindings(plan, envelope, qualifications, meta)

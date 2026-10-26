"""Alternate call paths and optimized Python must preserve closed authority."""

from copy import deepcopy
import json
import os
import subprocess
import sys

import pytest

from research.research_os.engines.decay import decay_monitor
from research.research_os.expansion.final_shape import decay_guard
from research.research_os.expansion.forward_v2 import ForwardRegistryV2, build_forward_contract_v2
from research.research_os.expansion.experiment_runner import DryRunExperimentRunner
from research.research_os.tests.test_experiment_runner_frozen_protocol import fixture


def registration():
    return dict(observation_authorization="NOT_AUTHORIZED", observation_started=False,
                future_outcomes_consumed=0)


@pytest.mark.parametrize("changes", [
    {"observation_authorization": "AUTHORIZED_FOR_EXACT_SCOPE"},
    {"observation_authorization": "UNKNOWN"}, {"future_outcomes_consumed": 1},
    {"future_outcomes_consumed": False}, {"observation_started": True},
    {"observation_started": "false"},
])
def test_decay_guard_rejects_inconsistent_authority_and_consumption(changes):
    record = dict(registration(), **changes)
    with pytest.raises(PermissionError):
        decay_guard([record])


@pytest.mark.parametrize("optimization", [[], ["-O"], ["-OO"]])
def test_guard_still_executes_when_python_assertions_are_removed(optimization):
    code = """
from research.research_os.expansion.final_shape import decay_guard
try:
    decay_guard([{'observation_authorization': 'AUTHORIZED_FOR_EXACT_SCOPE',
                  'observation_started': True, 'future_outcomes_consumed': 1}])
except PermissionError:
    print('BLOCKED')
else:
    raise SystemExit('FAIL_OPEN')
"""
    result = subprocess.run([sys.executable, *optimization, "-c", code],
                            env=os.environ.copy(), capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == "BLOCKED"


@pytest.mark.parametrize("key", ["economic_experiment_authorized", "prospective_observation_authorized",
                                 "real_capital_authorized", "live_trading_authorized"])
@pytest.mark.parametrize("value", [True, "false", 0, None])
def test_dry_run_replay_cannot_accept_an_authority_grant_or_ambiguous_flag(key, value):
    runner = DryRunExperimentRunner()
    plan = runner.plan(*fixture())
    plan[key] = value
    with pytest.raises(PermissionError):
        runner.replay(plan)


@pytest.mark.parametrize("field,value", [("state", "AUTHORIZED_FOR_EXACT_SCOPE"),
                                         ("owner_authorization", "AUTHORIZED_FOR_EXACT_SCOPE"),
                                         ("future_outcomes_consumed", 1), ("observation_count", 1)])
def test_forward_import_and_reload_refuse_forged_authority(tmp_path, field, value):
    registry = ForwardRegistryV2()
    contract = build_forward_contract_v2(
        dict(prospective_contract_id="fixture", hypothesis_id="fixture", generation_id="one",
             protocol_hash="fixture", readiness="READY_AWAITING_OWNER_AUTHORITY"),
        t0="2026-10-20T00:00:00Z", observation_scope={"fixture": True})
    registry.register(contract)
    registry.save(tmp_path / "forward.json")
    registry = ForwardRegistryV2.load(tmp_path / "forward.json")
    forged = deepcopy(contract)
    forged[field] = value
    with pytest.raises(PermissionError):
        registry.register(forged)
    with pytest.raises(PermissionError):
        registry.validate_observation_candidate("fixture", {"observed_at": "2026-10-21T00:00:00Z"})
    assert registry.snapshot()["authorized_count"] == 0


def test_older_decay_entrypoint_cannot_consume_forged_observations():
    with pytest.raises(RuntimeError):
        decay_monitor({"prospective_observation_authorized": True,
                       "registrations": [{"observation_started": True}]})
    clean = decay_guard([registration()])
    assert clean["observations_consumed"] == 0
    assert json.loads(json.dumps(clean))["status"] == "INACTIVE_BY_AUTHORITY"

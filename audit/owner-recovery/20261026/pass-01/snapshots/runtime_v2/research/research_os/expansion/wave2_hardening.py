from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from .experiment_runner import DryRunExperimentRunner, summarize_reproducibility
from .forward_v2 import ForwardRegistryV2, build_forward_contract_v2
from .persistent_state import build_persistent_final_shape
from .portfolio_v2 import portfolio_diagnostics_v2
from .source_qualification import ImmutableSourceRouteRegistry, qualify_source_route
from .validation_v2 import validator_diagnostics_v2, validator_portfolio_summary


def build_wave2_hardening(
    base_fixture: Dict[str, Any],
    wave2_fixture: Dict[str, Any],
    *,
    legacy_ledger_path: Optional[Path] = None,
) -> Dict[str, Any]:
    persistent = build_persistent_final_shape(base_fixture, legacy_ledger_path=legacy_ledger_path)
    outputs = persistent["engine_outputs"]
    by_hid = {item["candidate"]["hypothesis_id"]: item for item in outputs}
    envelope_by_hid = {
        item["hypothesis_generation"].split(":", 1)[0]: item
        for item in persistent["experiment_envelopes"]
    }
    validation_by_hid = {item["hypothesis_id"]: item for item in persistent["validations"]}
    trial_by_hid = {item["hypothesis_id"]: item for item in persistent["trial_ledger"]}

    source_registry = ImmutableSourceRouteRegistry()
    source_qualifications: Dict[str, Dict[str, Any]] = {}
    for hid, route in wave2_fixture["source_routes"].items():
        qualification = qualify_source_route(route, freeze_time=wave2_fixture["freeze_time"])
        source_registry.register(qualification)
        source_qualifications[hid] = qualification

    runner = DryRunExperimentRunner()
    dry_runs: Dict[str, Dict[str, Any]] = {}
    replays: Dict[str, Dict[str, Any]] = {}
    validator_v2: Dict[str, Dict[str, Any]] = {}

    for hid, output in by_hid.items():
        qualification = source_qualifications[hid]
        envelope = envelope_by_hid[hid]
        plan = runner.plan(
            envelope,
            [qualification],
            wave2_fixture["runner_meta"][hid],
        )
        dry_runs[hid] = plan
        if plan["status"] == "READY_FOR_REPRODUCIBLE_DRY_RUN":
            replays[hid] = runner.replay(plan)
        validator_v2[hid] = validator_diagnostics_v2(
            engine_output=output,
            validation_v1=validation_by_hid[hid],
            source_qualifications=[qualification],
            envelope=envelope,
            dry_run_plan=plan,
            trial_record=trial_by_hid[hid],
            experiment_meta=base_fixture["experiments"][hid],
        )

    portfolio_v2 = portfolio_diagnostics_v2(persistent["portfolio"]["identities"])

    forward_registry = ForwardRegistryV2()
    forward_contracts: Dict[str, Dict[str, Any]] = {}
    for registration in persistent["forward_farm"]:
        hid = registration["hypothesis_id"]
        contract = build_forward_contract_v2(
            registration,
            t0=wave2_fixture["forward"][hid]["t0"],
            observation_scope=wave2_fixture["forward"][hid]["scope"],
        )
        forward_registry.register(contract)
        forward_contracts[hid] = contract

    source_snapshot = source_registry.snapshot()
    forward_snapshot = forward_registry.snapshot()
    reproducibility = summarize_reproducibility(dry_runs.values())
    validator_summary = validator_portfolio_summary(validator_v2.values())

    unsafe_access = (
        any(item["outcome_accessed"] for item in source_qualifications.values())
        or any(item["outcome_accessed"] for item in dry_runs.values())
        or portfolio_v2["return_series_consumed"]
        or forward_snapshot["future_outcomes_consumed"] > 0
        or forward_snapshot["authorized_count"] > 0
    )

    candidate_states = {
        hid: {
            "source": source_qualifications[hid]["status"],
            "dry_run": dry_runs[hid]["status"],
            "validator_v2": validator_v2[hid]["status"],
            "claim_ceiling": validator_v2[hid]["claim_ceiling"],
            "forward_state": forward_contracts[hid]["state"],
        }
        for hid in sorted(by_hid)
    }

    hardening_status = "PASS"
    if persistent["persistent_state_status"] != "PASS" or unsafe_access:
        hardening_status = "FAIL"
    if source_snapshot["outcome_routes_authorized"] is not False:
        hardening_status = "FAIL"
    if portfolio_v2["capital_allocation_authorized"] or portfolio_v2["orders_authorized"]:
        hardening_status = "FAIL"

    return {
        "run_id": persistent["run_id"],
        "hardening_status": hardening_status,
        "persistent_base_status": persistent["persistent_state_status"],
        "source_registry": source_snapshot,
        "source_qualifications": source_qualifications,
        "dry_run_experiments": dry_runs,
        "dry_run_replays": replays,
        "reproducibility": reproducibility,
        "validator_v2": validator_v2,
        "validator_summary": validator_summary,
        "portfolio_v2": portfolio_v2,
        "forward_contracts_v2": forward_contracts,
        "forward_registry_v2": forward_snapshot,
        "candidate_states": candidate_states,
        "unsafe_access_detected": unsafe_access,
        "economic_experiment_authorized": False,
        "prospective_observation_authorized": False,
        "real_capital_authorized": False,
        "live_trading_authorized": False,
    }

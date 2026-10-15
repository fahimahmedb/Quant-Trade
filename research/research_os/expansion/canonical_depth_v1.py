from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from research.research_os.scientific_store import sha256_json

from .engine_dossiers_v1 import REQUIRED_BY_FAMILY, build_engine_dossier
from .experiment_runner import DryRunExperimentRunner
from .forward_v2 import ForwardRegistryV2, build_forward_contract_v2
from .portfolio_v2 import portfolio_diagnostics_v2
from .source_qualification import qualify_source_route
from .validation_v2 import validator_diagnostics_v2


def enrich_canonical_depth(
    canonical: Dict[str, Any],
    base_fixture: Dict[str, Any],
    wave2_fixture: Dict[str, Any],
    wave3_fixture: Dict[str, Any],
) -> Dict[str, Any]:
    """Thicken already-frozen canonical interfaces without adding a new top-level stage.

    This function consumes the output of ``run_canonical_spine`` and enriches the
    artifacts that already exist: candidate dossier, source/PIT qualification,
    experiment dry-run reproducibility, validator diagnostics, portfolio structural
    diagnostics and forward-contract immutability.

    It is deliberately outcome-blind and authority-blind: no economic result,
    prospective observation, capital allocation or live trading can be opened here.
    """

    if canonical.get("downstream_executed") is not True:
        raise ValueError("canonical depth requires a non-legacy-blocked lineage")

    output = deepcopy(canonical["candidate"])
    candidate = output["candidate"]
    hid = candidate["hypothesis_id"]
    family = output["engine_family"]

    candidate_hash_before = sha256_json(candidate)

    route = wave2_fixture["source_routes"][hid]
    source_qualification = qualify_source_route(
        route,
        freeze_time=wave2_fixture["freeze_time"],
    )

    runner = DryRunExperimentRunner()
    dry_run = runner.plan(
        canonical["experiment_envelope"],
        [source_qualification],
        wave2_fixture["runner_meta"][hid],
    )
    replay = None
    if dry_run["status"] == "READY_FOR_REPRODUCIBLE_DRY_RUN":
        replay = runner.replay(dry_run)

    validator_v2 = validator_diagnostics_v2(
        engine_output=output,
        validation_v1=canonical["validation"],
        source_qualifications=[source_qualification],
        envelope=canonical["experiment_envelope"],
        dry_run_plan=dry_run,
        trial_record=canonical["trial_ledger"][0],
        experiment_meta=base_fixture["experiments"][hid],
    )

    dossier = None
    if family in REQUIRED_BY_FAMILY:
        dossier = build_engine_dossier(
            output,
            wave3_fixture["engine_details"][hid],
        )

    portfolio_v2 = portfolio_diagnostics_v2([canonical["economic_identity"]])

    forward_contract = build_forward_contract_v2(
        canonical["forward_registration"],
        t0=wave2_fixture["forward"][hid]["t0"],
        observation_scope=wave2_fixture["forward"][hid]["scope"],
    )
    forward_registry = ForwardRegistryV2()
    forward_registry.register(forward_contract)
    forward_snapshot = forward_registry.snapshot()

    candidate_hash_after = sha256_json(output["candidate"])
    candidate_unchanged = candidate_hash_before == candidate_hash_after

    unsafe_access = any(
        (
            source_qualification.get("outcome_accessed") is not False,
            dry_run.get("outcome_accessed") is not False,
            portfolio_v2.get("return_series_consumed") is not False,
            forward_snapshot.get("authorized_count") != 0,
            forward_snapshot.get("future_outcomes_consumed") != 0,
            not candidate_unchanged,
        )
    )

    system_failures = []
    if source_qualification["status"] != "PASS":
        system_failures.append("SOURCE_QUALIFICATION")
    if dossier is not None and dossier["status"] != "PASS":
        system_failures.append("ENGINE_DOSSIER")
    if unsafe_access:
        system_failures.append("UNSAFE_ACCESS_OR_MUTATION")

    # Candidate-level scientific blockers are not system failures. For example an
    # implementability blocker can legitimately make the dry-run / validator BLOCK.
    candidate_state = {
        "implementability": canonical["implementability"]["status"],
        "dry_run": dry_run["status"],
        "validator_v2": validator_v2["status"],
        "claim_ceiling": validator_v2["claim_ceiling"],
        "forward_state": forward_contract["state"],
    }

    return {
        "depth_profile": "canonical-depth.v1",
        "system_status": "PASS" if not system_failures else "FAIL",
        "system_failures": system_failures,
        "hypothesis_id": hid,
        "generation_id": candidate["generation_id"],
        "engine_family": family,
        "candidate_hash_before": candidate_hash_before,
        "candidate_hash_after": candidate_hash_after,
        "candidate_unchanged": candidate_unchanged,
        "engine_dossier": dossier,
        "source_qualification": source_qualification,
        "dry_run_experiment": dry_run,
        "dry_run_replay": replay,
        "validator_v2": validator_v2,
        "portfolio_v2": portfolio_v2,
        "forward_contract_v2": forward_contract,
        "forward_registry_v2": forward_snapshot,
        "candidate_state": candidate_state,
        "unsafe_access_detected": unsafe_access,
        "economic_result_observed": False,
        "economic_experiment_authorized": False,
        "prospective_observation_authorized": False,
        "real_capital_authorized": False,
        "live_trading_authorized": False,
    }

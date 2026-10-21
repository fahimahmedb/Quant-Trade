from __future__ import annotations

from copy import deepcopy

from research.research_os.scientific_store import sha256_json
from research.research_os.expansion.experiment_infrastructure import bind_pre_outcome_infrastructure
from research.research_os.expansion.experiment_runner import DryRunExperimentRunner


def rebind_factory_infrastructure(bundle: dict) -> dict:
    """Re-attest a deliberately rebound pre-outcome test fixture.

    This helper is intentionally test-only. It rebuilds the canonical Factory
    runner/receipt/replay/registry envelope after a test has deliberately
    changed frozen scientific intent. It never opens outcomes or grants any
    execution authority.
    """
    envelope = bundle["protocol"]
    payload = envelope["protocol_payload"]
    frozen_protocol = payload["dataset_provenance"]["protocol"]
    frozen_sources = payload["dataset_provenance"]["sources"]
    pit = bundle["sources"]["pit_metadata"]

    qualifications = [
        {
            "status": "PASS",
            "outcome_accessed": False,
            "route_hash": sha256_json(source["route"]),
            "snapshot_hash": source["snapshot_hash"],
        }
        for source in frozen_sources
    ]
    runner_meta = {
        "dataset_manifest_hash": bundle["sources"]["manifest_hash"],
        "code_hash": sha256_json({"code": "fixture-rebind"}),
        "environment_hash": sha256_json({"environment": "fixture-rebind"}),
        "seed": 7,
        "declared_metrics": ["gross", "net"],
        "code_sha": "fixture-rebind-code-sha",
        "environment": "fixture-python",
        "dependency_fingerprint": sha256_json({"deps": "fixture-rebind"}),
        "source_pit_metadata": deepcopy(pit),
        "frozen_protocol": deepcopy(frozen_protocol),
    }
    runner = DryRunExperimentRunner()
    plan = runner.plan(deepcopy(envelope), qualifications, runner_meta)
    if plan["status"] != "READY_FOR_REPRODUCIBLE_DRY_RUN":
        raise AssertionError(plan["blockers"])
    replay = runner.replay(plan)
    infrastructure = bind_pre_outcome_infrastructure(
        envelope=deepcopy(envelope),
        plan=plan,
        replay=replay,
        trial_accounting=deepcopy(bundle["trial_accounting"]),
        geometry_declaration=frozen_protocol.get("geometry_declaration"),
        power_declaration=frozen_protocol.get("power_declaration"),
    )
    bundle["experiment_infrastructure"] = infrastructure

    binding = bundle["reproducibility"]["binding_payload"]
    binding["candidate_hash"] = bundle["candidate_hash"]
    binding["protocol_hash"] = envelope["protocol_hash"]
    binding["source_snapshot_hashes"] = sorted(bundle["sources"]["snapshot_hashes"])
    binding["execution_plan_hash"] = plan["execution_plan_hash"]
    binding["experiment_registry_id"] = infrastructure["registry"]["registry_id"]
    binding["experiment_registry_hash"] = infrastructure["registry"]["entry_hash"]
    binding["experiment_infrastructure_hash"] = infrastructure["infrastructure_hash"]
    bundle["reproducibility"]["binding_hash"] = sha256_json(binding)
    return bundle

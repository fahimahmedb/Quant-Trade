from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Optional

from research.research_os.scientific_store import sha256_json
from .engine_dossiers_v1 import REQUIRED_BY_FAMILY, build_engine_dossiers
from .persistent_state import build_persistent_final_shape
from .source_adapters_v1 import DesignOnlyAdapterRegistry, validate_adapter_spec
from .wave2_hardening import build_wave2_hardening


def build_wave3_engine_depth(
    base_fixture: Dict[str, Any],
    wave2_fixture: Dict[str, Any],
    wave3_fixture: Dict[str, Any],
    *,
    legacy_ledger_path: Optional[Path] = None,
) -> Dict[str, Any]:
    wave2 = build_wave2_hardening(
        base_fixture,
        wave2_fixture,
        legacy_ledger_path=legacy_ledger_path,
    )
    persistent = build_persistent_final_shape(
        base_fixture,
        legacy_ledger_path=legacy_ledger_path,
    )

    primary_outputs = [
        deepcopy(output)
        for output in persistent["engine_outputs"]
        if output["engine_family"] in REQUIRED_BY_FAMILY
    ]
    candidate_fingerprint_before = sha256_json(
        [output["candidate"] for output in primary_outputs]
    )

    adapter_registry = DesignOnlyAdapterRegistry()
    validated_adapters: Dict[str, Dict[str, Any]] = {}
    for spec in wave3_fixture["adapters"]:
        validated = validate_adapter_spec(spec)
        adapter_registry.register(validated)
        validated_adapters[validated["adapter_id"]] = validated

    adapter_bindings: Dict[str, Dict[str, Any]] = {}
    primary_hypotheses = {
        output["candidate"]["hypothesis_id"] for output in primary_outputs
    }
    for hid in sorted(primary_hypotheses):
        adapter_ids = list(wave3_fixture.get("adapter_map", {}).get(hid) or [])
        missing = sorted(adapter_id for adapter_id in adapter_ids if adapter_id not in validated_adapters)
        blocked = sorted(
            adapter_id
            for adapter_id in adapter_ids
            if adapter_id in validated_adapters and validated_adapters[adapter_id]["status"] != "PASS"
        )
        blockers = []
        if not adapter_ids:
            blockers.append("NO_ADAPTER_BOUND")
        blockers.extend(f"MISSING_ADAPTER:{adapter_id}" for adapter_id in missing)
        blockers.extend(f"BLOCKED_ADAPTER:{adapter_id}" for adapter_id in blocked)
        adapter_bindings[hid] = {
            "hypothesis_id": hid,
            "adapter_ids": adapter_ids,
            "status": "READY_DESIGN_ONLY" if not blockers else "BLOCK",
            "blockers": blockers,
            "network_activation_authorized": False,
            "outcome_access_authorized": False,
        }

    dossiers = build_engine_dossiers(
        primary_outputs,
        wave3_fixture["engine_details"],
    )
    dossier_by_hid = {
        record["hypothesis_id"]: record for record in dossiers["records"]
    }

    candidate_fingerprint_after = sha256_json(
        [output["candidate"] for output in primary_outputs]
    )
    adapter_snapshot = adapter_registry.snapshot()

    unsafe_access = (
        wave2["unsafe_access_detected"]
        or adapter_snapshot["activated_count"] > 0
        or adapter_snapshot["network_enabled_count"] > 0
        or adapter_snapshot["outcome_authorized_count"] > 0
        or any(record["outcome_accessed"] for record in dossiers["records"])
        or any(record["candidate_mutated"] for record in dossiers["records"])
        or candidate_fingerprint_before != candidate_fingerprint_after
    )

    status = "PASS"
    if wave2["hardening_status"] != "PASS":
        status = "FAIL"
    if any(item["status"] != "PASS" for item in validated_adapters.values()):
        status = "FAIL"
    if any(item["status"] != "READY_DESIGN_ONLY" for item in adapter_bindings.values()):
        status = "FAIL"
    if dossiers["block_count"] != 0 or dossiers["pass_count"] != len(primary_outputs):
        status = "FAIL"
    if unsafe_access:
        status = "FAIL"

    engine_states = {
        hid: {
            "adapter_binding": adapter_bindings[hid]["status"],
            "dossier": dossier_by_hid[hid]["status"],
            "wave2_source": wave2["candidate_states"][hid]["source"],
            "wave2_dry_run": wave2["candidate_states"][hid]["dry_run"],
            "wave2_validator": wave2["candidate_states"][hid]["validator_v2"],
            "wave2_claim_ceiling": wave2["candidate_states"][hid]["claim_ceiling"],
            "economic_result": "NOT_OBSERVED",
        }
        for hid in sorted(primary_hypotheses)
    }

    return {
        "run_id": wave2["run_id"],
        "wave3_status": status,
        "wave2_status": wave2["hardening_status"],
        "adapter_registry": adapter_snapshot,
        "validated_adapters": validated_adapters,
        "adapter_bindings": adapter_bindings,
        "engine_dossiers": dossiers,
        "engine_states": engine_states,
        "candidate_integrity": {
            "before": candidate_fingerprint_before,
            "after": candidate_fingerprint_after,
            "unchanged": candidate_fingerprint_before == candidate_fingerprint_after,
        },
        "unsafe_access_detected": unsafe_access,
        "real_source_activation_authorized": False,
        "network_access_authorized": False,
        "economic_experiment_authorized": False,
        "prospective_observation_authorized": False,
        "real_capital_authorized": False,
        "live_trading_authorized": False,
    }

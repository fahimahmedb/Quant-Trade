from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from .acquisition_firewall_v1 import (
    build_acquisition_plan,
    build_provenance_manifest,
    content_firewall,
    firewall_summary,
    normalize_typed_pit_record,
)
from .typed_pit_registry_v1 import TypedPITRegistry
from .wave3_engine_depth import build_wave3_engine_depth


def build_wave4_acquisition_firewall(
    base_fixture: Dict[str, Any],
    wave2_fixture: Dict[str, Any],
    wave3_fixture: Dict[str, Any],
    wave4_fixture: Dict[str, Any],
    *,
    legacy_ledger_path: Optional[Path] = None,
) -> Dict[str, Any]:
    wave3 = build_wave3_engine_depth(
        base_fixture,
        wave2_fixture,
        wave3_fixture,
        legacy_ledger_path=legacy_ledger_path,
    )

    plans: Dict[str, Dict[str, Any]] = {}
    firewalls: Dict[str, Dict[str, Any]] = {}
    typed_records: Dict[str, Dict[str, Any]] = {}
    manifests: Dict[str, Dict[str, Any]] = {}
    registry = TypedPITRegistry()

    for request in wave4_fixture["acquisition_requests"]:
        request_id = request["request_id"]
        adapter_id = request["adapter_id"]
        adapter = wave3["validated_adapters"][adapter_id]
        plan = build_acquisition_plan(adapter, request)
        raw_record = wave4_fixture["raw_records"][request_id]
        firewall = content_firewall(plan, raw_record)
        typed = normalize_typed_pit_record(plan, raw_record, firewall)
        manifest = build_provenance_manifest(plan, firewall, typed)

        plans[request_id] = plan
        firewalls[request_id] = firewall
        typed_records[request_id] = typed
        manifests[request_id] = manifest
        if typed.get("status") == "PASS" and manifest.get("status") == "PASS":
            registry.register(typed, manifest)

    registry_snapshot = registry.snapshot()
    firewall_stats = firewall_summary(firewalls.values())

    records_by_adapter: Dict[str, list[str]] = {}
    for entry in registry_snapshot["entries"]:
        records_by_adapter.setdefault(entry["adapter_id"], []).append(entry["record_id"])

    engine_input_bindings: Dict[str, Dict[str, Any]] = {}
    for hid, adapter_ids in wave3_fixture["adapter_map"].items():
        record_refs = sorted(
            record_id
            for adapter_id in adapter_ids
            for record_id in records_by_adapter.get(adapter_id, [])
        )
        engine_input_bindings[hid] = {
            "hypothesis_id": hid,
            "adapter_ids": list(adapter_ids),
            "typed_pit_record_refs": record_refs,
            "status": "READY_PIT_TYPED_FIXTURE_ONLY" if record_refs else "BLOCK",
            "network_access_authorized": False,
            "outcome_access_authorized": False,
            "candidate_mutated": False,
        }

    unsafe_access = (
        wave3["unsafe_access_detected"]
        or any(plan.get("network_call_performed") for plan in plans.values())
        or any(plan.get("outcome_accessed") for plan in plans.values())
        or firewall_stats["network_records"] > 0
        or firewall_stats["outcomes_accessed"] > 0
        or registry_snapshot["network_origin_count"] > 0
        or registry_snapshot["outcome_accessed_count"] > 0
    )

    status = "PASS"
    if wave3["wave3_status"] != "PASS":
        status = "FAIL"
    if any(plan["status"] != "READY_AWAITING_SOURCE_ACTIVATION_AUTHORITY" for plan in plans.values()):
        status = "FAIL"
    if any(record["status"] != "PASS" for record in firewalls.values()):
        status = "FAIL"
    if any(record["status"] != "PASS" for record in typed_records.values()):
        status = "FAIL"
    if any(record["status"] != "PASS" for record in manifests.values()):
        status = "FAIL"
    if any(binding["status"] != "READY_PIT_TYPED_FIXTURE_ONLY" for binding in engine_input_bindings.values()):
        status = "FAIL"
    if registry_snapshot["entry_count"] != len(wave4_fixture["acquisition_requests"]):
        status = "FAIL"
    if unsafe_access:
        status = "FAIL"

    return {
        "run_id": wave3["run_id"],
        "wave4_status": status,
        "wave3_status": wave3["wave3_status"],
        "acquisition_plans": plans,
        "content_firewall": firewalls,
        "typed_pit_records": typed_records,
        "provenance_manifests": manifests,
        "typed_pit_registry": registry_snapshot,
        "firewall_summary": firewall_stats,
        "engine_input_bindings": engine_input_bindings,
        "unsafe_access_detected": unsafe_access,
        "real_source_activation_authorized": False,
        "network_access_authorized": False,
        "economic_experiment_authorized": False,
        "prospective_observation_authorized": False,
        "real_capital_authorized": False,
        "live_trading_authorized": False,
    }

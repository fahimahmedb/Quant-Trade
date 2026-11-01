#!/usr/bin/env python3
"""Executable guardrails for the Quant-Trade two-branch AI working method.

This validator is deliberately small. It does not decide scientific truth or runtime truth.
It catches the recurring process failures already observed in the project: stale authority,
local-only PASS, wrong-SHA qualification, unnecessary rebuild/review, WIP expansion,
missing continuation, and post-migration branch sprawl.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping


class ContractError(ValueError):
    pass


def load_json(path: str | Path) -> Dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ContractError(f"{path}: expected JSON object")
    return data


def validate_contract(contract: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    if contract.get("contract_version") != 1:
        errors.append("contract_version must be 1")

    authorities = contract.get("authorities", {})
    if authorities.get("project_branch") != "project/canonical":
        errors.append("project authority must be project/canonical")
    if authorities.get("code_branch") != "code/canonical":
        errors.append("code authority must be code/canonical")
    if authorities.get("project_router") != "governance/CURRENT_PROJECT_STATE.md":
        errors.append("project router must be governance/CURRENT_PROJECT_STATE.md")

    if contract.get("existing_capability_order") != [
        "REUSE",
        "CONNECT",
        "REPAIR",
        "BUILD_REQUIRED",
        "UNKNOWN",
    ]:
        errors.append("existing capability order must be REUSE > CONNECT > REPAIR > BUILD_REQUIRED > UNKNOWN")

    concurrency = contract.get("concurrency", {})
    if concurrency.get("max_active_decision_lanes") != 2:
        errors.append("max_active_decision_lanes must be 2")
    if concurrency.get("max_mutating_builders_per_capability") != 1:
        errors.append("max_mutating_builders_per_capability must be 1")
    if concurrency.get("reviewer_mutates_subject") is not False:
        errors.append("reviewer_mutates_subject must be false")

    laws = contract.get("hard_laws", {})
    required_false = {
        "local_only_pass_allowed",
        "stale_prompt_is_authority",
        "branch_name_is_authority",
        "default_branch_is_engineering_authority",
        "wrong_sha_qualification_allowed",
        "unknown_authorizes_global_audit",
        "external_block_global_stops_independent_lane",
        "build_allowed_when_reuse_connect_repair_proven",
        "review_without_new_decision_evidence_allowed",
        "code_pass_grants_scientific_or_capital_authority",
    }
    for key in sorted(required_false):
        if laws.get(key) is not False:
            errors.append(f"hard_laws.{key} must be false")

    gate_ids = [gate.get("id") for gate in contract.get("finish_gates", [])]
    expected_gates = [
        "F0_TWO_BRANCH_AUTHORITY",
        "F1_RECOVERABLE_CANONICAL_STATE",
        "F2_EXACT_HEAD_ENGINEERING_QUALIFICATION",
        "F3_REAL_VM_MULTI_WAKE",
        "F4_GLOBAL_MISSION_CONTINUATION",
        "F5_IDENTITY_CONSERVING_E2E",
        "F6_OPERATIONAL_HANDOFF",
    ]
    if gate_ids != expected_gates:
        errors.append("finish gate set/order does not match F0-F6 contract")

    if contract.get("finish_claim") != "QUANT_SYSTEM_V1_FINISHED":
        errors.append("finish_claim must be QUANT_SYSTEM_V1_FINISHED")

    expected_branches = {"project/canonical", "code/canonical"}
    if set(contract.get("post_migration_remote_branches", [])) != expected_branches:
        errors.append("post-migration branches must be exactly project/canonical and code/canonical")

    return errors


def validate_agents_entrypoint(text: str) -> List[str]:
    errors: List[str] = []
    required = [
        "project/canonical",
        "code/canonical",
        "governance/CURRENT_PROJECT_STATE.md",
        "governance/AI_WORKING_METHOD_V1.md",
    ]
    for token in required:
        if token not in text:
            errors.append(f"AGENTS.md missing canonical entrypoint token: {token}")

    stale_tokens = [
        "BLUE_CONTEXT_REACQUISITION_F11_2026-09-21.md",
        "CURRENT_GOVERNANCE_STATE_2026-09-20.md",
        "BLUE_MASTER_V2_STATE_2026-09-20.md",
    ]
    for token in stale_tokens:
        if token in text:
            errors.append(f"AGENTS.md still routes current agents through stale Blue entrypoint: {token}")
    return errors


def evaluate_mission(contract: Mapping[str, Any], mission: Mapping[str, Any]) -> str:
    required = contract.get("mission_required_fields", [])
    if any(field not in mission or mission[field] in (None, "") for field in required):
        return "REJECT_MISSING_FIELDS"

    if mission.get("current_subject_fresh") is False:
        return "RECONCILE_REQUIRED"

    max_lanes = contract.get("concurrency", {}).get("max_active_decision_lanes", 2)
    if int(mission.get("active_decision_lanes", 1)) > max_lanes:
        return "BLOCK_WIP_LIMIT"

    if mission.get("claim") == "PASS" and not mission.get("durable_remote_output", False):
        return "INVALID_LOCAL_ONLY_PASS"

    if mission.get("qualification_claim", False):
        subject_sha = mission.get("subject_sha")
        tested_sha = mission.get("tested_sha")
        if not subject_sha or not tested_sha or subject_sha != tested_sha:
            return "INVALID_WRONG_SHA_QUALIFICATION"

    existing = mission.get("existing_capability")
    if mission.get("requested_action") == "BUILD" and existing in {"REUSE", "CONNECT", "REPAIR"}:
        return "REJECT_UNNECESSARY_BUILD"

    if mission.get("mission_kind") == "REVIEW":
        decision_changing_inputs = (
            mission.get("new_exact_subject", False),
            mission.get("new_evidence", False),
            mission.get("new_counterexample_class", False),
            mission.get("new_primary_object", False),
            mission.get("irreversible_boundary", False),
        )
        if not any(decision_changing_inputs):
            return "NO_CHANGE_REQUIRED"

    if mission.get("irreversible_action", False) and mission.get("owner_authorization_required", False):
        if not mission.get("owner_authorized", False):
            return "BLOCK_OWNER_AUTHORITY"

    if mission.get("external_block", False) and mission.get("independent_lane_available", False):
        return "PARK_BLOCKED_LANE_CONTINUE_INDEPENDENT"

    if not mission.get("next_action"):
        return "REJECT_MISSING_NEXT_ACTION"

    return "ADMIT"


def validate_checkpoint(contract: Mapping[str, Any], checkpoint: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    for field in contract.get("checkpoint_required_fields", []):
        if field not in checkpoint or checkpoint[field] in (None, ""):
            errors.append(f"checkpoint missing {field}")
    return errors


def project_finish_status(contract: Mapping[str, Any], gate_status: Mapping[str, str]) -> str:
    for gate in contract.get("finish_gates", []):
        if gate.get("required", True) and gate_status.get(gate["id"]) != "PASS":
            return "NOT_FINISHED"
    return contract.get("finish_claim", "QUANT_SYSTEM_V1_FINISHED")


def validate_remote_branches(contract: Mapping[str, Any], branches: Iterable[str]) -> List[str]:
    names = {name.strip() for name in branches if name.strip()}
    required = set(contract.get("post_migration_remote_branches", []))
    errors: List[str] = []
    missing = required - names
    if missing:
        errors.append(f"missing canonical branches: {sorted(missing)}")
    if contract.get("two_branch_mode") == "ENFORCED":
        extra = names - required
        if extra:
            errors.append(f"post-migration extra remote branches forbidden: {sorted(extra)}")
        if names != required:
            errors.append("two-branch mode requires exactly two remote branches")
    return errors


def _main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("contract")
    parser.add_argument("agents")
    parser.add_argument("--branches-file")
    args = parser.parse_args(argv)

    contract = load_json(args.contract)
    errors = validate_contract(contract)
    text = Path(args.agents).read_text(encoding="utf-8")
    errors.extend(validate_agents_entrypoint(text))

    if args.branches_file:
        branches = Path(args.branches_file).read_text(encoding="utf-8").splitlines()
        errors.extend(validate_remote_branches(contract, branches))

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("AI_WORKING_METHOD_GATE=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))

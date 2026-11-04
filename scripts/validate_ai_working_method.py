#!/usr/bin/env python3
"""Executable guardrails for the Quant-Trade canonical AI working method.

The validator covers both the declarative method contract and the real mission
admission/completion interface. It deliberately does not decide scientific or
runtime truth; it verifies identity, freshness, bounded authority, provenance
shape and durable handoff invariants that can be checked mechanically.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence


class ContractError(ValueError):
    pass


def load_json(path: str | Path) -> Dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ContractError(f"{path}: expected JSON object")
    return data


def canonical_json_identity(value: Mapping[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


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
        "exact_claim_without_opened_primary_source_allowed",
        "primary_evidence_contradiction_may_be_overridden",
        "unknown_source_may_be_filled_by_inference",
        "stale_scoped_evidence_may_support_current_claim",
    }
    for key in sorted(required_false):
        if laws.get(key) is not False:
            errors.append(f"hard_laws.{key} must be false")

    continuation = contract.get("execution_continuity")
    required_continuation = {
        "external_agent_dispatch_requires_explicit_owner_authorization": True,
        "external_agent_dispatch_requires_verified_budget": True,
        "external_agent_dispatch_requires_verified_transport": True,
        "delegated_in_scope_repair_requires_new_owner_approval": False,
        "checkpoint_implies_final_handoff": False,
        "checkpoint_proves_autonomous_relaunch": False,
        "local_blocker_stops_independent_work": False,
    }
    if not isinstance(continuation, Mapping):
        errors.append("execution_continuity contract required")
    else:
        for key, expected in required_continuation.items():
            if continuation.get(key) is not expected:
                errors.append(f"execution_continuity.{key} must be {expected!r}")

    rescue = contract.get("behavioral_opportunity_rescue")
    if rescue is not None:
        if not isinstance(rescue, Mapping):
            errors.append("behavioral_opportunity_rescue must be an object")
        else:
            if rescue.get("terminal_claims") != ["PARK", "BLOCK"]:
                errors.append("behavioral_opportunity_rescue.terminal_claims must be PARK/BLOCK")
            required_scopes = {"IMPLEMENTATION", "MECHANISM", "SCIENTIFIC", "AUTHORITY", "RUNTIME", "UNKNOWN"}
            if set(rescue.get("disposition_scopes") or []) != required_scopes:
                errors.append("behavioral_opportunity_rescue.disposition_scopes mismatch")
            for key in ("terminal_disposition_required", "require_implementation_rescue_evidence",
                        "require_exact_reopen_condition", "forbid_mechanism_falsification_from_route_block"):
                if rescue.get(key) is not True:
                    errors.append(f"behavioral_opportunity_rescue.{key} must be true")

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

    admission = contract.get("mission_admission", {})
    if admission:
        if admission.get("receipt_path") != ".quant/MISSION_ADMISSION.json":
            errors.append("mission_admission.receipt_path must be .quant/MISSION_ADMISSION.json")
        if admission.get("material_change_exempt_prefixes") != ["data/feeds/"]:
            errors.append("mission_admission.material_change_exempt_prefixes must be exactly ['data/feeds/']")
        required = admission.get("required_fields", [])
        for field in (
            "mission_id",
            "mission_kind",
            "receipt_timestamp",
            "project_canonical_sha",
            "code_canonical_sha",
            "current_router_identity",
            "current_subject",
            "current_blocker_or_decision",
            "target_gate_or_blocker",
            "existing_capability",
            "why_this_work_can_change_the_decision",
            "minimal_decisive_test",
            "counterexample",
            "primary_evidence",
            "durable_output_required",
            "next_action_after_pass_fail_block",
            "owner_authorization_required",
            "active_seam",
            "active_decision_lanes",
            "mutating_builders_on_seam",
            "requested_action",
        ):
            if field not in required:
                errors.append(f"mission_admission.required_fields missing {field}")

    provenance = contract.get("exact_claim_provenance")
    if not isinstance(provenance, Mapping):
        errors.append("exact_claim_provenance contract required")
    else:
        if provenance.get("required_for_material_decision") is not True:
            errors.append("exact_claim_provenance.required_for_material_decision must be true")
        if provenance.get("admission_field") != "primary_evidence":
            errors.append("exact_claim_provenance.admission_field must be primary_evidence")
        if provenance.get("source_must_be_opened_for_support") is not True:
            errors.append("exact_claim_provenance.source_must_be_opened_for_support must be true")
        if provenance.get("primary_contradiction_wins") is not True:
            errors.append("exact_claim_provenance.primary_contradiction_wins must be true")
        if provenance.get("stale_scope_cannot_support_current_claim") is not True:
            errors.append("exact_claim_provenance.stale_scope_cannot_support_current_claim must be true")
        required_item_fields = set(provenance.get("required_item_fields", []))
        expected_item_fields = {
            "claim_id", "claim", "source_kind", "object_identity",
            "observed_value", "support", "scope", "opened",
        }
        if not expected_item_fields.issubset(required_item_fields):
            errors.append("exact_claim_provenance.required_item_fields incomplete")
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

    # External agent requests must independently pass a concrete transport/budget preflight.
    # A generic BUILD admission does not grant any secondary-agent dispatch authority.
    if mission.get("external_agent_dispatch_requested") is True:
        if mission.get("external_agent_dispatch_owner_authorized") is not True:
            return "BLOCK_EXTERNAL_AGENT_AUTHORITY"
        if mission.get("external_agent_budget_verified") is not True:
            return "BLOCK_EXTERNAL_AGENT_BUDGET"
        if (mission.get("external_agent_source_access_verified") is not True
                or mission.get("external_agent_permission_verified") is not True):
            return "BLOCK_EXTERNAL_AGENT_TRANSPORT"

    if mission.get("checkpoint_only") is True and mission.get("final_handoff_requested") is True:
        return "REJECT_CHECKPOINT_AS_FINAL"

    if mission.get("repairable_in_scope_failure") is True:
        if mission.get("remaining_budget_verified") is not True:
            return "BLOCK_REPAIR_BUDGET"
        if mission.get("owner_authorization_required") is False:
            return "CONTINUE_WITHIN_MANDATE"

    if not mission.get("next_action"):
        return "REJECT_MISSING_NEXT_ACTION"

    return "ADMIT"


def _missing(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def admission_required_fields(contract: Mapping[str, Any]) -> Sequence[str]:
    configured = contract.get("mission_admission", {}).get("required_fields")
    if configured:
        return configured
    return (
        "mission_id",
        "mission_kind",
        "receipt_timestamp",
        "project_canonical_sha",
        "code_canonical_sha",
        "current_router_identity",
        "current_subject",
        "current_blocker_or_decision",
        "target_gate_or_blocker",
        "existing_capability",
        "why_this_work_can_change_the_decision",
        "minimal_decisive_test",
        "counterexample",
        "primary_evidence",
        "durable_output_required",
        "next_action_after_pass_fail_block",
        "owner_authorization_required",
        "active_seam",
        "active_decision_lanes",
        "mutating_builders_on_seam",
        "requested_action",
    )


def validate_primary_evidence(contract: Mapping[str, Any], admission: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    cfg = contract.get("exact_claim_provenance", {})
    if not isinstance(cfg, Mapping):
        return ["MISSING_EXACT_CLAIM_PROVENANCE_CONTRACT"]

    field = str(cfg.get("admission_field") or "primary_evidence")
    evidence = admission.get(field)
    if cfg.get("required_for_material_decision", False) and (not isinstance(evidence, list) or not evidence):
        return ["MISSING_PRIMARY_EVIDENCE"]
    if evidence is None:
        return errors
    if not isinstance(evidence, list):
        return ["INVALID_PRIMARY_EVIDENCE_SHAPE"]

    required_fields = tuple(cfg.get("required_item_fields", ()))
    allowed_support = set(cfg.get("allowed_support", ("SUPPORTS", "CONTRADICTS", "UNKNOWN_SOURCE")))
    allowed_scope = set(cfg.get("allowed_scope", ("CURRENT", "HISTORICAL")))
    locator_sources = set(cfg.get("locator_sources_are_not_primary_evidence", ()))

    for index, item in enumerate(evidence):
        prefix = f"PRIMARY_EVIDENCE_{index}"
        if not isinstance(item, Mapping):
            errors.append(f"{prefix}_INVALID_ITEM")
            continue
        for name in required_fields:
            if name not in item or _missing(item[name]):
                errors.append(f"{prefix}_MISSING_{name.upper()}")
        if any(error.startswith(prefix + "_MISSING_") for error in errors):
            continue

        support = str(item.get("support"))
        scope = str(item.get("scope"))
        source_kind = str(item.get("source_kind"))
        opened = item.get("opened")

        if support not in allowed_support:
            errors.append(f"{prefix}_INVALID_SUPPORT")
        if scope not in allowed_scope:
            errors.append(f"{prefix}_INVALID_SCOPE")
        if support in {"SUPPORTS", "CONTRADICTS"} and opened is not True:
            errors.append(f"{prefix}_EXACT_CLAIM_WITHOUT_OPENED_PRIMARY_SOURCE")
        if support == "SUPPORTS" and source_kind in locator_sources:
            errors.append(f"{prefix}_NON_PRIMARY_SOURCE_USED_FOR_EXACT_CLAIM")
        if support == "SUPPORTS" and scope == "HISTORICAL":
            errors.append(f"{prefix}_STALE_SCOPED_EVIDENCE_USED_FOR_CURRENT_DECISION")
    return errors


def validate_real_mission_admission(
    contract: Mapping[str, Any],
    admission: Mapping[str, Any],
    *,
    current_project_sha: str,
    current_code_sha: str,
    current_router_identity: str,
    expected_mission_id: str | None = None,
) -> List[str]:
    errors: List[str] = []
    for field in admission_required_fields(contract):
        if field not in admission or _missing(admission[field]):
            errors.append(f"MISSING_{field.upper()}")

    if errors:
        return errors

    if admission.get("project_canonical_sha") != current_project_sha:
        errors.append("STALE_PROJECT_SHA")
    if admission.get("code_canonical_sha") != current_code_sha:
        errors.append("STALE_CODE_SHA")
    if admission.get("current_router_identity") != current_router_identity:
        errors.append("STALE_ROUTER_IDENTITY")
    if expected_mission_id is not None and admission.get("mission_id") != expected_mission_id:
        errors.append("COPIED_RECEIPT_MISSION_MISMATCH")

    subject = admission.get("current_subject")
    if not isinstance(subject, Mapping):
        errors.append("MISSING_EXACT_SUBJECT")
    else:
        if subject.get("project_sha") != current_project_sha or subject.get("code_sha") != current_code_sha:
            errors.append("MISSING_EXACT_SUBJECT")

    if not admission.get("current_blocker_or_decision"):
        errors.append("MISSING_BLOCKER_OR_DECISION")
    if not admission.get("next_action_after_pass_fail_block"):
        errors.append("MISSING_NEXT_ACTION")

    errors.extend(validate_primary_evidence(contract, admission))

    existing = admission.get("existing_capability")
    if existing not in {"REUSE", "CONNECT", "REPAIR", "BUILD_REQUIRED", "UNKNOWN"}:
        errors.append("INVALID_EXISTING_CAPABILITY")
    if admission.get("requested_action") in {"BUILD", "BUILD_REQUIRED"} and existing in {"REUSE", "CONNECT", "REPAIR"}:
        errors.append("BUILD_WHEN_REUSE_CONNECT_REPAIR_EXISTS")

    max_lanes = int(contract.get("concurrency", {}).get("max_active_decision_lanes", 2))
    if int(admission.get("active_decision_lanes", 0)) > max_lanes:
        errors.append("WIP_LIMIT_VIOLATION")
    max_builders = int(contract.get("concurrency", {}).get("max_mutating_builders_per_capability", 1))
    if int(admission.get("mutating_builders_on_seam", 0)) > max_builders:
        errors.append("CONCURRENT_SAME_SEAM_BUILDERS")

    if admission.get("mission_kind") == "REVIEW":
        decision_changing_inputs = (
            admission.get("new_exact_subject", False),
            admission.get("new_evidence", False),
            admission.get("new_counterexample_class", False),
            admission.get("new_primary_object", False),
            admission.get("irreversible_boundary", False),
        )
        if not any(decision_changing_inputs):
            errors.append("REVIEW_WITHOUT_NEW_SUBJECT_EVIDENCE_COUNTEREXAMPLE_OR_IRREVERSIBLE_BOUNDARY")

    if admission.get("local_blocker", False) and admission.get("global_stop_requested", False):
        if admission.get("independent_lane_available", False):
            errors.append("LOCAL_BLOCKER_CAUSING_UNJUSTIFIED_GLOBAL_STOP")

    if admission.get("owner_authorization_required", False) and not admission.get("owner_authorized", False):
        errors.append("OWNER_AUTHORITY_REQUIRED_BUT_MISSING")

    # This validates declared dispatch intent; a tool invocation that bypasses
    # admission still requires runtime/permission controls and is NOT proven safe.
    if admission.get("external_agent_dispatch_requested") is True:
        if admission.get("external_agent_dispatch_owner_authorized") is not True:
            errors.append("EXTERNAL_AGENT_DISPATCH_OWNER_AUTHORITY_MISSING")
        if admission.get("external_agent_budget_verified") is not True:
            errors.append("EXTERNAL_AGENT_DISPATCH_BUDGET_UNVERIFIED")
        if (admission.get("external_agent_source_access_verified") is not True
                or admission.get("external_agent_permission_verified") is not True):
            errors.append("EXTERNAL_AGENT_DISPATCH_TRANSPORT_UNVERIFIED")

    return errors


def validate_completion_binding(
    contract: Mapping[str, Any],
    admission: Mapping[str, Any],
    completion: Mapping[str, Any],
    *,
    current_project_sha: str,
    current_code_sha: str,
) -> List[str]:
    errors: List[str] = []
    identity = canonical_json_identity(admission)
    if completion.get("admission_identity") != identity:
        errors.append("ADMISSION_IDENTITY_MISMATCH")
    if completion.get("mission_id") != admission.get("mission_id"):
        errors.append("COPIED_RECEIPT_MISSION_MISMATCH")
    if completion.get("subject_sha") != current_code_sha:
        errors.append("WRONG_SHA_SUBJECT")
    if completion.get("tested_sha") != current_code_sha:
        errors.append("WRONG_SHA_QUALIFICATION")
    if completion.get("project_sha") != current_project_sha:
        errors.append("STALE_PROJECT_SHA")
    if completion.get("claim") == "PASS" and not completion.get("durable_remote_output", False):
        errors.append("LOCAL_ONLY_PASS")
    if not completion.get("next_action"):
        errors.append("MISSING_NEXT_ACTION")

    rescue_cfg = contract.get("behavioral_opportunity_rescue")
    if not isinstance(rescue_cfg, Mapping):
        rescue_cfg = {}
    # The hosted Method Gate uses claim=PASS for a FINAL_HANDOFF, even when
    # the admitted durable handoff_result is a legitimate terminal PARK/BLOCK.
    # Inspect that real admitted disposition instead of silently skipping
    # terminal anti-PARK validation on every production final handoff.
    terminal_evidence = completion
    terminal_claim = completion.get("claim")
    if admission.get("completion_intent") == "FINAL_HANDOFF":
        handoff_result = completion.get("handoff_result")
        if isinstance(handoff_result, str) and handoff_result in {"PARK", "BLOCK"}:
            terminal_claim = handoff_result
            terminal_evidence = admission
    if (rescue_cfg.get("terminal_disposition_required") is True
            and isinstance(terminal_claim, str) and terminal_claim in {"PARK", "BLOCK"}):
        scope = terminal_evidence.get("disposition_scope")
        allowed_scopes = set(rescue_cfg.get("disposition_scopes") or [])
        if not isinstance(scope, str) or scope not in allowed_scopes:
            errors.append("TERMINAL_DISPOSITION_SCOPE_REQUIRED")
        if not terminal_evidence.get("exact_reopen_condition"):
            errors.append("TERMINAL_EXACT_REOPEN_CONDITION_REQUIRED")

        if scope == "IMPLEMENTATION":
            if not terminal_evidence.get("tested_implementation_route"):
                errors.append("IMPLEMENTATION_PARK_MISSING_EXACT_TESTED_ROUTE")
            review = terminal_evidence.get("solution_search")
            if not isinstance(review, Mapping):
                errors.append("IMPLEMENTATION_PARK_MISSING_BOUNDED_SOLUTION_SEARCH")
            else:
                status = review.get("status")
                if not isinstance(status, str) or status not in {"CHECKED", "HARD_BOUNDARY", "NO_DECISION_CHANGING_ALTERNATIVE"}:
                    errors.append("IMPLEMENTATION_PARK_INVALID_SOLUTION_SEARCH_STATUS")
                if not review.get("material_obstacle") or not review.get("chosen_action_or_stop_reason"):
                    errors.append("IMPLEMENTATION_PARK_MISSING_DECISION_EVIDENCE")
                if isinstance(status, str) and status in {"CHECKED", "NO_DECISION_CHANGING_ALTERNATIVE"}:
                    primary = admission.get("primary_evidence") or []
                    qualified_refs = {
                        item.get("object_identity") for item in primary
                        if isinstance(item, Mapping) and isinstance(item.get("object_identity"), str)
                        and item.get("opened") is True
                        and item.get("support") == "SUPPORTS" and item.get("scope") == "CURRENT"
                    }
                    decisive_ref = review.get("decisive_primary_ref")
                    if not isinstance(decisive_ref, str) or decisive_ref not in qualified_refs:
                        errors.append("IMPLEMENTATION_PARK_UNLINKED_DECISIVE_PRIMARY")
                if (status == "NO_DECISION_CHANGING_ALTERNATIVE"
                        and not review.get("why_remaining_routes_cannot_change_decision")):
                    errors.append("IMPLEMENTATION_PARK_UNJUSTIFIED_NO_ALTERNATIVE")
                if status == "CHECKED":
                    paths = review.get("paths_considered")
                    if not isinstance(paths, list) or not (1 <= len(paths) <= 5) or not all(
                        isinstance(item, Mapping) and isinstance(item.get("route"), str)
                        and item.get("route").strip()
                        and isinstance(item.get("disposition"), str)
                        and item.get("disposition") in {"EXCLUDED", "BLOCKED", "UNKNOWN", "QUALIFIED"}
                        for item in paths
                    ):
                        errors.append("IMPLEMENTATION_PARK_MISSING_CHECKED_PATHS")
                if status == "HARD_BOUNDARY" and not review.get("hard_boundary_reason"):
                    errors.append("IMPLEMENTATION_PARK_MISSING_HARD_BOUNDARY_PROOF")
                if review.get("mechanism_falsified") is True:
                    errors.append("IMPLEMENTATION_BLOCK_CANNOT_FALSIFY_MECHANISM")
            if terminal_evidence.get("mechanism_falsified") is True:
                errors.append("IMPLEMENTATION_BLOCK_CANNOT_FALSIFY_MECHANISM")

        if scope != "MECHANISM" and terminal_evidence.get("mechanism_falsified") is True:
            errors.append("MECHANISM_FALSIFICATION_SCOPE_MISMATCH")
        if scope == "MECHANISM" and terminal_evidence.get("mechanism_falsified") is True:
            ref = terminal_evidence.get("falsification_primary_ref")
            primary = admission.get("primary_evidence") or []
            qualified_refs = {
                item.get("object_identity") for item in primary
                if isinstance(item, Mapping) and item.get("opened") is True
                and item.get("support") == "SUPPORTS" and item.get("scope") == "CURRENT"
            }
            if not isinstance(ref, str) or ref not in qualified_refs:
                errors.append("MECHANISM_FALSIFICATION_WITHOUT_LINKED_PRIMARY")

    if completion.get("claim") == contract.get("finish_claim", "QUANT_SYSTEM_V1_FINISHED"):
        gates = completion.get("finish_gate_statuses", {})
        if project_finish_status(contract, gates) != contract.get("finish_claim"):
            errors.append("FALSE_FINISH_WITH_OPEN_BLOCK_UNKNOWN_GATE")
    return errors


def material_change_requires_admission(paths: Iterable[str], contract: Mapping[str, Any]) -> bool:
    normalized = [path.strip() for path in paths if path and path.strip()]
    if not normalized:
        return False
    exempt = tuple(contract.get("mission_admission", {}).get("material_change_exempt_prefixes", ["data/feeds/"]))
    return any(not any(path.startswith(prefix) for prefix in exempt) for path in normalized)


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
    parser.add_argument("--admission")
    parser.add_argument("--completion")
    parser.add_argument("--current-project-sha")
    parser.add_argument("--current-code-sha")
    parser.add_argument("--current-router-identity")
    parser.add_argument("--completion-code-sha")
    parser.add_argument("--expected-mission-id")
    args = parser.parse_args(argv)

    contract = load_json(args.contract)
    errors = validate_contract(contract)
    text = Path(args.agents).read_text(encoding="utf-8")
    errors.extend(validate_agents_entrypoint(text))

    if args.branches_file:
        branches = Path(args.branches_file).read_text(encoding="utf-8").splitlines()
        errors.extend(validate_remote_branches(contract, branches))

    admission: Dict[str, Any] | None = None
    if args.admission:
        required_cli = {
            "--current-project-sha": args.current_project_sha,
            "--current-code-sha": args.current_code_sha,
            "--current-router-identity": args.current_router_identity,
        }
        for flag, value in required_cli.items():
            if not value:
                errors.append(f"{flag} required with --admission")
        if not errors:
            admission = load_json(args.admission)
            errors.extend(
                validate_real_mission_admission(
                    contract,
                    admission,
                    current_project_sha=args.current_project_sha,
                    current_code_sha=args.current_code_sha,
                    current_router_identity=args.current_router_identity,
                    expected_mission_id=args.expected_mission_id,
                )
            )

    if args.completion:
        if admission is None:
            errors.append("--completion requires --admission")
        elif not args.current_project_sha or not args.current_code_sha:
            errors.append("--completion requires current project/code SHAs")
        else:
            completion = load_json(args.completion)
            errors.extend(
                validate_completion_binding(
                    contract,
                    admission,
                    completion,
                    current_project_sha=args.current_project_sha,
                    current_code_sha=args.completion_code_sha or args.current_code_sha,
                )
            )

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    if admission is not None:
        print(f"MISSION_ADMISSION_IDENTITY={canonical_json_identity(admission)}")
        print("REAL_MISSION_ADMISSION=PASS")
    print("AI_WORKING_METHOD_GATE=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))

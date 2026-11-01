from scripts.validate_ai_working_method import (
    canonical_json_identity,
    evaluate_mission,
    material_change_requires_admission,
    project_finish_status,
    validate_agents_entrypoint,
    validate_checkpoint,
    validate_completion_binding,
    validate_contract,
    validate_real_mission_admission,
    validate_remote_branches,
)


def contract():
    return {
        "contract_version": 1,
        "authorities": {
            "project_branch": "project/canonical",
            "code_branch": "code/canonical",
            "project_router": "governance/CURRENT_PROJECT_STATE.md",
        },
        "two_branch_mode": "MIGRATING",
        "existing_capability_order": ["REUSE", "CONNECT", "REPAIR", "BUILD_REQUIRED", "UNKNOWN"],
        "concurrency": {
            "max_active_decision_lanes": 2,
            "max_mutating_builders_per_capability": 1,
            "reviewer_mutates_subject": False,
        },
        "hard_laws": {
            "local_only_pass_allowed": False,
            "stale_prompt_is_authority": False,
            "branch_name_is_authority": False,
            "default_branch_is_engineering_authority": False,
            "wrong_sha_qualification_allowed": False,
            "unknown_authorizes_global_audit": False,
            "external_block_global_stops_independent_lane": False,
            "build_allowed_when_reuse_connect_repair_proven": False,
            "review_without_new_decision_evidence_allowed": False,
            "code_pass_grants_scientific_or_capital_authority": False,
        },
        "mission_required_fields": [
            "current_subject",
            "current_blocker_or_decision",
            "decision_impact",
            "existing_capability",
            "minimal_decisive_test",
            "counterexample",
            "durable_output_required",
            "next_action",
            "owner_authorization_required",
        ],
        "mission_admission": {
            "receipt_path": ".quant/MISSION_ADMISSION.json",
            "material_change_exempt_prefixes": ["data/feeds/"],
            "required_fields": [
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
                "durable_output_required",
                "next_action_after_pass_fail_block",
                "owner_authorization_required",
                "active_seam",
                "active_decision_lanes",
                "mutating_builders_on_seam",
                "requested_action",
            ],
        },
        "checkpoint_required_fields": [
            "subject",
            "completed",
            "tests_executed",
            "decision_changed",
            "blockers_unknowns",
            "next_action",
        ],
        "finish_gates": [
            {"id": "F0_TWO_BRANCH_AUTHORITY", "required": True},
            {"id": "F1_RECOVERABLE_CANONICAL_STATE", "required": True},
            {"id": "F2_EXACT_HEAD_ENGINEERING_QUALIFICATION", "required": True},
            {"id": "F3_REAL_VM_MULTI_WAKE", "required": True},
            {"id": "F4_GLOBAL_MISSION_CONTINUATION", "required": True},
            {"id": "F5_IDENTITY_CONSERVING_E2E", "required": True},
            {"id": "F6_OPERATIONAL_HANDOFF", "required": True},
        ],
        "finish_claim": "QUANT_SYSTEM_V1_FINISHED",
        "post_migration_remote_branches": ["project/canonical", "code/canonical"],
    }


def base_mission(**overrides):
    mission = {
        "current_subject": "code/canonical@abc",
        "current_blocker_or_decision": "close current seam",
        "decision_impact": "moves F3",
        "existing_capability": "REPAIR",
        "minimal_decisive_test": "one bounded test",
        "counterexample": "existing path already closes seam",
        "durable_output_required": "remote exact SHA + run",
        "next_action": "continue to next gate",
        "owner_authorization_required": False,
        "current_subject_fresh": True,
        "active_decision_lanes": 1,
        "requested_action": "REPAIR",
    }
    mission.update(overrides)
    return mission


def base_admission(**overrides):
    admission = {
        "mission_id": "method-enforcement-1",
        "mission_kind": "BUILDER",
        "receipt_timestamp": "2026-11-02T00:44:00+01:00",
        "project_canonical_sha": "p1",
        "code_canonical_sha": "c1",
        "current_router_identity": "governance/CURRENT_PROJECT_STATE.md@r1",
        "current_subject": {"project_sha": "p1", "code_sha": "c1", "object": "AI method enforcement seam"},
        "current_blocker_or_decision": "METHOD_REAL_AGENT_ENFORCEMENT=NOT_PROVEN",
        "target_gate_or_blocker": "F1_RECOVERABLE_CANONICAL_STATE",
        "existing_capability": "REPAIR",
        "why_this_work_can_change_the_decision": "bind real missions to fresh canonical identity",
        "minimal_decisive_test": "real receipt accepted; stale/copy rejected",
        "counterexample": "agent can still push material work with copied receipt",
        "durable_output_required": "exact SHA + run + router status",
        "next_action_after_pass_fail_block": "run fresh-agent recovery or record bounded environment block",
        "owner_authorization_required": False,
        "owner_authorized": True,
        "active_seam": "AI_WORKING_METHOD_ENFORCEMENT",
        "active_decision_lanes": 1,
        "mutating_builders_on_seam": 1,
        "requested_action": "REPAIR",
    }
    admission.update(overrides)
    return admission


def validate(admission, **kwargs):
    return validate_real_mission_admission(
        contract(), admission,
        current_project_sha=kwargs.get("project", "p1"),
        current_code_sha=kwargs.get("code", "c1"),
        current_router_identity=kwargs.get("router", "governance/CURRENT_PROJECT_STATE.md@r1"),
        expected_mission_id=kwargs.get("mission_id", "method-enforcement-1"),
    )


def base_completion(admission=None, **overrides):
    admission = admission or base_admission()
    completion = {
        "mission_id": admission["mission_id"],
        "admission_identity": canonical_json_identity(admission),
        "project_sha": "p1",
        "subject_sha": "c2",
        "tested_sha": "c2",
        "claim": "PASS",
        "durable_remote_output": True,
        "next_action": "run fresh-agent recovery",
    }
    completion.update(overrides)
    return completion


def test_contract_shape_is_bounded_and_two_branch():
    assert validate_contract(contract()) == []


def test_stale_subject_requires_reconcile():
    assert evaluate_mission(contract(), base_mission(current_subject_fresh=False)) == "RECONCILE_REQUIRED"


def test_local_only_work_cannot_be_pass():
    assert evaluate_mission(contract(), base_mission(claim="PASS", durable_remote_output=False)) == "INVALID_LOCAL_ONLY_PASS"


def test_wrong_sha_cannot_qualify_current_subject():
    assert evaluate_mission(contract(), base_mission(qualification_claim=True, subject_sha="abc", tested_sha="def")) == "INVALID_WRONG_SHA_QUALIFICATION"


def test_build_rejected_when_connect_exists():
    assert evaluate_mission(contract(), base_mission(requested_action="BUILD", existing_capability="CONNECT")) == "REJECT_UNNECESSARY_BUILD"


def test_review_without_new_decision_evidence_stops():
    assert evaluate_mission(contract(), base_mission(mission_kind="REVIEW", new_exact_subject=False, new_evidence=False, new_counterexample_class=False, new_primary_object=False, irreversible_boundary=False)) == "NO_CHANGE_REQUIRED"


def test_external_block_does_not_global_stop_independent_lane():
    assert evaluate_mission(contract(), base_mission(external_block=True, independent_lane_available=True)) == "PARK_BLOCKED_LANE_CONTINUE_INDEPENDENT"


def test_irreversible_action_requires_owner_when_contract_says_so():
    assert evaluate_mission(contract(), base_mission(irreversible_action=True, owner_authorization_required=True, owner_authorized=False)) == "BLOCK_OWNER_AUTHORITY"


def test_wip_limit_rejects_third_decision_lane():
    assert evaluate_mission(contract(), base_mission(active_decision_lanes=3)) == "BLOCK_WIP_LIMIT"


def test_checkpoint_must_leave_next_action():
    checkpoint = {"subject": "abc", "completed": "repair", "tests_executed": ["x"], "decision_changed": "F2 closed", "blockers_unknowns": [], "next_action": ""}
    assert "checkpoint missing next_action" in validate_checkpoint(contract(), checkpoint)


def test_project_cannot_finish_with_vm_gate_unproven():
    gates = {gate["id"]: "PASS" for gate in contract()["finish_gates"]}
    gates["F3_REAL_VM_MULTI_WAKE"] = "BLOCK"
    assert project_finish_status(contract(), gates) == "NOT_FINISHED"


def test_project_finishes_only_when_all_engineering_autonomy_gates_pass():
    gates = {gate["id"]: "PASS" for gate in contract()["finish_gates"]}
    assert project_finish_status(contract(), gates) == "QUANT_SYSTEM_V1_FINISHED"


def test_two_branch_gate_allows_migration_but_can_be_hardened():
    c = contract()
    assert validate_remote_branches(c, ["project/canonical", "code/canonical", "legacy/x"]) == []
    c["two_branch_mode"] = "ENFORCED"
    errors = validate_remote_branches(c, ["project/canonical", "code/canonical", "legacy/x"])
    assert any("extra remote branches forbidden" in error for error in errors)


def test_code_agents_entrypoint_must_not_route_through_old_blue():
    good = "project/canonical code/canonical governance/CURRENT_PROJECT_STATE.md governance/AI_WORKING_METHOD_V1.md"
    assert validate_agents_entrypoint(good) == []
    bad = good + " BLUE_CONTEXT_REACQUISITION_F11_2026-09-21.md"
    assert validate_agents_entrypoint(bad)


# Real-interface adversarial tests E6.
def test_real_admission_accepts_fresh_exact_subject():
    assert validate(base_admission()) == []


def test_a_stale_sha_receipt_rejected():
    errors = validate(base_admission(), code="c2")
    assert "STALE_CODE_SHA" in errors


def test_b_copied_receipt_rejected_by_mission_identity():
    errors = validate(base_admission(mission_id="old-unrelated"))
    assert "COPIED_RECEIPT_MISSION_MISMATCH" in errors


def test_c_unnecessary_build_rejected():
    errors = validate(base_admission(existing_capability="CONNECT", requested_action="BUILD"))
    assert "BUILD_WHEN_REUSE_CONNECT_REPAIR_EXISTS" in errors


def test_d_duplicate_review_rejected():
    errors = validate(base_admission(mission_kind="REVIEW"))
    assert "REVIEW_WITHOUT_NEW_SUBJECT_EVIDENCE_COUNTEREXAMPLE_OR_IRREVERSIBLE_BOUNDARY" in errors


def test_e_local_only_pass_rejected_at_completion():
    admission = base_admission()
    errors = validate_completion_binding(contract(), admission, base_completion(admission, durable_remote_output=False), current_project_sha="p1", current_code_sha="c2")
    assert "LOCAL_ONLY_PASS" in errors


def test_f_local_blocker_cannot_global_stop_independent_lane():
    errors = validate(base_admission(local_blocker=True, global_stop_requested=True, independent_lane_available=True))
    assert "LOCAL_BLOCKER_CAUSING_UNJUSTIFIED_GLOBAL_STOP" in errors


def test_g_missing_next_action_rejected():
    errors = validate(base_admission(next_action_after_pass_fail_block=""))
    assert "MISSING_NEXT_ACTION_AFTER_PASS_FAIL_BLOCK" in errors or "MISSING_NEXT_ACTION" in errors


def test_h_false_finish_rejected():
    admission = base_admission()
    gates = {gate["id"]: "PASS" for gate in contract()["finish_gates"]}
    gates["F3_REAL_VM_MULTI_WAKE"] = "UNKNOWN"
    completion = base_completion(admission, claim="QUANT_SYSTEM_V1_FINISHED", finish_gate_statuses=gates)
    errors = validate_completion_binding(contract(), admission, completion, current_project_sha="p1", current_code_sha="c2")
    assert "FALSE_FINISH_WITH_OPEN_BLOCK_UNKNOWN_GATE" in errors


def test_i_head_moved_after_admission_requires_reconcile():
    errors = validate(base_admission(), code="c2")
    assert "STALE_CODE_SHA" in errors


def test_j_concurrent_same_seam_builders_rejected():
    errors = validate(base_admission(mutating_builders_on_seam=2))
    assert "CONCURRENT_SAME_SEAM_BUILDERS" in errors


def test_wrong_sha_completion_rejected():
    admission = base_admission()
    errors = validate_completion_binding(contract(), admission, base_completion(admission, subject_sha="old", tested_sha="old"), current_project_sha="p1", current_code_sha="c2")
    assert "WRONG_SHA_SUBJECT" in errors
    assert "WRONG_SHA_QUALIFICATION" in errors


def test_completion_is_bound_to_immutable_admission_identity():
    admission = base_admission()
    completion = base_completion(admission)
    assert validate_completion_binding(contract(), admission, completion, current_project_sha="p1", current_code_sha="c2") == []
    completion["admission_identity"] = "sha256:copied"
    assert "ADMISSION_IDENTITY_MISMATCH" in validate_completion_binding(contract(), admission, completion, current_project_sha="p1", current_code_sha="c2")


def test_data_feed_only_push_is_not_material_ai_mission():
    assert material_change_requires_admission(["data/feeds/_runs.jsonl", "data/feeds/x.jsonl"], contract()) is False


def test_code_or_workflow_change_requires_real_admission():
    assert material_change_requires_admission(["scripts/validate_ai_working_method.py"], contract()) is True

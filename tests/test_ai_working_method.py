from scripts.validate_ai_working_method import (
    evaluate_mission,
    project_finish_status,
    validate_agents_entrypoint,
    validate_checkpoint,
    validate_contract,
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


def test_contract_shape_is_bounded_and_two_branch():
    assert validate_contract(contract()) == []


def test_stale_subject_requires_reconcile():
    assert evaluate_mission(contract(), base_mission(current_subject_fresh=False)) == "RECONCILE_REQUIRED"


def test_local_only_work_cannot_be_pass():
    assert evaluate_mission(
        contract(), base_mission(claim="PASS", durable_remote_output=False)
    ) == "INVALID_LOCAL_ONLY_PASS"


def test_wrong_sha_cannot_qualify_current_subject():
    assert evaluate_mission(
        contract(),
        base_mission(qualification_claim=True, subject_sha="abc", tested_sha="def"),
    ) == "INVALID_WRONG_SHA_QUALIFICATION"


def test_build_rejected_when_connect_exists():
    assert evaluate_mission(
        contract(), base_mission(requested_action="BUILD", existing_capability="CONNECT")
    ) == "REJECT_UNNECESSARY_BUILD"


def test_review_without_new_decision_evidence_stops():
    assert evaluate_mission(
        contract(),
        base_mission(
            mission_kind="REVIEW",
            new_exact_subject=False,
            new_evidence=False,
            new_counterexample_class=False,
            new_primary_object=False,
            irreversible_boundary=False,
        ),
    ) == "NO_CHANGE_REQUIRED"


def test_external_block_does_not_global_stop_independent_lane():
    assert evaluate_mission(
        contract(), base_mission(external_block=True, independent_lane_available=True)
    ) == "PARK_BLOCKED_LANE_CONTINUE_INDEPENDENT"


def test_irreversible_action_requires_owner_when_contract_says_so():
    assert evaluate_mission(
        contract(),
        base_mission(
            irreversible_action=True,
            owner_authorization_required=True,
            owner_authorized=False,
        ),
    ) == "BLOCK_OWNER_AUTHORITY"


def test_wip_limit_rejects_third_decision_lane():
    assert evaluate_mission(contract(), base_mission(active_decision_lanes=3)) == "BLOCK_WIP_LIMIT"


def test_checkpoint_must_leave_next_action():
    checkpoint = {
        "subject": "abc",
        "completed": "repair",
        "tests_executed": ["x"],
        "decision_changed": "F2 closed",
        "blockers_unknowns": [],
        "next_action": "",
    }
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

from scripts.validate_durable_continuation import validate_durable_continuation


def contract():
    return {
        "mission_admission": {
            "required_fields": ["completion_intent"],
        },
        "durable_continuation": {
            "enabled": True,
            "admission_field": "completion_intent",
            "allowed_intents": ["CHECKPOINT", "FINAL_HANDOFF"],
            "checkpoint_claim": "CHECKPOINT",
            "final_handoff_claim": "PASS",
            "canonical_router": "governance/CURRENT_PROJECT_STATE.md",
            "router_markers": {
                "mission_id": "LAST_MATERIAL_HANDOFF_MISSION",
                "result": "LAST_MATERIAL_HANDOFF_RESULT",
                "subject_sha": "LAST_MATERIAL_HANDOFF_SUBJECT",
                "next_action": "LAST_MATERIAL_HANDOFF_NEXT_ACTION",
                "reopen_condition": "LAST_MATERIAL_HANDOFF_REOPEN_CONDITION",
            },
        },
    }


def admission(intent="FINAL_HANDOFF"):
    return {
        "mission_id": "continuation-1",
        "completion_intent": intent,
        "handoff_result": "PASS",
        "handoff_subject_sha": "c1",
        "handoff_reopen_condition": "new contradictory primary evidence",
        "next_action_after_pass_fail_block": "continue F3 predeployment",
    }


def completion(adm, claim="PASS"):
    result = {
        "claim": claim,
        "durable_remote_output": True,
    }
    if adm["completion_intent"] == "FINAL_HANDOFF":
        result.update(
            {
                "handoff_router_identity": "governance/CURRENT_PROJECT_STATE.md@r1",
                "handoff_mission_id": adm["mission_id"],
                "handoff_result": adm["handoff_result"],
                "handoff_subject_sha": adm["handoff_subject_sha"],
                "handoff_next_action": adm["next_action_after_pass_fail_block"],
                "handoff_reopen_condition": adm["handoff_reopen_condition"],
            }
        )
    return result


def router_text(adm):
    return f"""
## Latest material handoff
`LAST_MATERIAL_HANDOFF_MISSION={adm["mission_id"]}`
`LAST_MATERIAL_HANDOFF_RESULT={adm["handoff_result"]}`
`LAST_MATERIAL_HANDOFF_SUBJECT={adm["handoff_subject_sha"]}`
`LAST_MATERIAL_HANDOFF_NEXT_ACTION={adm["next_action_after_pass_fail_block"]}`
`LAST_MATERIAL_HANDOFF_REOPEN_CONDITION={adm["handoff_reopen_condition"]}`
"""


def validate(adm, comp, router=""):
    return validate_durable_continuation(
        contract(),
        adm,
        comp,
        current_router_identity="governance/CURRENT_PROJECT_STATE.md@r1",
        router_text=router,
    )


def test_checkpoint_cannot_claim_authoritative_pass():
    adm = admission("CHECKPOINT")
    assert "CHECKPOINT_CANNOT_CLAIM_PASS" in validate(adm, completion(adm, "PASS"))


def test_checkpoint_can_qualify_without_router_handoff():
    adm = admission("CHECKPOINT")
    assert validate(adm, completion(adm, "CHECKPOINT")) == []


def test_final_handoff_requires_canonical_router_proof():
    adm = admission()
    errors = validate(adm, completion(adm), router="")
    assert "CANONICAL_HANDOFF_MISSION_ID_MISMATCH" in errors


def test_final_handoff_passes_only_when_router_matches():
    adm = admission()
    assert validate(adm, completion(adm), router=router_text(adm)) == []


def test_declared_durable_output_fails_when_router_next_action_is_stale():
    adm = admission()
    stale = router_text(adm).replace(adm["next_action_after_pass_fail_block"], "old next action")
    errors = validate(adm, completion(adm), router=stale)
    assert "CANONICAL_HANDOFF_NEXT_ACTION_MISMATCH" in errors

from __future__ import annotations

from copy import deepcopy

from research.research_os.research_intelligence import (
    capability_route_status,
    choose_next_action,
    classify_frontier,
    decide_candidate,
    evaluate_search_space,
)

AUTH = {
    "economic_experiment_authorized": False,
    "prospective_observation_authorized": False,
    "real_capital_authorized": False,
    "live_trading_authorized": False,
}
CAPS = {
    "capabilities": [
        {"capability_id": "quant_mechanisms", "production_enabled": True},
        {"capability_id": "source_qualification", "production_enabled": True},
        {"capability_id": "validator", "production_enabled": True},
    ]
}
LANES = {
    "lanes": [
        {"lane_id": "market_discovery", "capabilities": ["quant_mechanisms"]},
        {"lane_id": "evidence_data", "capabilities": ["source_qualification"]},
        {"lane_id": "independent_challenge", "capabilities": ["validator"]},
    ]
}


def identity(**overrides):
    base = {
        "mechanism": "forced benchmark rebalance",
        "payer": "benchmark trackers",
        "constrained_actor": "passive index funds",
        "timing_clock": "effective close",
        "universe": "us equities",
        "economic_exposure": "closing auction liquidity",
        "instrument": "equity",
        "source_family": "index rulebook",
        "evidence_identity": "sha256:doc-a",
    }
    base.update(overrides)
    return base


def candidate(cid="C1", **overrides):
    base = {
        "candidate_id": cid,
        "label": "whatever marketing name",
        "identity": identity(),
        "required_capability": "quant_mechanisms",
        "target_lane": "market_discovery",
        "actions": [
            {
                "action": "RUN_PRODUCER",
                "cost_units": 2,
                "depth": "DEEP",
                "deep_justification": "only after documentary falsifier",
                "is_falsifier": True,
                "required_capability": "quant_mechanisms",
                "target_lane": "market_discovery",
            },
            {
                "action": "ARCHAEOLOGY_LOOKUP",
                "cost_units": 0,
                "depth": "WIDE",
                "is_falsifier": True,
            },
        ],
    }
    base.update(overrides)
    return base


def memory(disposition="NEGATIVE", **overrides):
    ident = {
        "research_family_id": "family-a",
        "mechanism": "forced benchmark rebalance",
        "protocol_id": "p1",
        "universe": "us equities",
        "instrument": "equity",
        "timing_clock": "effective close",
        "horizon": "close",
        "evidence_identity": "sha256:doc-a",
        "evidence_time_boundary": "2026-01-01T00:00:00Z",
    }
    facets = {
        "mechanism": ident["mechanism"],
        "payer": "benchmark trackers",
        "constrained_actor": "passive index funds",
        "timing_clock": ident["timing_clock"],
        "universe": ident["universe"],
        "instrument": ident["instrument"],
        "evidence_identity": ident["evidence_identity"],
        "failure_reason": [],
        "protocol_weakness": [],
        "source_family": "index rulebook",
        "economic_exposure": "closing auction liquidity",
    }
    epistemic = {
        "NEGATIVE": ("KNOWN_NEGATIVE", "NEGATIVE_SCOPE_ONLY"),
        "BLOCKED": ("UNKNOWN", "UNKNOWN_ONLY"),
        "UNEXECUTED": ("UNKNOWN", "UNKNOWN_ONLY"),
        "POSITIVE_BUT_INSUFFICIENT": ("KNOWN_POSITIVE_INSUFFICIENT", "SIGNAL_NOT_PROOF"),
        "INVALIDATED_PROTOCOL": ("PROTOCOL_INVALID", "PROTOCOL_WEAKNESS_ONLY"),
        "SCIENTIFIC_MEMORY_ONLY": ("MEMORY_ONLY", "MEMORY_ONLY"),
    }[disposition]
    record = {
        "schema_version": "scientific-memory-v1",
        "memory_id": "smem:test",
        "semantic_key": "abc",
        "canonical": True,
        "scientific_disposition": disposition,
        "epistemic_status": epistemic[0],
        "claim_ceiling": epistemic[1],
        "record_status": "ACTIVE",
        "identity": ident,
        "evidence": {},
        "provenance": [{"kind": "RESULT_ARTIFACT", "ref": "artifact.json"}],
        "reason_codes": [],
        "query_facets": facets,
        "session_authority": {
            "economic_experiment_authorized": False,
            "prospective_observation_authorized": False,
            "real_capital_authorized": False,
            "live_trading_authorized": False,
            "outcome_accessed": False,
        },
        "supersession": None,
        "governance_refs": [],
        "source_identity": {"hypothesis_id": "OLD-NAME"},
    }
    for key, value in overrides.items():
        if key == "identity":
            record["identity"].update(value)
        elif key == "query_facets":
            record["query_facets"].update(value)
        else:
            record[key] = value
    return record


def decide(c, memories=(), budget=None, caps=CAPS, lanes=LANES):
    return decide_candidate(
        c,
        memory_records=memories,
        capability_registry=caps,
        workflow_lanes=lanes,
        authority=AUTH,
        budget_context={"remaining_units": 10} if budget is None else budget,
    )


def test_negative_family_resurfaces_under_rename_is_suppressed():
    d = decide(candidate(cid="RENAMED", label="brand new label"), [memory("NEGATIVE")])
    assert d["action"] == "NO_BUILD"
    assert "KNOWN_NEGATIVE_SAME_SEMANTIC_FAMILY" in d["reason_codes"]


def test_blocked_never_becomes_negative_and_can_reopen():
    blocked = memory("BLOCKED")
    parked = decide(candidate(), [blocked])
    assert parked["action"] == "PARK"
    assert "HISTORICAL_BLOCKER_UNRESOLVED_NOT_NEGATIVE" in parked["reason_codes"]
    reopened = decide(candidate(memory_blockers_resolved=True), [blocked])
    assert reopened["action"] != "NO_BUILD"
    assert "HISTORICAL_BLOCKER_RESOLVED_REOPENED" in reopened["reason_codes"]


def test_unexecuted_is_not_failed():
    d = decide(candidate(), [memory("UNEXECUTED")])
    assert d["action"] != "NO_BUILD"
    assert "HISTORICAL_UNEXECUTED_IS_NOT_FAILURE" in d["reason_codes"]


def test_invalid_protocol_cannot_rerun_unchanged():
    d = decide(candidate(protocol_id="p1"), [memory("INVALIDATED_PROTOCOL")])
    assert d["action"] == "REPAIR_PROTOCOL"
    assert "INVALIDATED_PROTOCOL_MUST_CHANGE_BEFORE_RERUN" in d["reason_codes"]


def test_invalid_protocol_changed_can_continue():
    d = decide(candidate(protocol_id="p2"), [memory("INVALIDATED_PROTOCOL")])
    assert d["action"] == "ARCHAEOLOGY_LOOKUP"


def test_unknown_identity_is_not_novelty():
    c = candidate()
    c["identity"]["payer"] = "UNKNOWN"
    d = decide(c)
    assert d["action"] == "ARCHAEOLOGY_LOOKUP"
    assert "UNKNOWN_IDENTITY_IS_NOT_NOVELTY" in d["reason_codes"]
    assert not d["identity"]["resolved"]


def test_same_evidence_under_new_path_reused_not_new():
    c = candidate(evidence_reuse_admissible=True, source_path="renamed/copied/file.json")
    d = decide(c, [memory("SCIENTIFIC_MEMORY_ONLY")])
    assert d["action"] == "REUSE_EXISTING_EVIDENCE"
    assert "PATH_RENAME_DOES_NOT_CREATE_EVIDENCE" in d["reason_codes"]


def test_cheap_falsifier_before_expensive_deep_action():
    c = candidate(actions=[
        {"action": "RUN_PRODUCER", "cost_units": 10, "depth": "DEEP", "deep_justification": "later", "is_falsifier": True, "required_capability": "quant_mechanisms", "target_lane": "market_discovery"},
        {"action": "ARCHAEOLOGY_LOOKUP", "cost_units": 0, "depth": "WIDE", "is_falsifier": True},
    ])
    assert decide(c)["action"] == "ARCHAEOLOGY_LOOKUP"


def test_declared_capability_without_route_is_not_available():
    lanes = {"lanes": [{"lane_id": "market_discovery", "capabilities": []}]}
    c = candidate(actions=[{"action": "RUN_PRODUCER", "cost_units": 1, "depth": "WIDE", "is_falsifier": True, "required_capability": "quant_mechanisms", "target_lane": "market_discovery"}])
    d = decide(c, lanes=lanes)
    assert d["action"] == "PARK"
    assert "ROUTE_CAPABILITY_MISMATCH" in d["blockers"]


def test_authority_sealed_action_is_not_selected_executable():
    c = candidate(actions=[{"action": "RUN_PRODUCER", "cost_units": 0, "depth": "WIDE", "is_falsifier": True, "required_capability": "quant_mechanisms", "target_lane": "market_discovery", "requires_authority": ["prospective_observation_authorized"]}])
    d = decide(c)
    assert d["action"] == "PARK"
    assert "AUTHORITY_SEALED" in d["reason_codes"]
    assert d["executable"] is False


def test_queue_empty_is_not_false_exhaustion():
    out = classify_frontier([], queue_active_count=0)
    assert out["state"] == "SEARCH_SPACE_INCOMPLETE"
    assert out["scientifically_exhausted"] is False


def test_only_duplicates_is_distinct_from_exhausted():
    decisions = evaluate_search_space([candidate("A"), candidate("B")], capability_registry=CAPS, workflow_lanes=LANES, authority=AUTH, budget_context={"remaining_units": 10})
    assert decisions[1]["action"] == "NO_BUILD"
    out = classify_frontier([decisions[1]], queue_active_count=0)
    assert out["state"] == "DUPLICATE_ONLY"
    assert out["scientifically_exhausted"] is False


def test_two_distinct_mechanisms_with_same_label_are_not_merged():
    a = candidate("A", label="same")
    b = candidate("B", label="same", identity=identity(mechanism="dealer balance sheet window dressing"))
    decisions = evaluate_search_space([a, b], capability_registry=CAPS, workflow_lanes=LANES, authority=AUTH, budget_context={"remaining_units": 10})
    assert decisions[1]["action"] != "NO_BUILD"


def test_positive_but_insufficient_does_not_promote_to_producer():
    c = candidate(actions=[{"action": "RUN_PRODUCER", "cost_units": 0, "depth": "WIDE", "is_falsifier": True, "required_capability": "quant_mechanisms", "target_lane": "market_discovery"}])
    d = decide(c, [memory("POSITIVE_BUT_INSUFFICIENT")])
    assert d["action"] == "ESCALATE_VALIDATION"
    assert "POSITIVE_BUT_INSUFFICIENT_NOT_PROMOTED" in d["reason_codes"]


def test_model_commentary_unqualified_memory_cannot_be_evidence():
    bogus = memory("NEGATIVE")
    bogus["canonical"] = False
    bogus["provenance"] = [{"kind": "MODEL_COMMENTARY", "ref": "chat"}]
    assert decide(candidate(), [bogus])["action"] != "NO_BUILD"


def test_wrong_semantic_identity_memory_does_not_influence_search_even_if_id_matches():
    wrong = memory("NEGATIVE")
    wrong["source_identity"]["hypothesis_id"] = "C1"
    wrong["query_facets"]["mechanism"] = "unrelated mechanism"
    wrong["identity"]["mechanism"] = "unrelated mechanism"
    assert decide(candidate("C1"), [wrong])["action"] != "NO_BUILD"


def test_stale_capability_does_not_drive_priority():
    stale = deepcopy(CAPS)
    stale["capabilities"][0]["stale"] = True
    c = candidate(actions=[{"action": "RUN_PRODUCER", "cost_units": 0, "depth": "WIDE", "is_falsifier": True, "required_capability": "quant_mechanisms", "target_lane": "market_discovery"}])
    d = decide(c, caps=stale)
    assert d["action"] == "PARK"
    assert "CAPABILITY_STALE" in d["blockers"]


def test_search_engine_never_creates_second_scheduler():
    decisions = evaluate_search_space([candidate("A")], capability_registry=CAPS, workflow_lanes=LANES, authority=AUTH, budget_context={"remaining_units": 10})
    assert decisions[0]["scheduler_mutation"] is False
    assert "task" not in decisions[0]
    assert "lease" not in decisions[0]


def test_deep_action_without_justification_fails_closed():
    c = candidate(actions=[{"action": "RUN_PRODUCER", "cost_units": 0, "depth": "DEEP", "is_falsifier": True, "required_capability": "quant_mechanisms", "target_lane": "market_discovery"}])
    d = decide(c)
    assert d["action"] == "PARK"
    assert "DEEP_ESCALATION_UNJUSTIFIED" in d["blockers"]


def test_budget_unknown_does_not_fabricate_budget_availability():
    c = candidate(actions=[{"action": "RUN_PRODUCER", "cost_units": 1, "depth": "WIDE", "is_falsifier": True, "required_capability": "quant_mechanisms", "target_lane": "market_discovery"}])
    d = decide_candidate(c, capability_registry=CAPS, workflow_lanes=LANES, authority=AUTH, budget_context=None)
    assert d["action"] == "PARK"
    assert "BUDGET_UNKNOWN" in d["blockers"]


def test_external_access_blocked_is_distinct_frontier_state():
    d = decide(candidate(external_access_required=True, external_access_available=False))
    assert classify_frontier([d], queue_active_count=0)["state"] == "EXTERNAL_ACCESS_BLOCKED"


def test_true_exhaustion_requires_explicit_complete_search_and_archaeology():
    out = classify_frontier([], queue_active_count=0, search_space_complete=True, archaeology_complete=True)
    assert out["state"] == "SCIENTIFICALLY_EXHAUSTED"
    assert out["scientifically_exhausted"] is True


def test_choose_next_action_is_pure_and_cost_ordered():
    ds = [
        {"candidate_id": "deep", "action": "RUN_PRODUCER", "executable": True, "selected_action": {"cost_units": 5}, "scheduler_mutation": False},
        {"candidate_id": "cheap", "action": "ARCHAEOLOGY_LOOKUP", "executable": True, "selected_action": {"cost_units": 0}, "scheduler_mutation": False},
    ]
    chosen = choose_next_action(ds)
    assert chosen["candidate_id"] == "cheap"
    assert chosen["scheduler_mutation"] is False


def test_capability_route_requires_both_surfaces():
    assert capability_route_status("quant_mechanisms", "market_discovery", CAPS, LANES)["available"] is True
    assert capability_route_status("missing", "market_discovery", CAPS, LANES)["state"] == "CAPABILITY_MISSING"

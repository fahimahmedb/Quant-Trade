from copy import deepcopy

import pytest

from research.research_os.discovery_engine import UNKNOWN, build_discovery_handoff


def _producer(family="QUANT_MECHANISM", hid="H-1", mechanism="Declared causal mechanism"):
    return {
        "engine_id": f"engine.{family.lower()}.test",
        "engine_family": family,
        "synthetic_only": True,
        "source_refs": [f"synthetic://{hid.lower()}"],
        "candidate": {
            "hypothesis_id": hid,
            "generation_id": "G1",
            "mechanism": mechanism,
            "claim": "Pre-outcome claim only.",
            "falsification_scope": "Kill generation if the declared mechanism premise fails.",
            "decision_map": {"supports": "EXPLORE", "fails": "KILL_GENERATION"},
            "economic_tags": ["test"],
            "horizon": "1d",
            "research_decision": "EXPLORE",
            "evidence_timing": "UNDETERMINED",
            "observation_authorization": "NOT_AUTHORIZED",
        },
    }


def _decision(hid="H-1"):
    return {
        "candidate_id": hid,
        "action": "RUN_PRODUCER",
        "executable": True,
        "scheduler_mutation": False,
        "outcome_accessed": False,
    }


def _dossier(family="QUANT_MECHANISM", hid="H-1"):
    return {
        "hypothesis_id": hid,
        "generation_id": "G1",
        "engine_family": family,
        "status": "PASS",
        "blockers": [],
        "candidate_mutated": False,
        "outcome_accessed": False,
        "claim_ceiling": "PRE_OUTCOME_MECHANISM_ONLY",
    }


def _family_evidence(family):
    if family == "QUANT_MECHANISM":
        return {"mechanism_supported": True, "statistical_signal_only": False}
    if family == "EVENT_DOCUMENT":
        return {
            "actor_security_identity_qualified": True,
            "novel_information_supported": True,
            "causal_transfer_supported": True,
            "revision_state_qualified": True,
            "reaction_horizon_qualified": True,
            "document_change_only": False,
        }
    if family == "FUNDAMENTAL":
        return {
            "issuer_security_identity_qualified": True,
            "pit_facts_qualified": True,
            "realized_vs_expected_qualified": True,
            "expectation_gap_supported": True,
            "valuation_mispricing_basis_supported": True,
            "uncertainty_qualified": True,
            "restatement_state_qualified": True,
            "good_fundamentals_only": False,
        }
    return {
        "binding_rule_supported": True,
        "actual_forced_action_supported": True,
        "eligibility_supported": True,
        "implementation_calendar_supported": True,
        "rule_exists_only": False,
    }


def _facts(family="QUANT_MECHANISM", mechanism_identity="MECH-1", exposure="EXP-1"):
    return {
        "payer": "PAYER-1",
        "causal_actor": "ACTOR-1",
        "constrained_actor": "ACTOR-1",
        "source_clocks": {
            "published_at": "2026-01-01T12:00:00Z",
            "available_at": "2026-01-01T12:05:00Z",
            "effective_at": "2026-01-01T12:06:00Z",
        },
        "entry_clock": "2026-01-01T12:10:00Z",
        "exit_clock": "2026-01-02T12:10:00Z",
        "universe": "US_EQUITY_TEST",
        "instrument": "TEST_COMMON",
        "wrapper": "COMMON_STOCK",
        "source_family": "QUALIFIED_TEST_SOURCE",
        "evidence_identity": "EVIDENCE-1",
        "expected_costs": {"status": "BOUNDED_HYPOTHESIS", "basis": "declared ex-ante model"},
        "capacity_hypothesis": {"status": "BOUNDED_HYPOTHESIS", "basis": "declared participation cap"},
        "turnover_hypothesis": "DECLARED_BOUNDED_TURNOVER",
        "crowding_hypothesis": "DECLARED_BOUNDED_CROWDING",
        "causal_timing": "trigger precedes declared entry window",
        "falsifiers": ["Declared mechanism premise fails."],
        "evidence_gaps": [],
        "claim_ceiling": "PRE_OUTCOME_MECHANISM_ONLY",
        "economic_identity_hints": {
            "mechanism_identity": mechanism_identity,
            "economic_exposure": exposure,
            "regime_identity": "REGIME-1",
            "factor_exposure": ["MARKET_BETA"],
            "beta_exposure": "DECLARED_NONZERO",
        },
        "family_evidence": _family_evidence(family),
        "source_available": True,
        "pit_feasible": True,
        "expression_feasible": True,
        "cost_model_feasible": True,
        "capacity_observable": True,
        "operational_complexity": "LOW",
        "direction_exposure_semantics": "LONG_EXPOSURE_TO_DECLARED_MECHANISM",
        "eligibility": "DECLARED_ELIGIBILITY_FILTER",
        "position_expression": "DECLARED_TEST_POSITION",
        "cost_model_requirements": "EX_ANTE_COST_BOUND",
        "capacity_requirements": "PARTICIPATION_CAP_REQUIRED",
        "data_requirements": "QUALIFIED_PIT_SOURCE",
        "execution_assumptions": "ENTRY_AFTER_AVAILABILITY_AND_EFFECTIVE_CLOCK",
        "falsification_relevant_implementation_conditions": "CLOCK_COST_OR_CAPACITY_BREACH_KILLS_GENERATION",
    }


def _run(family="QUANT_MECHANISM", hid="H-1", *, facts=None, prior=(), mechanism="Declared causal mechanism"):
    facts = deepcopy(facts if facts is not None else _facts(family))
    return build_discovery_handoff(
        _decision(hid),
        _producer(family, hid, mechanism),
        dossier=_dossier(family, hid),
        discovery_facts=facts,
        prior_candidates=prior,
    )


@pytest.mark.parametrize("family", ["QUANT_MECHANISM", "EVENT_DOCUMENT", "FUNDAMENTAL", "INSTITUTIONAL_FLOW"])
def test_all_four_families_share_one_ready_candidate_contract(family):
    result = _run(family)
    assert result["status"] == "READY_FOR_FACTORY"
    assert result["factory_handoff"]["status"] == "EXPERIMENT_READY_HANDOFF"
    assert result["candidate"]["discovery"]["producer_family"] == family
    assert result["discovery"]["implementability"]["status"] == "IMPLEMENTABLE"
    assert result["outcome_accessed"] is False
    assert all(value is False for value in result["authority"].values())


def test_candidate_extension_is_additive_and_does_not_mutate_producer_input():
    producer = _producer()
    before = deepcopy(producer)
    result = build_discovery_handoff(_decision(), producer, dossier=_dossier(), discovery_facts=_facts())
    assert producer == before
    assert "discovery" not in producer["candidate"]
    assert result["candidate"]["mechanism"] == before["candidate"]["mechanism"]
    assert result["candidate"]["discovery"]["schema_version"] == "mega-b-discovery-v1"


def test_document_change_is_not_edge():
    facts = _facts("EVENT_DOCUMENT")
    facts["family_evidence"]["document_change_only"] = True
    facts["family_evidence"]["causal_transfer_supported"] = False
    result = _run("EVENT_DOCUMENT", facts=facts)
    assert result["status"] == "BLOCKED_DISCOVERY"
    assert "DOCUMENT_CHANGE_NOT_EDGE" in result["blockers"]


def test_good_fundamentals_are_not_mispricing():
    facts = _facts("FUNDAMENTAL")
    facts["family_evidence"]["good_fundamentals_only"] = True
    facts["family_evidence"]["expectation_gap_supported"] = False
    result = _run("FUNDAMENTAL", facts=facts)
    assert "GOOD_FUNDAMENTALS_NOT_MISPRICING" in result["blockers"]


def test_rule_exists_is_not_forced_flow():
    facts = _facts("INSTITUTIONAL_FLOW")
    facts["family_evidence"]["rule_exists_only"] = True
    facts["family_evidence"]["actual_forced_action_supported"] = False
    result = _run("INSTITUTIONAL_FLOW", facts=facts)
    assert "RULE_EXISTS_NOT_FORCED_FLOW" in result["blockers"]


def test_statistical_signal_without_mechanism_is_blocked():
    facts = _facts("QUANT_MECHANISM")
    facts["family_evidence"]["statistical_signal_only"] = True
    facts["family_evidence"]["mechanism_supported"] = False
    result = _run("QUANT_MECHANISM", facts=facts)
    assert "STATISTICAL_SIGNAL_WITHOUT_MECHANISM" in result["blockers"]


def test_missing_tradable_expression_fails_closed():
    facts = _facts()
    facts["instrument"] = UNKNOWN
    facts["wrapper"] = UNKNOWN
    result = _run(facts=facts)
    assert "NO_TRADABLE_INSTRUMENT_OR_WRAPPER" in result["blockers"]
    assert "EARLY_IMPLEMENTABILITY_NOT_READY" in result["blockers"]


def test_source_time_leakage_blocks_entry_before_availability():
    facts = _facts()
    facts["entry_clock"] = "2026-01-01T12:01:00Z"
    result = _run(facts=facts)
    assert "SOURCE_TIME_LEAKAGE:ENTRY_BEFORE_AVAILABLE" in result["blockers"]


def test_outcome_payload_cannot_enter_discovery():
    facts = _facts()
    facts["pnl"] = 1.0
    result = _run(facts=facts)
    assert "OUTCOME_LEAKAGE_DETECTED" in result["blockers"]
    assert result["outcome_accessed"] is False


def test_research_intelligence_must_authorize_run_producer_without_scheduler_mutation():
    decision = _decision()
    decision["action"] = "NO_ACTION"
    result = build_discovery_handoff(decision, _producer(), dossier=_dossier(), discovery_facts=_facts())
    assert "RESEARCH_INTELLIGENCE_NOT_QUALIFIED_FOR_PRODUCER" in result["blockers"]
    assert result["scheduler_mutation"] is False


def test_same_mechanism_across_different_producer_labels_is_duplicate_without_lexical_matching():
    first = _run("EVENT_DOCUMENT", "H-EVENT", facts=_facts("EVENT_DOCUMENT", mechanism_identity="CANONICAL-MECH"), mechanism="Event wording A")
    assert first["status"] == "READY_FOR_FACTORY"
    second = _run("QUANT_MECHANISM", "H-QUANT", facts=_facts("QUANT_MECHANISM", mechanism_identity="CANONICAL-MECH"), prior=[first["candidate"]], mechanism="Totally different prose")
    duplicate = second["discovery"]["duplicate_identity"]
    assert duplicate["novelty_state"] == "DUPLICATE_MECHANISM"
    assert duplicate["lexical_similarity_used"] is False
    assert "DUPLICATE_HYPOTHESIS_NOT_NOVEL" in second["blockers"]


def test_same_exposure_under_different_wrapper_is_not_novel_expression():
    first_facts = _facts("QUANT_MECHANISM", mechanism_identity="MECH-A", exposure="EXP-SAME")
    first_facts["instrument"], first_facts["wrapper"] = "ETF-A", "ETF"
    first = _run("QUANT_MECHANISM", "H-A", facts=first_facts)
    second_facts = _facts("QUANT_MECHANISM", mechanism_identity="MECH-B", exposure="EXP-SAME")
    second_facts["instrument"], second_facts["wrapper"] = "FUT-B", "FUTURE"
    second = _run("QUANT_MECHANISM", "H-B", facts=second_facts, prior=[first["candidate"]])
    assert second["discovery"]["duplicate_identity"]["novelty_state"] == "SAME_EXPOSURE_DIFFERENT_WRAPPER"
    assert "DUPLICATE_EXPOSURE_DIFFERENT_WRAPPER" in second["blockers"]


def test_unknown_identity_never_becomes_novelty():
    facts = _facts()
    facts["economic_identity_hints"]["mechanism_identity"] = UNKNOWN
    result = _run(facts=facts)
    assert result["discovery"]["duplicate_identity"]["novelty_state"] == UNKNOWN
    assert "NOVELTY_IDENTITY_INCOMPLETE" in result["discovery"]["evidence_gaps"]
    assert "MECHANISM_IDENTITY_UNKNOWN" in result["blockers"]


def test_factory_handoff_reuses_implementability_but_does_not_cross_downstream_membranes():
    result = _run()
    handoff = result["factory_handoff"]
    assert handoff["implementability_receipt"]["implementability_status"] == "IMPLEMENTABLE"
    assert handoff["factory_law_redefined"] is False
    assert handoff["validator_invoked"] is False
    assert handoff["red_team_invoked"] is False
    assert handoff["experiment_frozen"] is False
    assert handoff["outcome_accessed"] is False

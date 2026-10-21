from research.research_os.discovery_chain import run_discovery_chain


def _decision(capability="quant_mechanisms"):
    return {
        "candidate_id": "RESEARCH-C1",
        "action": "RUN_PRODUCER",
        "executable": True,
        "reason_codes": ["CHEAPEST_ADMISSIBLE_FALSIFIER_FIRST"],
        "selected_action": {
            "action": "RUN_PRODUCER",
            "required_capability": capability,
            "target_lane": "market_discovery",
        },
        "scheduler_mutation": False,
    }


def _facts():
    return {
        "payer": "PAYER-1",
        "causal_actor": "ACTOR-1",
        "constrained_actor": "ACTOR-1",
        "source_clocks": {
            "published_at": "2026-01-01T12:00:00Z",
            "available_at": "2026-01-01T12:05:00Z",
        },
        "entry_clock": "2026-01-01T12:10:00Z",
        "exit_clock": "2026-01-02T12:10:00Z",
        "universe": "US_EQUITY_TEST",
        "instrument": "TEST_COMMON",
        "wrapper": "COMMON_STOCK",
        "source_family": "QUALIFIED_TEST_SOURCE",
        "evidence_identity": "EVIDENCE-1",
        "expected_costs": {"status": "BOUNDED_HYPOTHESIS"},
        "capacity_hypothesis": {"status": "BOUNDED_HYPOTHESIS"},
        "turnover_hypothesis": "DECLARED_BOUNDED_TURNOVER",
        "causal_timing": "trigger precedes declared entry window",
        "claim_ceiling": "PRE_OUTCOME_MECHANISM_ONLY",
        "economic_identity_hints": {
            "mechanism_identity": "MECH-ROUTED",
            "economic_exposure": "EXP-ROUTED",
            "regime_identity": "REGIME-1",
            "factor_exposure": ["MARKET_BETA"],
            "beta_exposure": "DECLARED_NONZERO",
        },
        "family_evidence": {"mechanism_supported": True, "statistical_signal_only": False},
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
        "execution_assumptions": "ENTRY_AFTER_AVAILABILITY",
        "falsification_relevant_implementation_conditions": "CLOCK_COST_OR_CAPACITY_BREACH_KILLS_GENERATION",
    }


def _quant_dossier_detail():
    return {
        "trigger": "declared trigger",
        "payer_or_forced_actor": "declared payer",
        "structural_reason": "declared structural reason",
        "expression": "declared expression",
        "universe_definition": "declared universe",
        "confounders": "declared confounders",
        "disconfirmation_checks": "declared disconfirmation",
        "outcome_accessed": False,
        "source_clock_frozen": True,
        "active_disconfirmation": True,
    }


def test_chain_executes_existing_producer_only_after_qualified_run_producer():
    result = run_discovery_chain(
        _decision(),
        engine_key="quant",
        source={"source_ref": "synthetic://mega-b-route"},
        run_id="RUN-MEGA-B",
        synthetic_only=True,
        discovery_facts=_facts(),
        dossier_detail=_quant_dossier_detail(),
    )
    assert result["status"] == "READY_FOR_FACTORY"
    assert result["producer_executed"] is True
    assert result["producer_execution_mode"] == "DIRECT_QUALIFIED_ACTION_NO_SCHEDULER"
    assert result["producer_route"]["required_capability"] == "quant_mechanisms"
    assert result["scheduler_mutation"] is False
    assert result["control_plane_mutation"] is False
    assert result["outcome_accessed"] is False


def test_capability_mismatch_blocks_before_producer_execution():
    result = run_discovery_chain(
        _decision("event_document"),
        engine_key="quant",
        source={"source_ref": "synthetic://mega-b-route"},
        run_id="RUN-MEGA-B",
        synthetic_only=True,
        discovery_facts=_facts(),
        dossier_detail=_quant_dossier_detail(),
    )
    assert result["status"] == "BLOCKED_BEFORE_PRODUCER"
    assert result["producer_executed"] is False
    assert result["blockers"] == ["RESEARCH_INTELLIGENCE_PRODUCER_CAPABILITY_MISSING_OR_MISMATCH"]

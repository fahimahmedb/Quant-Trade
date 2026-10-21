from copy import deepcopy

import pytest

from research.research_os.discovery_chain import ENGINE_ROUTES, run_discovery_chain


FAMILIES = {
    "quant": ("QUANT_MECHANISM", "quant_mechanisms"),
    "event_document": ("EVENT_DOCUMENT", "event_document"),
    "fundamental": ("FUNDAMENTAL", "fundamental"),
    "institutional_flow": ("INSTITUTIONAL_FLOW", "institutional_flows"),
}


def _decision(capability):
    return {
        "candidate_id": "RESEARCH-ROUTE",
        "action": "RUN_PRODUCER",
        "executable": True,
        "selected_action": {
            "action": "RUN_PRODUCER",
            "required_capability": capability,
            "target_lane": "market_discovery",
        },
        "scheduler_mutation": False,
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


def _facts(family):
    clocks = {
        "published_at": "2026-01-01T12:00:00Z",
        "available_at": "2026-01-01T12:05:00Z",
    }
    if family in {"EVENT_DOCUMENT", "INSTITUTIONAL_FLOW"}:
        clocks["effective_at"] = "2026-01-01T12:06:00Z"
    return {
        "payer": "PAYER-ROUTE",
        "causal_actor": "ACTOR-ROUTE",
        "constrained_actor": "ACTOR-ROUTE",
        "source_clocks": clocks,
        "entry_clock": "2026-01-01T12:10:00Z",
        "exit_clock": "2026-01-02T12:10:00Z",
        "universe": "US_EQUITY_TEST",
        "instrument": "TEST_COMMON",
        "wrapper": "COMMON_STOCK",
        "source_family": "QUALIFIED_TEST_SOURCE",
        "evidence_identity": f"EVIDENCE-{family}",
        "expected_costs": {"status": "BOUNDED_HYPOTHESIS"},
        "capacity_hypothesis": {"status": "BOUNDED_HYPOTHESIS"},
        "turnover_hypothesis": "DECLARED_BOUNDED_TURNOVER",
        "crowding_hypothesis": "DECLARED_BOUNDED_CROWDING",
        "causal_timing": "trigger precedes declared entry window",
        "claim_ceiling": "PRE_OUTCOME_MECHANISM_ONLY",
        "economic_identity_hints": {
            "mechanism_identity": f"MECH-{family}",
            "economic_exposure": f"EXP-{family}",
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
        "execution_assumptions": "ENTRY_AFTER_AVAILABILITY_AND_EFFECTIVE_IF_REQUIRED",
        "falsification_relevant_implementation_conditions": "CLOCK_COST_OR_CAPACITY_BREACH_KILLS_GENERATION",
    }


def _dossier(family):
    fields = {
        "QUANT_MECHANISM": [
            "trigger", "payer_or_forced_actor", "structural_reason", "expression",
            "universe_definition", "confounders", "disconfirmation_checks",
        ],
        "EVENT_DOCUMENT": [
            "event_identity", "document_clock", "eligibility_rule", "novel_information",
            "diffusion_hypothesis", "confounders", "disconfirmation_checks",
        ],
        "FUNDAMENTAL": [
            "issuer_identity", "financial_statements", "earnings_and_guidance",
            "estimate_revisions", "valuation_frame", "balance_sheet_quality",
            "cash_flow_quality", "competitive_position", "catalysts", "disconfirmation_checks",
        ],
        "INSTITUTIONAL_FLOW": [
            "forced_actor", "constraint_rule", "implementation_clock", "affected_universe",
            "expected_footprint", "capacity_constraints", "confounders", "disconfirmation_checks",
        ],
    }[family]
    detail = {field: f"declared {field}" for field in fields}
    detail.update(outcome_accessed=False, source_clock_frozen=True, active_disconfirmation=True)
    return detail


@pytest.mark.parametrize("engine_key", sorted(FAMILIES))
def test_all_builtin_discovery_producers_route_through_one_chain(engine_key):
    family, capability = FAMILIES[engine_key]
    assert ENGINE_ROUTES[engine_key] == (family, capability)
    result = run_discovery_chain(
        _decision(capability),
        engine_key=engine_key,
        source={"source_ref": f"synthetic://mega-b/{engine_key}"},
        run_id=f"RUN-MEGA-B-{engine_key}",
        synthetic_only=True,
        discovery_facts=deepcopy(_facts(family)),
        dossier_detail=_dossier(family),
    )
    assert result["status"] == "READY_FOR_FACTORY"
    assert result["producer_executed"] is True
    assert result["producer_route"] == {
        "engine_key": engine_key,
        "engine_family": family,
        "required_capability": capability,
    }
    assert result["candidate"]["discovery"]["producer_family"] == family
    assert result["factory_handoff"]["status"] == "EXPERIMENT_READY_HANDOFF"
    assert result["outcome_accessed"] is False
    assert result["scheduler_mutation"] is False

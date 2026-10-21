from __future__ import annotations

from copy import deepcopy
import unittest

from research.research_os.discovery_chain import ENGINE_ROUTES, run_discovery_chain
from research.research_os.discovery_engine import UNKNOWN, validate_discovery_handoff


FAMILIES = {
    "quant": ("QUANT_MECHANISM", "quant_mechanisms"),
    "event_document": ("EVENT_DOCUMENT", "event_document"),
    "fundamental": ("FUNDAMENTAL", "fundamental"),
    "institutional_flow": ("INSTITUTIONAL_FLOW", "institutional_flows"),
}


def _decision(capability: str, candidate_id: str = "RESEARCH-ROOT"):
    return {
        "candidate_id": candidate_id,
        "action": "RUN_PRODUCER",
        "executable": True,
        "selected_action": {
            "action": "RUN_PRODUCER",
            "required_capability": capability,
            "target_lane": "market_discovery",
        },
        "scheduler_mutation": False,
        "outcome_accessed": False,
    }


def _family_evidence(family: str):
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


def _facts(family: str, mechanism_identity: str | None = None, exposure: str | None = None):
    clocks = {
        "published_at": "2026-01-01T12:00:00Z",
        "available_at": "2026-01-01T12:05:00Z",
    }
    if family in {"EVENT_DOCUMENT", "INSTITUTIONAL_FLOW"}:
        clocks["effective_at"] = "2026-01-01T12:06:00Z"
    return {
        "payer": "PAYER-ROOT",
        "causal_actor": "ACTOR-ROOT",
        "constrained_actor": "ACTOR-ROOT",
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
            "mechanism_identity": mechanism_identity or f"MECH-{family}",
            "economic_exposure": exposure or f"EXP-{family}",
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
        "execution_assumptions": "ENTRY_AFTER_AVAILABLE_AND_EFFECTIVE_IF_REQUIRED",
        "falsification_relevant_implementation_conditions": "CLOCK_COST_OR_CAPACITY_BREACH_KILLS_GENERATION",
    }


def _dossier(family: str):
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


def _run(engine_key: str, *, facts=None, prior=(), decision=None):
    family, capability = FAMILIES[engine_key]
    return run_discovery_chain(
        decision or _decision(capability),
        engine_key=engine_key,
        source={"source_ref": f"synthetic://mega-b-gate/{engine_key}"},
        run_id=f"RUN-MEGA-B-GATE-{engine_key}",
        synthetic_only=True,
        discovery_facts=deepcopy(facts if facts is not None else _facts(family)),
        dossier_detail=_dossier(family),
        prior_candidates=prior,
    )


class MegaBCanonicalGateTests(unittest.TestCase):
    def test_all_four_builtin_routes_reach_common_factory_handoff(self):
        for engine_key, (family, capability) in FAMILIES.items():
            with self.subTest(engine_key=engine_key):
                self.assertEqual(ENGINE_ROUTES[engine_key], (family, capability))
                result = _run(engine_key)
                self.assertEqual(result["status"], "READY_FOR_FACTORY")
                self.assertTrue(result["producer_executed"])
                self.assertEqual(result["candidate"]["discovery"]["producer_family"], family)
                self.assertEqual(result["factory_handoff"]["status"], "EXPERIMENT_READY_HANDOFF")
                self.assertFalse(result["scheduler_mutation"])
                self.assertFalse(result["outcome_accessed"])
                self.assertTrue(all(value is False for value in result["authority"].values()))
                validate_discovery_handoff(result)

    def test_document_change_is_not_edge(self):
        facts = _facts("EVENT_DOCUMENT")
        facts["family_evidence"]["document_change_only"] = True
        facts["family_evidence"]["causal_transfer_supported"] = False
        self.assertIn("DOCUMENT_CHANGE_NOT_EDGE", _run("event_document", facts=facts)["blockers"])

    def test_good_fundamentals_are_not_mispricing(self):
        facts = _facts("FUNDAMENTAL")
        facts["family_evidence"]["good_fundamentals_only"] = True
        facts["family_evidence"]["expectation_gap_supported"] = False
        self.assertIn("GOOD_FUNDAMENTALS_NOT_MISPRICING", _run("fundamental", facts=facts)["blockers"])

    def test_rule_exists_is_not_forced_flow(self):
        facts = _facts("INSTITUTIONAL_FLOW")
        facts["family_evidence"]["rule_exists_only"] = True
        facts["family_evidence"]["actual_forced_action_supported"] = False
        self.assertIn("RULE_EXISTS_NOT_FORCED_FLOW", _run("institutional_flow", facts=facts)["blockers"])

    def test_statistical_signal_without_mechanism_is_blocked(self):
        facts = _facts("QUANT_MECHANISM")
        facts["family_evidence"]["statistical_signal_only"] = True
        facts["family_evidence"]["mechanism_supported"] = False
        self.assertIn("STATISTICAL_SIGNAL_WITHOUT_MECHANISM", _run("quant", facts=facts)["blockers"])

    def test_source_time_leakage_and_outcome_leakage_fail_closed(self):
        clock_facts = _facts("QUANT_MECHANISM")
        clock_facts["entry_clock"] = "2026-01-01T12:01:00Z"
        self.assertIn("SOURCE_TIME_LEAKAGE:ENTRY_BEFORE_AVAILABLE", _run("quant", facts=clock_facts)["blockers"])
        outcome_facts = _facts("QUANT_MECHANISM")
        outcome_facts["alpha"] = 0.1
        result = _run("quant", facts=outcome_facts)
        self.assertIn("OUTCOME_LEAKAGE_DETECTED", result["blockers"])
        self.assertFalse(result["outcome_accessed"])

    def test_recursive_outcome_aliases_fail_closed(self):
        aliases = {
            "pnl_series": [1.0],
            "unrealized_pnl": 1.0,
            "realized_return_series": [0.01],
            "price_series": [100.0],
            "fills": [{"px": 100.0}],
            "equity_curve": [1.0],
            "drawdown": -0.1,
            "win_rate": 0.6,
            "hit_rate": 0.6,
        }
        for key, value in aliases.items():
            with self.subTest(key=key):
                facts = _facts("QUANT_MECHANISM")
                facts["nested_diagnostics"] = [{"payload": {key: value}}]
                result = _run("quant", facts=facts)
                self.assertIn("OUTCOME_LEAKAGE_DETECTED", result["blockers"])
                self.assertEqual(result["factory_handoff"]["status"], "NOT_READY")
                self.assertFalse(result["outcome_accessed"])

    def test_future_effective_public_event_is_not_generic_time_leakage(self):
        facts = _facts("EVENT_DOCUMENT")
        facts["source_clocks"]["effective_at"] = "2026-02-01T00:00:00Z"
        result = _run("event_document", facts=facts)
        self.assertEqual(result["status"], "READY_FOR_FACTORY")
        self.assertEqual(result["discovery"]["source_clocks"]["entry_effective_relation"], "BEFORE_EFFECTIVE")
        self.assertNotIn("SOURCE_TIME_LEAKAGE:ENTRY_BEFORE_EFFECTIVE", result["blockers"])

    def test_future_effective_binding_rule_can_be_anticipated_only_when_flow_evidence_is_qualified(self):
        facts = _facts("INSTITUTIONAL_FLOW")
        facts["source_clocks"]["effective_at"] = "2026-02-01T00:00:00Z"
        qualified = _run("institutional_flow", facts=facts)
        self.assertEqual(qualified["status"], "READY_FOR_FACTORY")
        self.assertEqual(qualified["discovery"]["source_clocks"]["entry_effective_relation"], "BEFORE_EFFECTIVE")
        facts["family_evidence"]["implementation_calendar_supported"] = False
        blocked = _run("institutional_flow", facts=facts)
        self.assertIn("RULE_EXISTS_NOT_FORCED_FLOW", blocked["blockers"])
        self.assertIn("FLOW_IMPLEMENTATION_CALENDAR_SUPPORTED_MISSING", blocked["blockers"])

    def test_unknown_identity_stays_unknown(self):
        facts = _facts("QUANT_MECHANISM")
        facts["economic_identity_hints"]["mechanism_identity"] = UNKNOWN
        result = _run("quant", facts=facts)
        self.assertEqual(result["discovery"]["duplicate_identity"]["novelty_state"], UNKNOWN)
        self.assertIn("NOVELTY_IDENTITY_INCOMPLETE", result["discovery"]["evidence_gaps"])

    def test_same_exposure_different_wrapper_is_not_novel(self):
        first_facts = _facts("QUANT_MECHANISM", "MECH-A", "EXP-SAME")
        first_facts.update(instrument="ETF-A", wrapper="ETF")
        first = _run("quant", facts=first_facts)
        second_facts = _facts("QUANT_MECHANISM", "MECH-B", "EXP-SAME")
        second_facts.update(instrument="FUT-B", wrapper="FUTURE")
        second = _run("quant", facts=second_facts, prior=[first["candidate"]])
        self.assertEqual(second["discovery"]["duplicate_identity"]["novelty_state"], "SAME_EXPOSURE_DIFFERENT_WRAPPER")
        self.assertIn("DUPLICATE_EXPOSURE_DIFFERENT_WRAPPER", second["blockers"])

    def test_research_origin_is_lineage_not_hypothesis_identity(self):
        _, capability = FAMILIES["quant"]
        result = _run("quant", decision=_decision(capability, "RESEARCH-CANDIDATE-7"))
        ancestry = result["discovery"]["ancestry"]
        self.assertEqual(ancestry["research_origin_candidate_id"], "RESEARCH-CANDIDATE-7")
        self.assertNotEqual(ancestry["research_origin_candidate_id"], ancestry["hypothesis_id"])

    def test_discovery_and_factory_bindings_are_tamper_evident(self):
        result = _run("quant")
        validate_discovery_handoff(result)
        tampered = deepcopy(result)
        tampered["discovery"]["payer"] = "TAMPERED-PAYER"
        tampered["candidate"]["discovery"] = deepcopy(tampered["discovery"])
        tampered["factory_handoff"]["candidate"] = deepcopy(tampered["candidate"])
        tampered["factory_handoff"]["producer_output"]["candidate"] = deepcopy(tampered["candidate"])
        with self.assertRaisesRegex(ValueError, "discovery binding hash mismatch"):
            validate_discovery_handoff(tampered)

        tampered_factory = deepcopy(result)
        tampered_factory["factory_handoff"]["binding"]["candidate_hash"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "factory handoff binding hash mismatch"):
            validate_discovery_handoff(tampered_factory)

    def test_selected_action_mismatch_blocks_before_producer(self):
        decision = _decision("quant_mechanisms")
        decision["selected_action"]["action"] = "ARCHAEOLOGY_LOOKUP"
        result = _run("quant", decision=decision)
        self.assertEqual(result["status"], "BLOCKED_BEFORE_PRODUCER")
        self.assertFalse(result["producer_executed"])
        self.assertEqual(result["blockers"], ["RESEARCH_INTELLIGENCE_SELECTED_ACTION_MISMATCH"])


if __name__ == "__main__":
    unittest.main()

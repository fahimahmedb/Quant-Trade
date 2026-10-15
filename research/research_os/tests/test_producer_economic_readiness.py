from copy import deepcopy
import unittest

from research.research_os.expansion.source_qualification import (
    build_producer_test_readiness,
    qualify_producer_test_readiness,
)


def _candidate_output(family):
    return {
        "engine_family": family,
        "outcome_accessed": False,
        "economic_result": "NOT_OBSERVED",
        "candidate": {
            "hypothesis_id": f"TEST-{family}",
            "mechanism": "Documented mechanism premise; economic payoff remains untested.",
            "falsification_scope": "Reject the premise when its declared documentary preconditions fail.",
        },
    }


def _flow_detail():
    return {
        "forced_actor": {
            "status": "PARTIAL",
            "values": {
                "rule_actor": "covered broker/dealer",
                "actual_constrained_actor": "UNKNOWN",
                "forced_quantity": "UNKNOWN",
            },
        },
        "constraint_rule": {
            "status": "SUPPORTED",
            "values": {
                "rule_kind": "STANDARD_SETTLEMENT_OPERATIVE_RULE",
                "legal_basis": "OFFICIAL_CFR_2025_EDITION",
                "current_legal_status": "UNKNOWN",
            },
        },
        "implementation_clock": {
            "status": "PARTIAL",
            "values": {
                "standard_settlement_business_days": "1",
                "tradable_horizon": "UNKNOWN",
            },
        },
        "affected_universe": {
            "status": "PARTIAL",
            "values": {
                "bounded_scope": "ordinary common-equity contracts outside declared exclusions",
                "actual_eligible_quantity": "UNKNOWN",
            },
        },
    }


def _event_detail():
    return {
        "event_identity": {
            "status": "SUPPORTED",
            "values": {
                "issuer_id": "AAPL",
                "event_kind": "DECLARED_CASH_DISTRIBUTION_COMPARISON",
            },
        },
        "document_clock": {
            "status": "SUPPORTED",
            "values": {
                "publication_clock_basis": "FIRST_VERIFIED_PUBLIC_CAPTURE_NOT_HISTORICAL_PIT",
                "historical_pit": "NOT_ESTABLISHED",
            },
        },
        "eligibility_rule": {
            "status": "UNKNOWN",
            "values": {},
        },
    }


class ProducerEconomicReadinessTests(unittest.TestCase):
    def _flow_spec(self):
        return build_producer_test_readiness(
            _candidate_output("INSTITUTIONAL_FLOW"), _flow_detail()
        )["specification"]

    def _event_spec(self):
        return build_producer_test_readiness(
            _candidate_output("EVENT_DOCUMENT"), _event_detail()
        )["specification"]

    def _assert_promoted_claim_blocks(self, field, value):
        mutated = deepcopy(self._flow_spec())
        mutated["unsupported_economic_claims"][field] = value
        qualified = qualify_producer_test_readiness(mutated)
        self.assertEqual(qualified["status"], "BLOCK")
        self.assertTrue(any(field.upper() in blocker for blocker in qualified["blockers"]))

    def test_flow_readiness_closes_structure_not_economic_unknowns(self):
        result = build_producer_test_readiness(
            _candidate_output("INSTITUTIONAL_FLOW"), _flow_detail()
        )
        spec = result["specification"]
        self.assertEqual(result["qualification"]["status"], "PASS")
        self.assertEqual(spec["universe"]["status"], "PARTIAL")
        self.assertEqual(spec["clock"]["status"], "PARTIAL")
        self.assertEqual(spec["expression_requirements"]["status"], "REQUIRED")
        self.assertEqual(spec["data_requirements"]["status"], "REQUIRED")
        self.assertEqual(spec["cost_capacity_requirements"]["status"], "REQUIRED")
        self.assertEqual(
            spec["unsupported_economic_claims"],
            {
                "payer": "UNKNOWN",
                "quantity_mechanism": "UNKNOWN",
                "directional_mechanism": "UNKNOWN",
                "empirical_return": "NOT_OBSERVED",
                "capacity_estimate": "NOT_ESTIMATED",
            },
        )
        self.assertFalse(result["outcome_accessed"])

    def test_event_readiness_does_not_infer_surprise_or_market_response(self):
        result = build_producer_test_readiness(
            _candidate_output("EVENT_DOCUMENT"), _event_detail()
        )
        spec = result["specification"]
        self.assertEqual(result["qualification"]["status"], "PASS")
        self.assertEqual(spec["universe"]["status"], "PARTIAL")
        self.assertEqual(spec["clock"]["status"], "PARTIAL")
        self.assertEqual(spec["unsupported_economic_claims"]["novelty"], "UNKNOWN")
        self.assertEqual(spec["unsupported_economic_claims"]["consensus"], "UNKNOWN")
        self.assertEqual(spec["unsupported_economic_claims"]["surprise"], "UNKNOWN")
        self.assertEqual(spec["unsupported_economic_claims"]["market_response"], "NOT_OBSERVED")

    def test_quant_readiness_requires_implementability_without_backtest_result(self):
        detail = {
            "universe_definition": {
                "status": "PARTIAL",
                "values": {"instrument_class": "declared mechanism universe"},
            },
            "expression": {
                "status": "PARTIAL",
                "values": {"instrument": "declared expression", "direction": "UNKNOWN"},
            },
        }
        result = build_producer_test_readiness(
            _candidate_output("QUANT_MECHANISM"), detail
        )
        spec = result["specification"]
        self.assertEqual(result["qualification"]["status"], "PASS")
        self.assertEqual(spec["clock"]["status"], "UNKNOWN")
        self.assertEqual(spec["data_requirements"]["status"], "REQUIRED")
        self.assertEqual(spec["cost_capacity_requirements"]["status"], "REQUIRED")
        self.assertEqual(spec["unsupported_economic_claims"]["empirical_return"], "NOT_OBSERVED")

    def test_fundamental_remains_outside_prioritized_readiness_projection(self):
        with self.assertRaisesRegex(ValueError, "prioritized engine families"):
            build_producer_test_readiness(
                _candidate_output("FUNDAMENTAL"),
                {"issuer_identity": {"status": "SUPPORTED", "values": {"issuer_id": "AAPL"}}},
            )

    def test_new_claim_requires_legacy_screen_before_readiness_pass(self):
        base = self._event_spec()
        base["legacy_screen"] = {
            "status": "REQUIRED_BEFORE_NEW_CLAIM",
            "new_claim": True,
        }
        qualified = qualify_producer_test_readiness(base)
        self.assertEqual(qualified["status"], "BLOCK")
        self.assertIn("LEGACY_SCREEN_REQUIRED_BEFORE_NEW_PRODUCER_CLAIM", qualified["blockers"])

    def test_legacy_screen_pass_allows_new_claim_without_outcome_access(self):
        base = self._event_spec()
        base["legacy_screen"] = {
            "status": "PASS",
            "new_claim": True,
            "screen_id": "LEGACY-SCREEN-FIXTURE",
        }
        qualified = qualify_producer_test_readiness(base)
        self.assertEqual(qualified["status"], "PASS")
        self.assertFalse(qualified["outcome_accessed"])
        self.assertEqual(qualified["economic_result"], "NOT_OBSERVED")

    def test_payer_cannot_be_promoted_from_documentary_evidence(self):
        self._assert_promoted_claim_blocks("payer", "identified payer")

    def test_quantity_mechanism_cannot_be_promoted_from_documentary_evidence(self):
        self._assert_promoted_claim_blocks("quantity_mechanism", "10% forced quantity")

    def test_directional_mechanism_cannot_be_promoted_from_documentary_evidence(self):
        self._assert_promoted_claim_blocks("directional_mechanism", "forced buying")

    def test_surprise_cannot_be_promoted_from_documentary_evidence(self):
        self._assert_promoted_claim_blocks("surprise", "positive surprise")

    def test_market_response_cannot_be_promoted_from_documentary_evidence(self):
        self._assert_promoted_claim_blocks("market_response", "positive response")

    def test_empirical_return_cannot_be_promoted_from_documentary_evidence(self):
        self._assert_promoted_claim_blocks("empirical_return", "1.2%")

    def test_capacity_estimate_cannot_be_promoted_from_documentary_evidence(self):
        self._assert_promoted_claim_blocks("capacity_estimate", "USD 1m")

    def test_outcome_access_or_result_is_rejected(self):
        base = self._event_spec()
        base["outcome_accessed"] = True
        base["economic_result"] = "OBSERVED"
        qualified = qualify_producer_test_readiness(base)
        self.assertEqual(qualified["status"], "BLOCK")
        self.assertIn("OUTCOME_ACCESS_NOT_ALLOWED", qualified["blockers"])
        self.assertIn("ECONOMIC_RESULT_NOT_ALLOWED", qualified["blockers"])


if __name__ == "__main__":
    unittest.main()

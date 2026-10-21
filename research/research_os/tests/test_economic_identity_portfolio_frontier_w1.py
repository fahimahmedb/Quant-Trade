from __future__ import annotations

import unittest

from research.research_os.expansion.portfolio_v2 import portfolio_diagnostics_v2, structural_identity
from research.research_os.scientific_store import sha256_json


def identity(hypothesis_id: str, **overrides):
    base = {
        "hypothesis_id": hypothesis_id,
        "generation_id": "GEN-1",
        "payer": "dealer-balance-sheet",
        "forced_constrained_actor": "regulated-dealer",
        "mechanism": "balance-sheet-window",
        "instrument": "UST",
        "universe": "primary-dealers",
        "timing_clock": "quarter-end-close",
        "horizon": "1d",
        "capacity_bottleneck": {"limit": 1000, "unit": "contracts"},
        "cost_structure": {"spread_bps": 1.0, "financing_bps": 0.5},
        "economic_exposure": "quarter-end-balance-sheet-pressure",
        "event_rule_dependency": "reporting-window",
        "source_identity": "SRC-STRUCTURAL-1",
        "economic_tags": ["balance-sheet", "quarter-end"],
    }
    base.update(overrides)
    return base


def bound_identity(hypothesis_id: str, **overrides):
    value = identity(hypothesis_id, **overrides)
    candidate = {"hypothesis_id": hypothesis_id, "generation_id": "GEN-1"}
    value["candidate_snapshot"] = candidate
    value["candidate_binding"] = {
        "hypothesis_id": hypothesis_id,
        "generation_id": "GEN-1",
        "candidate_hash": sha256_json(candidate),
    }
    return value


class EconomicIdentityPortfolioFrontierW1Tests(unittest.TestCase):
    def test_nested_boolean_nonfinite_or_semantic_null_cannot_qualify_cost_capacity(self):
        cases = (
            ("capacity_bottleneck", {"limit": 1000, "enabled": True}),
            ("capacity_bottleneck", {"limit": 1000, "venue": "UNKNOWN"}),
            ("cost_structure", {"spread_bps": 1.0, "impact_bps": float("inf")}),
            ("cost_structure", {"spread_bps": 1.0, "financing_bps": "UNRESOLVED"}),
        )
        for field, payload in cases:
            with self.subTest(field=field, payload=payload):
                projected = structural_identity(identity("H1", **{field: payload}))
                self.assertEqual(projected["fields"][field]["status"], "UNKNOWN")
                self.assertEqual(projected["fields"][field]["value"], "UNKNOWN")

    def test_fully_known_structured_cost_capacity_remain_admissible(self):
        projected = structural_identity(identity("H1"))
        self.assertEqual(projected["fields"]["capacity_bottleneck"]["status"], "KNOWN")
        self.assertEqual(projected["fields"]["cost_structure"]["status"], "KNOWN")
        self.assertEqual(projected["fields"]["cost_structure"]["value"]["spread_bps"], 1.0)

    def test_mapping_readiness_is_not_pre_outcome_decision_clearance(self):
        portfolio = portfolio_diagnostics_v2([identity("H1"), identity("H2", instrument="SOFR-FUTURE")])
        self.assertEqual(portfolio["portfolio_readiness"]["structural_mapping"]["status"], "QUALIFIED_CURRENT")
        decision = portfolio["portfolio_readiness"]["pre_outcome_decision"]
        self.assertEqual(decision["status"], "PARTIAL_WITH_EXPLICIT_BLOCKER")
        self.assertTrue(any("CANDIDATE_BINDING_NOT_VERIFIED" in item for item in decision["blockers"]))
        self.assertTrue(any("SAME_EXPOSURE_REVIEW_REQUIRED" in item for item in decision["blockers"]))

    def test_distinct_complete_bound_candidates_can_clear_structural_decision_only(self):
        left = bound_identity("H1")
        right = bound_identity(
            "H2",
            payer="index-fund",
            forced_constrained_actor="passive-indexer",
            mechanism="index-rebalance",
            instrument="EQUITY-BASKET",
            universe="large-cap-index",
            timing_clock="index-close",
            horizon="5d",
            capacity_bottleneck={"limit": 500, "unit": "basket"},
            cost_structure={"spread_bps": 2.0, "financing_bps": 0.0},
            economic_exposure="index-rebalance-flow",
            event_rule_dependency="index-reconstitution",
            source_identity="SRC-STRUCTURAL-2",
        )
        portfolio = portfolio_diagnostics_v2([left, right])
        self.assertEqual(portfolio["portfolio_readiness"]["structural_mapping"]["status"], "QUALIFIED_CURRENT")
        self.assertEqual(portfolio["portfolio_readiness"]["pre_outcome_decision"]["status"], "QUALIFIED_CURRENT")
        self.assertEqual(portfolio["empirical_correlation"], "UNAVAILABLE")
        self.assertEqual(portfolio["marginal_portfolio_contribution"], "NOT_ESTIMATED")
        self.assertFalse(portfolio["return_series_consumed"])
        self.assertFalse(portfolio["economic_experiment_authorized"])
        self.assertFalse(portfolio["prospective_observation_authorized"])
        self.assertFalse(portfolio["real_capital_authorized"])
        self.assertFalse(portfolio["live_trading_authorized"])

    def test_single_candidate_mapping_is_not_a_diversification_decision(self):
        portfolio = portfolio_diagnostics_v2([bound_identity("H1")])
        self.assertEqual(portfolio["portfolio_readiness"]["structural_mapping"]["status"], "QUALIFIED_CURRENT")
        decision = portfolio["portfolio_readiness"]["pre_outcome_decision"]
        self.assertEqual(decision["status"], "PARTIAL_WITH_EXPLICIT_BLOCKER")
        self.assertIn("INSUFFICIENT_CANDIDATES_FOR_RELATIONSHIP_MAP", decision["blockers"])
        self.assertEqual(portfolio["structural_novelty"]["H1"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()

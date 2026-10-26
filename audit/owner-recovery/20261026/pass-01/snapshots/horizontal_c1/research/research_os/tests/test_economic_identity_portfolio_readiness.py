from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

from research.research_os.engines.builtin import ENGINE_REGISTRY
from research.research_os.engines.protocol import EngineContext
from research.research_os.expansion.final_shape import economic_identity_v1
from research.research_os.expansion.portfolio_v2 import (
    portfolio_diagnostics_v2,
    structural_identity,
    structural_pair,
)


BASE = Path(__file__).resolve().parents[1]


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
        "capacity_bottleneck": "dealer-balance-sheet",
        "cost_structure": "spread+financing",
        "economic_exposure": "quarter-end-balance-sheet-pressure",
        "event_rule_dependency": "reporting-window",
        "source_identity": "SRC-STRUCTURAL-1",
        "economic_tags": ["balance-sheet", "quarter-end"],
        "capital_authority": "NOT_AUTHORIZED",
    }
    base.update(overrides)
    return base


class EconomicIdentityPortfolioReadinessTests(unittest.TestCase):
    def test_same_mechanism_payer_clock_forces_high_overlap_review(self):
        left = identity("H1", instrument="UST")
        right = identity("H2", instrument="SOFR-FUTURE")
        pair = structural_pair(left, right)
        self.assertEqual(pair["classification"], "HIGH_STRUCTURAL_OVERLAP_REVIEW")
        self.assertTrue(pair["same_exposure_review_required"])
        self.assertEqual(pair["review_basis"], ["payer", "mechanism", "timing_clock"])
        self.assertEqual(pair["dimensions"]["payer"], 1.0)
        self.assertEqual(pair["dimensions"]["mechanism"], 1.0)
        self.assertEqual(pair["dimensions"]["timing_clock"], 1.0)

    def test_different_payer_and_mechanism_are_distinguishable(self):
        left = identity("H1")
        right = identity(
            "H2",
            payer="index-fund",
            mechanism="index-rebalance",
            forced_constrained_actor="passive-indexer",
            # W1 now reviews equal declared exposure even when labels differ.
            economic_exposure="index-rebalance-pressure",
        )
        pair = structural_pair(left, right)
        self.assertEqual(pair["classification"], "STRUCTURALLY_DISTINGUISHABLE")
        self.assertFalse(pair["same_exposure_review_required"])

    def test_missing_core_evidence_stays_unknown(self):
        # No known equal exposure may independently establish a related pair.
        left = identity("H1", payer="UNKNOWN", timing_clock="UNKNOWN", economic_exposure="UNKNOWN")
        right = identity("H2", payer="UNKNOWN", timing_clock="UNKNOWN", economic_exposure="UNKNOWN")
        pair = structural_pair(left, right)
        self.assertEqual(pair["classification"], "UNKNOWN")
        self.assertIn("payer", pair["unknown_dimensions"])
        self.assertIn("timing_clock", pair["unknown_dimensions"])

        projected = structural_identity(left)
        self.assertIn("payer", projected["unknown_fields"])
        self.assertEqual(projected["fields"]["payer"]["status"], "UNKNOWN")
        self.assertEqual(projected["fields"]["payer"]["value"], "UNKNOWN")

    def test_structural_similarity_never_fabricates_empirical_correlation(self):
        pair = structural_pair(identity("H1"), identity("H2"))
        self.assertEqual(pair["empirical_correlation"], "UNAVAILABLE")
        self.assertFalse(pair["return_series_consumed"])
        self.assertNotIsInstance(pair["empirical_correlation"], (int, float))

        portfolio = portfolio_diagnostics_v2([identity("H1"), identity("H2")])
        self.assertEqual(portfolio["empirical_correlation"], "UNAVAILABLE")
        self.assertEqual(portfolio["statistical_correlation_matrix"], "UNAVAILABLE_BY_DESIGN")
        self.assertFalse(portfolio["return_series_consumed"])

    def test_portfolio_contribution_remains_not_estimated_and_no_authority_exists(self):
        portfolio = portfolio_diagnostics_v2([identity("H1"), identity("H2")])
        self.assertEqual(portfolio["marginal_portfolio_contribution"], "NOT_ESTIMATED")
        self.assertFalse(portfolio["capital_allocation_authorized"])
        self.assertFalse(portfolio["position_sizing_authorized"])
        self.assertFalse(portfolio["orders_authorized"])
        self.assertFalse(portfolio["real_capital_authorized"])
        self.assertFalse(portfolio["live_trading_authorized"])
        self.assertFalse(portfolio["portfolio_optimization_authorized"])

    def test_every_structural_field_has_candidate_source_dossier_hash_generation_trace(self):
        projected = structural_identity(identity("H1"))
        expected = {
            "payer",
            "forced_constrained_actor",
            "mechanism",
            "instrument",
            "universe",
            "timing_clock",
            "horizon",
            "capacity_bottleneck",
            "cost_structure",
            "economic_exposure",
            "event_rule_dependency",
            "source_identity",
        }
        self.assertEqual(set(projected["fields"]), expected)
        for field in projected["fields"].values():
            trace = field["provenance"]
            self.assertEqual(trace["hypothesis_id"], "H1")
            self.assertEqual(trace["generation_id"], "GEN-1")
            self.assertIn("candidate_hash", trace)
            self.assertIn("source_hash", trace)
            self.assertIn("dossier_hash", trace)
            self.assertIn("identity_hash", trace)
            self.assertIn("source_path", trace)

    def test_identity_and_documentary_candidate_remain_immutable(self):
        source = json.loads((BASE / "sources/apple_fy2025_statement_cells.json").read_text())
        output = ENGINE_REGISTRY["fundamental"].run(
            source, EngineContext("IDENTITY-IMMUTABILITY", synthetic_only=False)
        )
        identity_value = economic_identity_v1(output, {})
        output_before = deepcopy(output)
        identity_before = deepcopy(identity_value)

        projected = structural_identity(identity_value)

        self.assertEqual(output, output_before)
        self.assertEqual(identity_value, identity_before)
        self.assertEqual(projected["candidate_immutable"], True)
        self.assertFalse(projected["empirical_return_data_consumed"])
        for field in projected["fields"].values():
            self.assertEqual(
                field["provenance"]["generation_id"], output["candidate"]["generation_id"]
            )


if __name__ == "__main__":
    unittest.main()

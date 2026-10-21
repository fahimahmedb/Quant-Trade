from __future__ import annotations

from copy import deepcopy
import unittest

from research.research_os.expansion.final_shape import economic_identity_v1, portfolio_map_v1
from research.research_os.expansion.portfolio_v2 import (
    portfolio_diagnostics_v2,
    structural_identity,
    structural_pair,
)


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


def synthetic_output(hypothesis_id: str, mechanism: str = "balance-sheet-window"):
    return {
        "synthetic_only": True,
        "candidate": {
            "hypothesis_id": hypothesis_id,
            "generation_id": "GEN-1",
            "mechanism": mechanism,
            "horizon": "1d",
            "economic_tags": ["balance-sheet", "quarter-end"],
        },
    }


class EconomicIdentityPortfolioDepthW1Tests(unittest.TestCase):
    def test_all_structural_unknown_is_neither_identical_nor_diversifying(self):
        fields = {
            "payer", "forced_constrained_actor", "mechanism", "instrument", "universe",
            "timing_clock", "horizon", "capacity_bottleneck", "cost_structure",
            "economic_exposure", "event_rule_dependency", "source_identity",
        }
        left = identity("H1", **{field: "UNKNOWN" for field in fields})
        right = identity("H2", **{field: "UNKNOWN" for field in fields})
        pair = structural_pair(left, right)
        self.assertEqual(pair["classification"], "UNKNOWN")
        self.assertEqual(pair["structural_overlap_score"], 0.0)
        self.assertFalse(pair["same_exposure_review_required"])
        portfolio = portfolio_diagnostics_v2([left, right])
        self.assertEqual(portfolio["structural_novelty"]["H1"], "UNKNOWN")
        self.assertEqual(portfolio["structural_novelty"]["H2"], "UNKNOWN")

    def test_explicit_canonical_mechanism_id_catches_label_variant(self):
        left = identity("H1", mechanism={
            "status": "KNOWN", "value": "Dealer balance-sheet close",
            "canonical_id": "dealer-quarter-end-balance-sheet",
        })
        right = identity("H2", mechanism={
            "status": "KNOWN", "value": "Q-end constraint",
            "canonical_id": "dealer-quarter-end-balance-sheet",
        })
        pair = structural_pair(left, right)
        self.assertEqual(pair["field_relationships"]["mechanism"]["relation"], "SAME")
        self.assertTrue(pair["same_exposure_review_required"])

    def test_only_syntactic_label_normalization_is_implicit(self):
        left = identity("H1", mechanism="Balance_Sheet Window")
        syntactic = identity("H2", mechanism="balance sheet-window")
        semantic_guess = identity("H3", mechanism="dealer constraint")
        self.assertEqual(
            structural_pair(left, syntactic)["field_relationships"]["mechanism"]["relation"],
            "SAME",
        )
        self.assertEqual(
            structural_pair(left, semantic_guess)["field_relationships"]["mechanism"]["relation"],
            "DIFFERENT",
        )

    def test_different_source_packet_is_not_independence_evidence(self):
        left = identity("H1", timing_clock="UNKNOWN", source_identity="PACKET-A")
        right = identity("H2", timing_clock="UNKNOWN", source_identity="PACKET-B")
        pair = structural_pair(left, right)
        self.assertEqual(pair["classification"], "RELATED_EXPOSURE_REVIEW")
        self.assertTrue(pair["same_exposure_review_required"])
        self.assertTrue(pair["explanation"]["source_identity_difference_is_not_independence_evidence"])

    def test_boolean_and_nonfinite_cost_capacity_are_unknown_not_evidence(self):
        projected = structural_identity(identity(
            "H1", capacity_bottleneck=True, cost_structure=float("nan")
        ))
        self.assertEqual(projected["fields"]["capacity_bottleneck"]["status"], "UNKNOWN")
        self.assertEqual(projected["fields"]["cost_structure"]["status"], "UNKNOWN")

    def test_cost_capacity_contract_preserves_assumption_and_evidence_refs(self):
        projected = structural_identity(identity(
            "H1",
            capacity_bottleneck={
                "status": "KNOWN", "value": "dealer-balance-sheet",
                "evidence_refs": ["DOC-1"], "assumption": "structural premise only",
            },
            cost_structure={
                "status": "KNOWN", "value": "spread+financing",
                "evidence_refs": ["COST-MODEL-DECL-1"], "assumption": "declared, not realized",
            },
        ))
        self.assertEqual(projected["fields"]["capacity_bottleneck"]["evidence_refs"], ["DOC-1"])
        self.assertEqual(projected["fields"]["cost_structure"]["assumption"], "declared, not realized")
        self.assertFalse(projected["empirical_return_data_consumed"])

    def test_not_applicable_does_not_count_as_same_or_different(self):
        pair = structural_pair(
            identity("H1", capacity_bottleneck="NOT_APPLICABLE"),
            identity("H2", capacity_bottleneck="NOT_APPLICABLE"),
        )
        self.assertEqual(pair["field_relationships"]["capacity_bottleneck"]["relation"], "NOT_APPLICABLE")
        self.assertIsNone(pair["dimensions"]["capacity_bottleneck"])

    def test_contradictory_clock_is_not_silently_normalized(self):
        left = identity("H1", timing_clock="quarter-end", clock="month-end")
        projected = structural_identity(left)
        self.assertEqual(projected["fields"]["timing_clock"]["status"], "CONFLICTED")
        self.assertIn("CORE_TIMING_CLOCK_CONFLICTED", projected["identity_readiness"]["blockers"])
        pair = structural_pair(left, identity("H2"))
        self.assertEqual(pair["classification"], "CONFLICTED_IDENTITY_REVIEW")
        self.assertTrue(pair["same_exposure_review_required"])

    def test_declared_candidate_binding_mismatch_is_rejected(self):
        value = identity("H1")
        value["candidate_binding"] = {
            "hypothesis_id": "H-OTHER",
            "generation_id": "GEN-1",
            "candidate_hash": "0" * 64,
        }
        with self.assertRaisesRegex(ValueError, "hypothesis binding mismatch"):
            structural_identity(value)

    def test_producer_identity_is_bound_to_candidate_snapshot(self):
        produced = economic_identity_v1(
            synthetic_output("H1"),
            {"payer": "dealer-balance-sheet", "asset": "UST"},
        )
        projected = structural_identity(produced)
        self.assertEqual(projected["candidate_binding"]["status"], "BOUND")
        self.assertEqual(
            produced["candidate_binding"]["candidate_hash"],
            projected["candidate_binding"]["candidate_hash"],
        )

        tampered = deepcopy(produced)
        tampered["candidate_snapshot"]["mechanism"] = "different-mechanism"
        with self.assertRaisesRegex(ValueError, "candidate hash binding mismatch"):
            structural_identity(tampered)

    def test_portfolio_map_v1_routes_synthetic_identities_through_canonical_v2(self):
        left = economic_identity_v1(
            synthetic_output("H1"),
            {"payer": "dealer-balance-sheet", "asset": "UST"},
        )
        right = economic_identity_v1(
            synthetic_output("H2"),
            {"payer": "dealer-balance-sheet", "asset": "SOFR-FUTURE"},
        )
        mapped = portfolio_map_v1([left, right])
        self.assertIn("structural_diagnostics", mapped)
        self.assertIn("economic_structure", mapped["pairwise"][0])
        self.assertEqual(mapped["empirical_correlation"], "UNAVAILABLE")
        self.assertFalse(mapped["return_series_consumed"])
        self.assertFalse(mapped["capital_allocation_authorized"])
        self.assertFalse(mapped["live_trading_authorized"])

    def test_memory_context_never_becomes_alpha_or_empirical_correlation(self):
        value = identity("H1", memory_refs=["MEM-HISTORICAL-POSITIVE-SIGNAL"])
        projected = structural_identity(value)
        self.assertFalse(projected["memory_context"]["expected_alpha_inferred"])
        self.assertFalse(projected["memory_context"]["empirical_correlation_inferred"])
        portfolio = portfolio_diagnostics_v2([value])
        self.assertEqual(portfolio["marginal_alpha_estimate"], "NOT_ESTIMATED")
        self.assertEqual(portfolio["empirical_correlation"], "UNAVAILABLE")
        self.assertFalse(portfolio["return_series_consumed"])

    def test_empirical_portfolio_layer_remains_explicitly_sealed(self):
        portfolio = portfolio_diagnostics_v2([identity("H1"), identity("H2")])
        self.assertEqual(portfolio["portfolio_readiness"]["empirical_layer"]["status"], "SEALED_BY_AUTHORITY")
        self.assertEqual(portfolio["marginal_portfolio_contribution"], "NOT_ESTIMATED")
        self.assertEqual(portfolio["empirical_correlation"], "UNAVAILABLE")
        self.assertFalse(portfolio["economic_experiment_authorized"])
        self.assertFalse(portfolio["prospective_observation_authorized"])
        self.assertFalse(portfolio["real_capital_authorized"])
        self.assertFalse(portfolio["live_trading_authorized"])


if __name__ == "__main__":
    unittest.main()

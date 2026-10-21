"""Missing economic identity evidence must stay unknown, not become overlap."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from research.research_os.engines.builtin import ENGINE_REGISTRY
from research.research_os.engines.protocol import EngineContext
from research.research_os.expansion.final_shape import economic_identity_v1
from research.research_os.expansion.portfolio_v2 import (
    portfolio_diagnostics_v2, structural_identity, structural_pair,
)
from research.research_os.scientific_store import sha256_json
from research.research_os.tests import test_economic_identity_portfolio_readiness as fixtures
from research.research_os.tests import test_economic_identity_memory_context_w1 as _w1_memory
from research.research_os.tests import test_economic_identity_portfolio_depth_w1 as _w1_depth
from research.research_os.tests import test_economic_identity_portfolio_frontier_w1 as _w1_frontier


def _run_w1_falsification_cases() -> None:
    """Run W1 lane cases inside the existing root test inventory."""
    for case_type in (
        _w1_memory.EconomicIdentityMemoryContextW1Tests,
        _w1_depth.EconomicIdentityPortfolioDepthW1Tests,
        _w1_frontier.EconomicIdentityPortfolioFrontierW1Tests,
    ):
        for method_name in sorted(name for name in dir(case_type) if name.startswith("test_")):
            case = case_type(methodName=method_name)
            case.setUp()
            try:
                getattr(case, method_name)()
            finally:
                case.tearDown()


class StructuralUnknownEvidenceTests(unittest.TestCase):
    def test_semantic_nulls_cannot_prove_shared_core_exposure(self):
        for value in (None, "UNKNOWN", "UNRESOLVED", "NOT_YET_MEASURABLE", "NOT_APPLICABLE",
                      "unresolved", " UNKNOWN ", " ", False, True, float("nan"), float("inf")):
            left = {"hypothesis_id": "H1", "payer": value, "mechanism": value, "timing_clock": value}
            right = dict(left, hypothesis_id="H2")
            with self.subTest(value=value):
                result = structural_pair(left, right)
                self.assertEqual(result["classification"], "UNKNOWN")
                self.assertFalse(result["same_exposure_review_required"])
                for dimension in ("payer", "mechanism", "timing_clock"):
                    self.assertIsNone(result["dimensions"][dimension])
                portfolio = portfolio_diagnostics_v2([left, right])
                self.assertEqual(portfolio["structural_novelty"], {"H1": "UNKNOWN", "H2": "UNKNOWN"})
                self.assertEqual(portfolio["same_exposure_review_pairs"], [])

    def test_empty_or_all_null_structures_stay_unknown_but_real_numeric_facts_survive(self):
        for value in ([], {}, ["UNKNOWN"], {"value": "UNRESOLVED"}, [None, False],
                      {"nested": ["NOT_YET_MEASURABLE", {}]}):
            projected = structural_identity({"hypothesis_id": "H1", "payer": value})
            with self.subTest(value=value):
                self.assertEqual(projected["fields"]["payer"]["value"], "UNKNOWN")
        for value in (0, 0.0, 1.25, 10 ** 400, {"spread": 0, "financing": 0.001}):
            projected = structural_identity({"hypothesis_id": "H1", "cost_structure": value})
            with self.subTest(value=value):
                self.assertEqual(projected["fields"]["cost_structure"]["value"], value)

    def test_placeholder_tags_do_not_inflate_overlap_or_create_empirical_claims(self):
        left = fixtures.identity("H1", economic_tags=["UNKNOWN", "real-left"])
        right = fixtures.identity("H2", economic_tags=["UNKNOWN", "real-right"])
        result = portfolio_diagnostics_v2([left, right])
        self.assertEqual(result["pairwise"][0]["dimensions"]["economic_tags"], 0.0)
        left["economic_tags"] = ["UNKNOWN"]
        self.assertIsNone(structural_pair(left, right)["dimensions"]["economic_tags"])
        self.assertEqual(result["empirical_correlation"], "UNAVAILABLE")
        self.assertEqual(result["marginal_portfolio_contribution"], "NOT_ESTIMATED")
        self.assertFalse(result["return_series_consumed"])
        for key in ("capital_allocation_authorized", "position_sizing_authorized", "orders_authorized",
                    "real_capital_authorized", "live_trading_authorized", "portfolio_optimization_authorized"):
            self.assertIs(result[key], False)

    def test_known_overlap_and_real_native_projection_keep_golden_hashes_and_inputs(self):
        self.assertEqual(sha256_json(structural_pair(fixtures.identity("H1"), fixtures.identity("H2"))),
                         "b85268f4fcaf3cf5ceb6d24c6f05185db952931845bd44f4dc86c8524a38ccb7")
        source_path = Path(__file__).resolve().parents[1] / "research/research_os/sources/apple_fy2025_statement_cells.json"
        output = ENGINE_REGISTRY["fundamental"].run(
            json.loads(source_path.read_text()), EngineContext("IDENTITY-IMMUTABILITY", synthetic_only=False))
        identity = economic_identity_v1(output, {})
        before = deepcopy(identity)
        self.assertEqual(sha256_json(structural_identity(identity)),
                         "03af5bdd581963292f10daa557c3e5feb6aeb713429cb5d8ac01155d981a4ce0")
        self.assertEqual(identity, before)
        _run_w1_falsification_cases()


if __name__ == "__main__":
    unittest.main()

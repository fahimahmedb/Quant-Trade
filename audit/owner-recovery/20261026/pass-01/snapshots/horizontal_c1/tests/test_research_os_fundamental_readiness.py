"""Connect native Fundamental metadata without promoting accounting into edge."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from research.research_os.engines.builtin import ENGINE_REGISTRY
from research.research_os.engines.protocol import EngineContext
from research.research_os.expansion.engine_dossiers_v1 import build_engine_dossier
from research.research_os.expansion.economic_test_readiness_v1 import economic_test_readiness, READY
from research.research_os.expansion.evidence_acquisition_intents_v2 import build_evidence_acquisition_intents
from research.research_os.expansion.source_qualification import (
    build_producer_test_readiness, qualify_producer_test_readiness,
)
from research.research_os.tests.test_economic_readiness_integration import fixture, legacy
from research.research_os.tests.test_producer_economic_readiness import (
    _candidate_output, _event_detail, _flow_detail,
)


class FundamentalReadinessTests(unittest.TestCase):
    def native(self):
        source = json.loads(Path("research/research_os/sources/apple_fy2025_statement_cells.json").read_text())
        output = ENGINE_REGISTRY["fundamental"].run(source, EngineContext("FUNDAMENTAL-READINESS", synthetic_only=False))
        return output, build_engine_dossier(output)

    def test_actual_accounting_support_stays_partial_without_valuation_or_trading_clock(self):
        output, dossier = self.native()
        before = deepcopy((output, dossier))
        result = build_producer_test_readiness(output, dossier["dossier"])
        spec = result["specification"]
        self.assertEqual(result["qualification"]["status"], "PASS")
        self.assertEqual(spec["universe"]["status"], "PARTIAL")
        self.assertEqual(spec["clock"], {"status": "UNKNOWN", "value": "UNKNOWN", "support": []})
        self.assertEqual(spec["documentary_support"]["financial_statements"]["status"], "PARTIAL")
        self.assertEqual(spec["documentary_support"]["valuation_frame"]["status"], "UNKNOWN")
        self.assertEqual(spec["unsupported_economic_claims"]["mispricing"], "UNKNOWN")
        self.assertEqual(dossier["status"], "BLOCK")
        self.assertEqual((output, dossier), before)

    def test_fundamental_requirements_reach_existing_acquisition_bridge_without_routes(self):
        output, dossier = self.native()
        readiness = build_producer_test_readiness(output, dossier["dossier"])
        result = build_evidence_acquisition_intents(readiness, declared_routes=[], validated_adapters={})
        self.assertEqual(result["summary"], {"requirement_count": 5, "ready_count": 0,
                                           "blocked_count": 0, "unresolved_count": 5})
        self.assertEqual(result["readiness_hash"], readiness["qualification"]["readiness_hash"])
        self.assertTrue(all(v is False for v in result["authority"].values()))
        self.assertFalse(result["network_call_performed"])

    def test_accounting_cannot_be_promoted_to_unsupported_economic_claims(self):
        output, dossier = self.native()
        for field in ("mispricing", "valuation_edge", "earnings_forecast", "rerating_alpha"):
            for value in ("positive economic claim", True, [], {"estimate": "unverified"}):
                with self.subTest(field=field, value=value):
                    result = build_producer_test_readiness(output, dossier["dossier"])
                    result["specification"]["unsupported_economic_claims"][field] = value
                    qualified = qualify_producer_test_readiness(result["specification"])
                    self.assertEqual(qualified["status"], "BLOCK")
                    self.assertIn("UNSUPPORTED_" + field.upper() + "_PROMOTED", qualified["blockers"])
                    with self.assertRaisesRegex(ValueError, "NOT_QUALIFIED"):
                        build_evidence_acquisition_intents(result, declared_routes=[], validated_adapters={})

    def test_existing_three_family_projection_hashes_remain_exactly_qualified(self):
        # Captured from exact previously qualified code 89c013b; these are
        # interface fingerprints, not empirical evidence or invented market data.
        cases = (
            ("EVENT_DOCUMENT", _event_detail(), "91e6e08c6fae031b0b9513dc178f8f460a7510460f5a1da26d5f8f8655c1d6ed"),
            ("INSTITUTIONAL_FLOW", _flow_detail(), "6550c553dfc9d71479f3fbfbd542bca7698b9ea0a4cd83a6d80c064443832b2b"),
            ("QUANT_MECHANISM", {}, "1ab3a2950dfc968425a2ed7136bd1c3a9173b166bd7109b4715efa089655e2e0"),
        )
        for family, detail, expected in cases:
            with self.subTest(family=family):
                result = build_producer_test_readiness(_candidate_output(family), detail)
                self.assertEqual(result["qualification"]["readiness_hash"], expected)

    def test_metadata_only_fundamental_package_can_freeze_replay_and_detect_mutation(self):
        package = fixture()
        package["engine_output"]["engine_family"] = "FUNDAMENTAL"
        before = deepcopy(package)
        frozen = economic_test_readiness(package, legacy=legacy())
        self.assertEqual(frozen["status"], READY, frozen["block_reasons"])
        self.assertEqual(frozen, economic_test_readiness(package, legacy=legacy(), frozen=frozen))
        self.assertEqual(frozen["remaining_execution_blockers"], ["OWNER_AUTHORIZATION"])
        self.assertTrue(all(v is False for v in frozen["authority"].values()))
        self.assertEqual(package, before)
        package["engine_output"]["candidate"]["generation_id"] = "G2"
        changed = economic_test_readiness(package, legacy=legacy(), frozen=frozen)
        self.assertEqual(changed["status"], "BLOCK")
        self.assertIn("GENERATION_BINDING_MISMATCH", changed["block_reasons"])

    def test_real_native_blocked_dossier_cannot_use_metadata_fixture_to_become_ready(self):
        output, dossier = self.native()
        package = fixture()
        package["engine_output"] = output
        package["dossier_detail"] = dossier["dossier"]
        result = economic_test_readiness(package, legacy=legacy())
        self.assertEqual(result["status"], "BLOCK")
        self.assertIn("FUNDAMENTAL_DOSSIER_NOT_QUALIFIED", result["block_reasons"])
        self.assertFalse(result["outcome_accessed"])


if __name__ == "__main__":
    unittest.main()

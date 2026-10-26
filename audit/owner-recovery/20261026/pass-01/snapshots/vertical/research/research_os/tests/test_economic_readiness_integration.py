from copy import deepcopy
import unittest

from research.research_os.legacy import LegacyKnowledgeBase
from research.research_os.scientific_store import sha256_json
from research.research_os.expansion.economic_test_readiness_v1 import AUTHORITY, READY, economic_test_readiness
from research.research_os.tests.test_implementability_depth import _complete_meta, _engine_output
from research.research_os.tests.test_experiment_runner_frozen_protocol import fixture as runner_fixture
from research.research_os.tests.test_economic_identity_portfolio_readiness import identity


def fixture():
    # Metadata only: no prices, returns, outcomes, task claims or runtime writes.
    output = _engine_output()
    output.update(engine_family="QUANT_MECHANISM", synthetic_only=True)
    output["candidate"].update(payer="fixture-payer", horizon="one interval")
    impl = _complete_meta()
    expression = impl["economic_expression"]
    _, _, meta = runner_fixture()
    protocol = meta["frozen_protocol"]
    protocol.update(
        universe={"status": "DEFINED", "universe_id": expression["universe"],
                  "definition_hash": sha256_json({"fixture": "eligible universe"}),
                  "membership_policy": "POINT_IN_TIME"},
        clock={"timezone": "UTC", "data_cutoff": "2026-10-15T10:00:00Z",
               "decision_time": "2026-10-15T10:30:00Z", "freeze_time": "2026-10-15T11:00:00Z"},
        economic_expression=deepcopy(expression), entry_definition=expression["entry_clock"],
        exit_definition=expression["exit_clock"], decision_map=output["candidate"]["decision_map"],
        cost_assumptions={"model_id": "FIXTURE-COST", "fees_bps": 0, "spread_bps": 1,
                          "slippage_bps": 2, "financing_bps": 0, "borrow_bps": 0},
        capacity_assumptions={"model_id": "FIXTURE-CAP", "max_adv_fraction": .01,
                              "evidence_ref": "fixture://declared-liquidity-contract"},
        multiplicity_method="count every attempt before outcome access",
    )
    sources = [{"route": {
        "route_id": "FIXTURE-SOURCE", "source_class": "SYNTHETIC_FIXTURE", "transport": "MEMORY",
        "locator": "fixture://metadata", "permission_state": "FIXTURE_ONLY", "pit_mode": "VERSIONED_SNAPSHOT",
        "revision_policy": "IMMUTABLE", "survivorship_policy": "PIT_MEMBERSHIP", "timezone": "UTC",
        "availability_start": "2026-10-15T09:00:00Z", "contains_outcome": False,
    }, "snapshot_hash": sha256_json({"fixture": "metadata-only snapshot"}), "available_at": "2026-10-15T09:00:00Z"}]
    meta["dataset_manifest_hash"] = sha256_json(sources)
    return {"engine_output": output, "implementability_meta": impl, "runner_meta": meta,
            "sources": sources, "validator_id": "independent-validator.v3", "authority": dict(AUTHORITY)}


def legacy():
    # A populated synthetic legacy corpus, with no outcome-bearing records.
    return LegacyKnowledgeBase({}, {"records": [{"HYPOTHESIS_ID": "LEGACY-FIXTURE-ONLY", "MECHANISM": "unrelated"}]})


class EconomicReadinessIntegrationTests(unittest.TestCase):
    def run_package(self, p=None, **kwargs):
        return economic_test_readiness(p or fixture(), legacy=legacy(), **kwargs)

    def assert_block(self, p, code, **kwargs):
        r = self.run_package(p, **kwargs)
        self.assertEqual(r["status"], "BLOCK")
        self.assertIn(code, r["block_reasons"])
        self.assertEqual(r["authority"], AUTHORITY)
        return r

    def test_full_pre_outcome_path_and_deterministic_replay(self):
        p = fixture()
        before = deepcopy(p)
        result = self.run_package(p)
        self.assertEqual(result["status"], READY, result["block_reasons"])
        self.assertEqual(result, self.run_package(p))
        self.assertEqual(result, self.run_package(p, frozen=result))
        self.assertEqual(result["deterministic_replay"]["status"], "REPLAY_MATCH")
        self.assertEqual(result["remaining_execution_blockers"], ["OWNER_AUTHORIZATION"])
        self.assertTrue(result["architecture_stop_build"])
        self.assertEqual(p, before)
        self.assertFalse(result["outcome_accessed"])
        self.assertEqual(result["economic_result"], "NOT_OBSERVED")
        self.assertEqual(result["producer_readiness"]["qualification"]["status"], "PASS")

    def test_cost_and_capacity_missing_invalid_or_unknown_block(self):
        for field, code in (("cost_assumptions", "COST_ASSUMPTIONS_INVALID"),
                            ("capacity_assumptions", "CAPACITY_ASSUMPTIONS_INVALID")):
            for value in ({}, {"model_id": "UNKNOWN"}):
                with self.subTest(field=field, value=value):
                    p = fixture()
                    p["runner_meta"]["frozen_protocol"][field] = value
                    self.assert_block(p, code)
        for value in (-1, float("inf"), True):
            p = fixture()
            p["runner_meta"]["frozen_protocol"]["capacity_assumptions"]["max_adv_fraction"] = value
            self.assert_block(p, "CAPACITY_ASSUMPTIONS_INVALID")

    def test_implementability_missing_capacity_blocks(self):
        p = fixture()
        del p["implementability_meta"]["capacity_observable"]
        self.assert_block(p, "CAPACITY_OBSERVABILITY_UNKNOWN")

    def test_source_pit_and_provenance_block(self):
        for key, value, code in (("pit_mode", "INVALID", "PIT_MODE_NOT_ALLOWED"),
                                  ("contains_outcome", True, "UNAUTHORIZED_OUTCOME_BEARING_ROUTE")):
            p = fixture()
            p["sources"][0]["route"][key] = value
            self.assert_block(p, code)
        p = fixture()
        p["sources"][0]["available_at"] = "2026-10-15T12:00:00Z"
        self.assert_block(p, "PIT_QUALIFICATION_FAILED")
        p = fixture()
        p["sources"][0]["snapshot_hash"] = "bad"
        self.assert_block(p, "SOURCE_PROVENANCE_INCOMPLETE")

    def test_candidate_protocol_source_generation_and_code_mutation_fail_closed(self):
        frozen = self.run_package()
        mutations = (
            (lambda p: p["engine_output"]["candidate"].update(claim="changed"), "CANDIDATE_BINDING_MISMATCH"),
            (lambda p: p["engine_output"]["candidate"].update(generation_id="G2"), "GENERATION_BINDING_MISMATCH"),
            (lambda p: p["runner_meta"]["frozen_protocol"].update(benchmark="changed"), "PROTOCOL_BINDING_MISMATCH"),
            (lambda p: p["sources"][0].update(snapshot_hash=sha256_json("changed")), "PROTOCOL_BINDING_MISMATCH"),
            (lambda p: p["runner_meta"].update(code_sha="changed"), "PROTOCOL_BINDING_MISMATCH"),
        )
        for mutate, code in mutations:
            with self.subTest(code=code):
                p = fixture()
                mutate(p)
                self.assert_block(p, code, frozen=frozen)

    def test_missing_multiplicity_and_trial_accounting_block_unknown_is_preserved(self):
        for key, code in (("multiplicity_family", "MULTIPLICITY_DECLARATION_MISSING"),
                          ("observed_attempt_count", "TRIAL_ACCOUNTING_INVALID")):
            p = fixture()
            del p["runner_meta"]["frozen_protocol"][key]
            self.assert_block(p, code)
        result = self.run_package()
        self.assertEqual(result["trial_accounting"]["effective_trials_status"], "UNKNOWN")
        self.assertIsNone(result["trial_accounting"]["estimated_effective_trials"])

    def test_producer_cannot_self_validate(self):
        p = fixture()
        p["validator_id"] = p["engine_output"]["engine_id"]
        self.assert_block(p, "PRODUCER_VALIDATOR_NOT_INDEPENDENT")

    def test_red_team_can_block_without_repair_or_retuning(self):
        p = fixture()
        before = deepcopy(p)
        result = self.assert_block(p, "BLOCK_LEAKAGE", red_team_context={"leakage_status": "FAIL"})
        self.assertEqual(p, before)
        for key in ("repair_attempted", "signal_repair_attempted", "parameters_optimized", "retuned_until_profitable"):
            self.assertIs(result["red_team"][key], False)

    def test_structural_duplication_blocks_without_fabricating_empirical_correlation_or_allocation(self):
        p = fixture()
        p["identity_meta"] = {"payer": "fixture-payer", "asset": "UST"}
        peer = identity(
            "PEER",
            payer="fixture-payer",
            mechanism=p["engine_output"]["candidate"]["mechanism"],
            instrument="UST",
            horizon="one interval",
            timing_clock="UNKNOWN",
        )
        result = self.run_package(p, peer_identities=[peer])
        self.assertEqual(result["status"], "BLOCK")
        self.assertIn("BLOCK_UNRESOLVED_CURRENT_EXPOSURE_OVERLAP", result["block_reasons"])
        portfolio = result["portfolio"]
        self.assertEqual(portfolio["same_exposure_review_pairs"], [])
        self.assertTrue(portfolio["readiness_blocking_review_pairs"])
        blocker = portfolio["readiness_blocking_review_pairs"][0]
        self.assertEqual(blocker["basis"], "SAME_PAYER_MECHANISM_CLOCK_UNKNOWN")
        self.assertEqual(blocker["payer"], 1.0)
        self.assertEqual(blocker["mechanism"], 1.0)
        self.assertIsNone(blocker["timing_clock"])
        self.assertEqual(
            portfolio["pairwise"][0]["economic_structure"]["classification"],
            "UNKNOWN",
        )
        self.assertEqual(portfolio["empirical_correlation"], "UNAVAILABLE")
        self.assertEqual(portfolio["marginal_portfolio_contribution"], "NOT_ESTIMATED")
        for key in ("capital_allocation_authorized", "position_sizing_authorized", "orders_authorized", "return_series_consumed"):
            self.assertIs(portfolio[key], False)

    def test_authority_barrier_rejects_every_authority_request(self):
        self.assertEqual(self.run_package()["authority"], AUTHORITY)
        for key in AUTHORITY:
            p = fixture()
            p["authority"][key] = True
            self.assert_block(p, "AUTHORITY_MUST_REMAIN_FALSE")

    def test_exact_legacy_duplicate_or_unloaded_ledger_blocks(self):
        p = fixture()
        p["engine_output"]["candidate"]["hypothesis_id"] = "LEGACY-FIXTURE-ONLY"
        self.assert_block(p, "BLOCK_EXACT_LEGACY_DUPLICATE")
        result = economic_test_readiness(fixture(), legacy=LegacyKnowledgeBase({}))
        self.assertIn("LEGACY_LEDGER_NOT_LOADED", result["block_reasons"])

    def test_frozen_receipt_tampering_blocks(self):
        frozen = self.run_package()
        frozen["experiment_plan"]["frozen_protocol"]["clock"]["timezone"] = "changed"
        self.assert_block(fixture(), "frozen protocol mutation detected", frozen=frozen)

    def test_malformed_package_fails_closed(self):
        for p in ({}, {"engine_output": None}):
            result = economic_test_readiness(p, legacy=legacy())
            self.assertEqual(result["status"], "BLOCK")
            self.assertTrue(result["block_reasons"][0].startswith("INVALID_READINESS_PACKAGE:"))
            self.assertEqual(result["authority"], AUTHORITY)

    def test_portfolio_retains_b4_diagnostics_alongside_canonical_summary(self):
        from research.research_os.expansion.portfolio_v2 import portfolio_diagnostics_v2, structural_pair
        left, right = identity("A"), identity("B")
        pair = portfolio_diagnostics_v2([left, right])["pairwise"][0]
        rich = structural_pair(left, right)
        self.assertEqual(pair["economic_structure"]["classification"], "HIGH_STRUCTURAL_OVERLAP_REVIEW")
        self.assertEqual(pair["economic_structure"]["dimensions"], rich["dimensions"])
        self.assertTrue(pair["same_exposure_review_required"])


if __name__ == "__main__":
    unittest.main()

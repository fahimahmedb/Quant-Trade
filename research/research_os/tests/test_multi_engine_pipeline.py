import json
import unittest
from pathlib import Path

from research.research_os.engines.pipeline import run_pipeline


class MultiEnginePipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base = Path(__file__).resolve().parents[1]
        fixture = json.loads((base / "simulations" / "multi_engine_fixture.json").read_text())
        cls.result = run_pipeline(fixture)

    def test_pipeline_passes(self):
        self.assertEqual(self.result["status"], "PASS")
        self.assertTrue(self.result["synthetic_only"])

    def test_all_initial_engines_present(self):
        families = {e["engine_family"] for e in self.result["engines"]}
        self.assertEqual(families, {
            "QUANT_MECHANISM",
            "FUNDAMENTAL",
            "EVENT_DOCUMENT",
            "INSTITUTIONAL_FLOW",
        })

    def test_validation_is_independent_and_clean(self):
        self.assertTrue(all(v["validator"] == "independent-validator.v0" for v in self.result["validations"]))
        self.assertTrue(all(v["status"] == "PASS" for v in self.result["validations"]))
        self.assertEqual(self.result["red_team"]["status"], "PASS")

    def test_portfolio_has_no_capital_authority(self):
        p = self.result["portfolio"]
        self.assertFalse(p["capital_allocation_authorized"])
        self.assertEqual(p["marginal_portfolio_value"], "NOT_ESTIMATED_WITHOUT_EMPIRICAL_RETURN_DATA")
        self.assertEqual(len(p["identities"]), 4)

    def test_shadow_does_not_start_observation(self):
        s = self.result["shadow"]
        self.assertFalse(s["prospective_observation_authorized"])
        self.assertTrue(all(x["observation_authorization"] == "NOT_AUTHORIZED" for x in s["registrations"]))
        self.assertTrue(all(x["observation_started"] is False for x in s["registrations"]))

    def test_authority_invariants(self):
        self.assertEqual(self.result["authorities"], {
            "real_capital": False,
            "live_trading": False,
            "prospective_observation": False,
            "economic_experiment": False,
        })

    def test_worker_events_are_native_shaped(self):
        events = self.result["worker_events"]
        self.assertGreaterEqual(len(events), 14)
        for event in events:
            self.assertIn(event["event_type"], {"ACTION_STARTED", "ACTION_COMPLETED"})
            self.assertGreaterEqual(event["event_seq"], 1)
            self.assertEqual(event["generation"], 1)


if __name__ == "__main__":
    unittest.main()

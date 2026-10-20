import unittest

from research.research_os.expansion.edge_observability_v2 import (
    EdgeObservabilityError,
    build_edge_observability_projection,
)


class EdgeObservabilityProjectionTest(unittest.TestCase):
    def task(self):
        return {"task_id": "T-1", "task_type": "EVENT_DOCUMENT"}

    def research(self):
        return {
            "authority": {
                "economic_experiment_authorized": False,
                "prospective_observation_authorized": False,
                "real_capital_authorized": False,
                "live_trading_authorized": False,
            },
            "economic_result": "NOT_OBSERVED",
            "outcome_accessed": False,
            "candidate": {"hypothesis_id": "H-1"},
            "dossier": {
                "claim_ceiling": "DOCUMENTED_FACTS_ONLY",
                "blockers": ["UNQUALIFIED_ELIGIBILITY_RULE"],
                "dossier": {
                    "document_clock": {
                        "status": "SUPPORTED",
                        "support": {"ref": "primary"},
                        "limitations": [],
                    },
                    "eligibility_rule": {
                        "status": "UNKNOWN",
                        "support": None,
                        "limitations": ["not documented"],
                    },
                    "confounders": {
                        "status": "PARTIAL",
                        "support": {"ref": "bounded"},
                        "limitations": ["market response not observed"],
                    },
                },
            },
        }

    def test_projection_exposes_missing_evidence_without_economic_claim(self):
        out = build_edge_observability_projection(task=self.task(), research=self.research())
        self.assertEqual(out["scientific_maturity"], "EVIDENCE_BOUND")
        self.assertEqual(out["experiment_readiness"], "INCOMPLETE")
        self.assertEqual(out["operational_state"], "BLOCKED")
        self.assertEqual(out["interpretation"], "BLOCKED_NOT_FAILED")
        self.assertEqual(out["economic_result"], "NOT_OBSERVED")
        self.assertEqual(out["empirical_correlation"], "UNKNOWN")
        self.assertEqual(out["evidence_maturity"]["counts"]["SUPPORTED"], 1)
        self.assertEqual(out["evidence_maturity"]["counts"]["PARTIAL"], 1)
        self.assertEqual(out["evidence_maturity"]["counts"]["UNKNOWN"], 1)
        self.assertEqual(
            [row["field"] for row in out["evidence_maturity"]["missing_evidence"]],
            ["confounders", "eligibility_rule"],
        )

    def test_blocked_attempt_is_not_relabelled_failed(self):
        out = build_edge_observability_projection(
            task={"task_id": "T-2", "task_type": "INSTITUTIONAL_FLOW"},
            research={
                "blocker": "STAGE_NOT_EXPLICITLY_AUTHORIZED:mechanism_research",
                "economic_result": "NOT_OBSERVED",
                "outcome_accessed": False,
            },
        )
        self.assertEqual(out["scientific_maturity"], "IDEA")
        self.assertEqual(out["operational_state"], "BLOCKED")
        self.assertEqual(out["interpretation"], "BLOCKED_NOT_FAILED")

    def test_ready_package_remains_pre_outcome_and_authority_closed(self):
        out = build_edge_observability_projection(
            task=self.task(),
            research={"candidate": {"hypothesis_id": "H"}, "economic_result": "NOT_OBSERVED", "outcome_accessed": False},
            disconfirmation={"attempted": True, "outcome_accessed": False},
            frozen_candidate={"candidate_hash": "abc", "outcome_accessed": False},
            validator={"scientific_decision": "PASS", "outcome_accessed": False},
            readiness={
                "status": "READY",
                "claim_ceiling": "READY_FOR_AUTHORIZED_ECONOMIC_TEST_ONLY",
                "blockers": [],
                "outcome_accessed": False,
            },
            export_intent={"evaluation_plane_status": "SEALED"},
        )
        self.assertEqual(out["scientific_maturity"], "VALIDATED")
        self.assertEqual(out["experiment_readiness"], "READY")
        self.assertEqual(out["operational_state"], "READY_PACKAGE")
        self.assertEqual(out["interpretation"], "READY_IS_NOT_PROFITABLE")
        self.assertTrue(all(value is False for value in out["authority"].values()))
        self.assertFalse(out["outcome_accessed"])

    def test_rejects_outcome_payload(self):
        with self.assertRaisesRegex(EdgeObservabilityError, "OUTCOME_FIELD_VISIBLE"):
            build_edge_observability_projection(
                task=self.task(),
                research={"pnl": 1.2},
            )

    def test_rejects_open_authority_or_observed_economic_result(self):
        with self.assertRaisesRegex(EdgeObservabilityError, "AUTHORITY_OPEN"):
            build_edge_observability_projection(
                task=self.task(),
                readiness={"authority": {"real_capital_authorized": True}},
            )
        with self.assertRaisesRegex(EdgeObservabilityError, "ECONOMIC_RESULT_VISIBLE"):
            build_edge_observability_projection(
                task=self.task(),
                research={"economic_result": "POSITIVE"},
            )


if __name__ == "__main__":
    unittest.main()

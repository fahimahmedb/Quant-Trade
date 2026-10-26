from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import (
    DeterministicFakeBackend,
    build_context_snapshot,
    policy_c,
    raw_artifact,
)


def snap():
    keys = (
        "memory_snapshot_ref", "ancestry_snapshot_ref", "frontier_snapshot_ref",
        "evidence_snapshot_ref", "source_catalog_snapshot_ref", "capability_snapshot_ref",
        "authority_snapshot_ref", "active_work_snapshot_ref",
    )
    return build_context_snapshot(
        ideation_cycle_id="nested-outcome-firewall",
        created_at="2026-10-21T20:00:00Z",
        refs={key: key for key in keys},
        relevant_schema_versions={},
    )


class NestedOutcomeFirewallTests(unittest.TestCase):
    def valid_idea(self):
        return {
            "summary": "bounded idea",
            "mechanism": "m",
            "payer": "p",
            "actor": "a",
            "clock": "c",
            "universe": "u",
            "falsifier": "f",
        }

    def test_policy_c_blocks_recursive_outcome_aliases_without_persisting_receipt(self):
        aliases = {
            "pnl": 1.0,
            "pnl_series": [1.0],
            "return": 0.01,
            "returns": [0.01],
            "return_series": [0.01],
            "realized_return_series": [0.01],
            "sharpe": 1.2,
            "alpha": 0.1,
            "empirical_correlation": 0.2,
            "price_series": [100.0],
            "fills": [{"price": 100.0}],
            "equity_curve": [1.0],
            "unrealized_pnl": 1.0,
            "win_rate": 0.5,
            "hit_rate": 0.5,
            "economic_result": "POSITIVE",
        }
        for key, value in aliases.items():
            with self.subTest(key=key):
                idea = self.valid_idea()
                idea["metadata"] = [{"claim": {key: value}}]
                artifact, receipt = policy_c(
                    snapshot=snap(),
                    backend=DeterministicFakeBackend({
                        "alternatives": [idea],
                        "selected_alternative_index": 0,
                    }),
                    mandate={},
                )
                self.assertEqual(artifact["status"], "BLOCKED")
                self.assertEqual(artifact["reason"], "OUTCOME_BEARING_MODEL_OUTPUT_FORBIDDEN")
                self.assertIsNone(receipt)
                self.assertIsNone(artifact["artifact_kind"])
                self.assertEqual(artifact["payload"], {})

    def test_raw_artifact_rejects_recursive_outcome_payload(self):
        with self.assertRaisesRegex(ValueError, "outcome-bearing ideation field forbidden"):
            raw_artifact(
                policy_kind="DIVERGENT_EXPLORATION",
                status="PROPOSAL_EMITTED",
                context_snapshot_hash="a" * 64,
                artifact_kind="IDEA_PROPOSAL",
                payload={"nested": [{"return_series": [0.1]}]},
            )

    def test_policy_c_rejects_outcome_bearing_mandate_before_backend_call(self):
        class ExplodingBackend:
            backend_identity = "must-not-run"
            model_identity = "must-not-run"

            def generate(self, mandate):
                raise AssertionError("backend must not receive outcome-bearing mandate")

        with self.assertRaisesRegex(ValueError, "outcome-bearing ideation field forbidden"):
            policy_c(
                snapshot=snap(),
                backend=ExplodingBackend(),
                mandate={"nested": {"pnl": 1.0}},
            )


if __name__ == "__main__":
    unittest.main()

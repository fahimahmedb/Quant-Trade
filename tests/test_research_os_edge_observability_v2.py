import unittest
from copy import deepcopy
import json
from unittest.mock import patch

from research.research_os.expansion.edge_observability_v2 import (
    EdgeObservabilityError,
    build_edge_observability_projection,
)
from research.research_os.expansion.source_adapters_v1 import validate_adapter_spec
from research.research_os.expansion.source_qualification import (
    PRODUCER_TEST_READINESS_FIELDS,
    qualify_producer_test_readiness,
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


class EvidenceAcquisitionObservabilityTest(unittest.TestCase):
    """Exercise the owner composition through the real bridge and firewall."""

    requirement = "declared documentary eligibility rule"

    def inputs(self, requirements=None):
        specification = {
            field: {"status": "REQUIRED", "value": ["declared fixture requirement"], "support": []}
            for field in PRODUCER_TEST_READINESS_FIELDS
        }
        specification.update({
            "engine_family": "EVENT_DOCUMENT",
            "data_requirements": {"status": "REQUIRED", "value": requirements or [self.requirement], "support": []},
            "legacy_screen": {"status": "NOT_APPLICABLE_EXISTING_BOUND_CANDIDATE", "new_claim": False},
            "unsupported_economic_claims": {"empirical_return": "NOT_OBSERVED"},
            "outcome_accessed": False,
            "economic_result": "NOT_OBSERVED",
        })
        readiness = {
            "hypothesis_id": "H-1",
            "specification": specification,
            "qualification": qualify_producer_test_readiness(specification),
            "outcome_accessed": False,
            "economic_result": "NOT_OBSERVED",
        }
        self.assertEqual(readiness["qualification"]["status"], "PASS")
        adapter = validate_adapter_spec({
            "adapter_id": "fixture-documentary.v1",
            "provider_family": "OFFICIAL_CORPORATE_ACTIONS",
            "data_class": "OFFICIAL_CORPORATE_ACTIONS",
            "permission_model": "PUBLIC",
            "clock_semantics": "PUBLICATION_TIME",
            "revision_policy": "VERSION_AS_PUBLISHED",
            "survivorship_policy": "INCLUDE_ALL_DECLARED_RECORDS",
            "locator_template": "declared-fixture-only",
            "activation_state": "DESIGN_ONLY_NOT_CONNECTED",
            "network_access": False,
            "contains_market_outcome": False,
            "allowed_content": ["official_corporate_actions"],
            "forbidden_content": ["returns"],
        })
        self.assertEqual(adapter["status"], "PASS")
        return {
            "task": {"task_id": "T-1", "task_type": "EVENT_DOCUMENT"},
            "research": {
                "candidate": {"hypothesis_id": "H-1"},
                "dossier": {"dossier": {"eligibility_rule": {"status": "UNKNOWN", "limitations": ["missing document"]}}},
            },
            "producer_readiness": readiness,
            "declared_routes": [{
                "requirement": self.requirement,
                "adapter_id": adapter["adapter_id"],
                "content_classes": ["official_corporate_actions"],
                "entity_scope": {"issuer_id": "FIXTURE"},
                "clock_cutoff": "2026-10-20T01:00:00Z",
                "version_policy": "AS_PUBLISHED_AT_OR_BEFORE_CUTOFF",
                "locator_parameters": {"private_locator": "must-not-be-displayed"},
            }],
            "validated_adapters": {adapter["adapter_id"]: adapter},
        }

    def test_ready_plan_composes_missing_evidence_without_promoting_maturity(self):
        result = build_edge_observability_projection(**self.inputs())
        acquisition = result["evidence_acquisition"]
        self.assertEqual(result["evidence_maturity"]["missing_evidence"][0]["field"], "eligibility_rule")
        self.assertEqual(acquisition["status"], "READY_PLAN_ONLY")
        row = acquisition["intents"][0]
        self.assertEqual(row["requirement"], self.requirement)
        self.assertEqual(row["firewall_status"], "READY_AWAITING_SOURCE_ACTIVATION_AUTHORITY")
        self.assertEqual(row["execution_mode"], "PLAN_ONLY_NO_NETWORK")
        self.assertTrue(row["request_id"].startswith("ACQ-"))
        self.assertEqual(result["scientific_maturity"], "EVIDENCE_BOUND")
        self.assertEqual(result["experiment_readiness"], "INCOMPLETE")
        self.assertEqual(result["claim_ceiling"], "DESIGN_ONLY")
        self.assertEqual(result["economic_result"], "NOT_OBSERVED")
        self.assertTrue(all(value is False for value in result["authority"].values()))
        self.assertFalse(result["outcome_accessed"])
        self.assertFalse(acquisition["network_execution_authorized"])
        self.assertFalse(acquisition["network_call_performed"])
        self.assertEqual(acquisition["network_connectivity"], "NOT_INSPECTED")
        self.assertNotIn("must-not-be-displayed", json.dumps(result))

    def test_missing_route_or_adapter_remains_unresolved_without_firewall_plan(self):
        for field, value, status in (
            ("declared_routes", [], "UNRESOLVED_NO_DECLARED_ROUTE"),
            ("validated_adapters", {}, "UNRESOLVED_ADAPTER_NOT_DECLARED"),
        ):
            with self.subTest(field=field):
                inputs = self.inputs()
                inputs[field] = value
                acquisition = build_edge_observability_projection(**inputs)["evidence_acquisition"]
                self.assertEqual(acquisition["status"], "INCOMPLETE_UNRESOLVED")
                self.assertEqual(acquisition["summary"]["unresolved_count"], 1)
                self.assertEqual(acquisition["intents"][0]["status"], status)
                self.assertEqual(acquisition["intents"][0]["firewall_status"], "NOT_PLANNED")
                self.assertIsNone(acquisition["intents"][0]["request_id"])

    def test_firewall_block_is_visible_with_its_actual_reasons(self):
        inputs = self.inputs()
        inputs["declared_routes"][0]["content_classes"] = ["unlisted_document"]
        acquisition = build_edge_observability_projection(**inputs)["evidence_acquisition"]
        row = acquisition["intents"][0]
        self.assertEqual(acquisition["status"], "BLOCK")
        self.assertEqual(row["status"], "BLOCK_FIREWALL")
        self.assertEqual(row["firewall_status"], "BLOCK")
        self.assertIn("CONTENT_NOT_ALLOWED:unlisted_document", row["firewall_blockers"])
        self.assertFalse(acquisition["network_execution_authorized"])

    def test_invalid_pit_version_ambiguity_and_outcome_content_remain_blocked(self):
        for overrides, expected in (
            ({"clock_cutoff": "2026-10-20T01:00:00"}, "BLOCK_INVALID_DECLARED_ROUTE"),
            ({"version_policy": "UNKNOWN"}, "BLOCK_INVALID_DECLARED_ROUTE"),
            ({"content_classes": ["returns"]}, "BLOCK_FORBIDDEN_CONTENT_CLASS"),
            ({}, "BLOCK_AMBIGUOUS_DECLARED_ROUTE"),
        ):
            with self.subTest(expected=expected, overrides=overrides):
                inputs = self.inputs()
                inputs["declared_routes"][0].update(overrides)
                if not overrides:
                    inputs["declared_routes"].append(deepcopy(inputs["declared_routes"][0]))
                acquisition = build_edge_observability_projection(**inputs)["evidence_acquisition"]
                self.assertEqual(acquisition["status"], "BLOCK")
                self.assertEqual(acquisition["intents"][0]["status"], expected)
                self.assertEqual(acquisition["intents"][0]["firewall_status"], "NOT_PLANNED")

    def test_forbidden_requirement_and_mixed_states_keep_separate_counts(self):
        inputs = self.inputs([self.requirement, "another missing document", "future price response"])
        acquisition = build_edge_observability_projection(**inputs)["evidence_acquisition"]
        self.assertEqual(acquisition["status"], "BLOCK")
        self.assertEqual(acquisition["summary"], {
            "requirement_count": 3, "ready_count": 1, "blocked_count": 1, "unresolved_count": 1,
        })
        states = {row["status"] for row in acquisition["intents"]}
        self.assertEqual(states, {"READY_PLAN_ONLY", "UNRESOLVED_NO_DECLARED_ROUTE", "BLOCK_FORBIDDEN_REQUIREMENT"})

    def test_no_explicit_gap_is_not_a_ready_acquisition_plan(self):
        inputs = self.inputs()
        spec = inputs["producer_readiness"]["specification"]
        spec["data_requirements"] = {"status": "SUPPORTED", "value": ["fixture support"], "support": ["fixture"]}
        inputs["producer_readiness"]["qualification"] = qualify_producer_test_readiness(spec)
        acquisition = build_edge_observability_projection(**inputs)["evidence_acquisition"]
        self.assertEqual(acquisition["status"], "NO_EXPLICIT_DATA_REQUIREMENTS")
        self.assertEqual(acquisition["intents"], [])

    def test_readiness_and_intent_hashes_bind_exact_upstream_changes(self):
        inputs = self.inputs()
        first = build_edge_observability_projection(**inputs)
        self.assertEqual(first, build_edge_observability_projection(**deepcopy(inputs)))
        spec = inputs["producer_readiness"]["specification"]
        spec["mechanism"]["value"] = ["changed upstream declaration"]
        with self.assertRaisesRegex(ValueError, "READINESS_QUALIFICATION_BINDING_MISMATCH"):
            build_edge_observability_projection(**inputs)
        inputs["producer_readiness"]["qualification"] = qualify_producer_test_readiness(spec)
        second = build_edge_observability_projection(**inputs)
        for key in ("readiness_hash", "intent_projection_hash"):
            self.assertNotEqual(first["evidence_acquisition"][key], second["evidence_acquisition"][key])
        self.assertNotEqual(first["projection_hash"], second["projection_hash"])

    def test_rejects_cross_hypothesis_composition(self):
        for field in ("task", "research"):
            inputs = self.inputs()
            inputs[field]["hypothesis_id"] = "OTHER"
            with self.subTest(field=field), self.assertRaisesRegex(EdgeObservabilityError, "HYPOTHESIS_BINDING_MISMATCH"):
                build_edge_observability_projection(**inputs)

    def test_rejects_outcomes_or_open_authority_in_new_inputs(self):
        for extra in (
            {"outcome_accessed": True},
            {"economic_result": "POSITIVE"},
            {"pnl": 12},
            {"authority": {"live_trading_authorized": True}},
        ):
            inputs = self.inputs()
            inputs["producer_readiness"].update(extra)
            with self.subTest(extra=extra), self.assertRaises(EdgeObservabilityError):
                build_edge_observability_projection(**inputs)

    def test_composition_is_pure_and_performs_no_io(self):
        inputs = self.inputs()
        before = deepcopy(inputs)
        with patch("builtins.open", side_effect=AssertionError("file I/O forbidden")), \
             patch("socket.socket", side_effect=AssertionError("network forbidden")), \
             patch("subprocess.run", side_effect=AssertionError("process forbidden")), \
             patch("pathlib.Path.write_text", side_effect=AssertionError("write forbidden")):
            build_edge_observability_projection(**inputs)
        self.assertEqual(inputs, before)

    def test_optional_catalogs_require_readiness_and_missing_catalogs_do_not_invent_routes(self):
        with self.assertRaisesRegex(EdgeObservabilityError, "PRODUCER_READINESS_REQUIRED"):
            build_edge_observability_projection(task={"task_id": "T"}, declared_routes=[])
        inputs = self.inputs()
        del inputs["declared_routes"], inputs["validated_adapters"]
        acquisition = build_edge_observability_projection(**inputs)["evidence_acquisition"]
        self.assertEqual(acquisition["intents"][0]["status"], "UNRESOLVED_NO_DECLARED_ROUTE")

    def test_legacy_call_has_no_new_acquisition_fields(self):
        result = build_edge_observability_projection(task={"task_id": "T"})
        self.assertNotIn("evidence_acquisition", result)


if __name__ == "__main__":
    unittest.main()

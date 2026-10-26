from __future__ import annotations

import unittest
from copy import deepcopy

from research.research_os.expansion.evidence_acquisition_intents_v2 import (
    CLOSED_AUTHORITY,
    build_evidence_acquisition_intents,
)
from research.research_os.expansion.source_adapters_v1 import validate_adapter_spec
from research.research_os.expansion.source_qualification import qualify_producer_test_readiness
from research.research_os.expansion.source_qualification import build_producer_test_readiness
from research.research_os.tests.test_producer_economic_readiness import _candidate_output, _event_detail


class EvidenceAcquisitionIntentsV2Tests(unittest.TestCase):
    documentary_control = "concurrent-news/confounder controls declared before outcome access"

    def test_existing_producer_control_is_unresolved_not_an_outcome_request(self):
        readiness = build_producer_test_readiness(_candidate_output("EVENT_DOCUMENT"), _event_detail())
        before = deepcopy(readiness)
        result = build_evidence_acquisition_intents(readiness, declared_routes=[], validated_adapters={})
        self.assertEqual(readiness, before)
        self.assertEqual(result["readiness_hash"], readiness["qualification"]["readiness_hash"])
        self.assertEqual(result["status"], "INCOMPLETE_UNRESOLVED")
        self.assertEqual(result["summary"], {"requirement_count": 4, "ready_count": 0, "blocked_count": 0, "unresolved_count": 4})
        self.assertTrue(all(i["status"] == "UNRESOLVED_NO_DECLARED_ROUTE" for i in result["intents"]))

    def test_exact_documentary_control_with_explicit_route_is_plan_only(self):
        adapter = self._adapter()
        result = build_evidence_acquisition_intents(
            self._readiness([self.documentary_control]),
            declared_routes=[self._route(self.documentary_control)],
            validated_adapters={adapter["adapter_id"]: adapter},
        )
        self.assertEqual(result["status"], "READY_PLAN_ONLY")
        self.assertEqual(result["intents"][0]["acquisition_plan"]["plan"]["execution_mode"], "PLAN_ONLY_NO_NETWORK")
        self.assertEqual(result["authority"], CLOSED_AUTHORITY)
        self.assertFalse(result["network_execution_authorized"])
        self.assertFalse(result["network_call_performed"])
        self.assertFalse(result["outcome_accessed"])

    def test_documentary_control_never_bypasses_content_adapter_or_pit_firewall(self):
        for route_changes, adapter_changes, expected in (
            ({"content_classes": ["returns"]}, {}, "BLOCK_FORBIDDEN_CONTENT_CLASS"),
            ({"content_classes": ["future_outcomes"]}, {}, "BLOCK_FORBIDDEN_CONTENT_CLASS"),
            ({"clock_cutoff": "2026-10-20T01:00:00"}, {}, "BLOCK_INVALID_DECLARED_ROUTE"),
            ({"version_policy": "UNKNOWN"}, {}, "BLOCK_INVALID_DECLARED_ROUTE"),
            ({}, {"activated": True}, "BLOCK_FIREWALL"),
            ({}, {"network_access": True}, "BLOCK_FIREWALL"),
            ({}, {"outcome_access_authorized": True}, "BLOCK_FIREWALL"),
        ):
            with self.subTest(route=route_changes, adapter=adapter_changes):
                adapter = self._adapter()
                adapter.update(adapter_changes)
                result = build_evidence_acquisition_intents(
                    self._readiness([self.documentary_control]),
                    declared_routes=[self._route(self.documentary_control, **route_changes)],
                    validated_adapters={adapter["adapter_id"]: adapter},
                )
                self.assertEqual(result["intents"][0]["status"], expected)
                self.assertFalse(result["network_execution_authorized"])
                self.assertFalse(result["outcome_accessed"])

    def test_control_wording_cannot_launder_extra_outcome_demands(self):
        for requirement in (
            self.documentary_control + " and future returns",
            "returns required; " + self.documentary_control,
            self.documentary_control.replace("before", "after"),
            self.documentary_control.upper(),
            self.documentary_control + "; fetch market reaction",
            self.documentary_control + "\npost-event prices",
        ):
            with self.subTest(requirement=requirement):
                result = build_evidence_acquisition_intents(
                    self._readiness([requirement]), declared_routes=[self._route(requirement)],
                    validated_adapters={},
                )
                self.assertEqual(result["intents"][0]["status"], "BLOCK_FORBIDDEN_REQUIREMENT")
                self.assertIsNone(result["intents"][0]["acquisition_plan"])

    def _readiness(self, requirements):
        specification = {
            "engine_family": "EVENT_DOCUMENT",
            "mechanism": {"status": "SUPPORTED", "value": "documentary event premise", "support": ["candidate.mechanism"]},
            "universe": {"status": "PARTIAL", "value": {"issuer_id": "AAPL"}, "support": ["dossier.event_identity"]},
            "clock": {"status": "PARTIAL", "value": {"information_availability": "DECLARED"}, "support": ["dossier.document_clock"]},
            "expression_requirements": {"status": "REQUIRED", "value": ["executable instrument"], "support": []},
            "data_requirements": {"status": "REQUIRED", "value": list(requirements), "support": []},
            "cost_capacity_requirements": {"status": "REQUIRED", "value": ["cost model declaration"], "support": []},
            "falsification": {"status": "SUPPORTED", "value": "withdraw if documentary premise is superseded", "support": ["candidate.falsification_scope"]},
            "legacy_screen": {"status": "NOT_APPLICABLE_EXISTING_BOUND_CANDIDATE", "new_claim": False},
            "unsupported_economic_claims": {
                "novelty": "UNKNOWN",
                "consensus": "UNKNOWN",
                "surprise": "UNKNOWN",
                "market_response": "NOT_OBSERVED",
                "empirical_return": "NOT_OBSERVED",
                "capacity_estimate": "NOT_ESTIMATED",
            },
            "outcome_accessed": False,
            "economic_result": "NOT_OBSERVED",
        }
        qualification = qualify_producer_test_readiness(specification)
        self.assertEqual(qualification["status"], "PASS", qualification)
        return {
            "readiness_version": "producer-test-readiness.v1",
            "hypothesis_id": "DOC-EVENT-TEST-001",
            "specification": specification,
            "qualification": qualification,
            "outcome_accessed": False,
            "economic_result": "NOT_OBSERVED",
        }

    def _adapter(self, allowed=None):
        validated = validate_adapter_spec({
            "adapter_id": "official-corp-actions.design.v1",
            "provider_family": "OFFICIAL_CORPORATE_ACTIONS",
            "data_class": "OFFICIAL_CORPORATE_ACTIONS",
            "permission_model": "PUBLIC",
            "clock_semantics": "PUBLICATION_TIME",
            "revision_policy": "VERSION_AS_PUBLISHED",
            "survivorship_policy": "INCLUDE_ALL_DECLARED_RECORDS",
            "locator_template": "declared-provider-template-only",
            "activation_state": "DESIGN_ONLY_NOT_CONNECTED",
            "network_access": False,
            "contains_market_outcome": False,
            "allowed_content": list(allowed or ["official_corporate_actions"]),
            "forbidden_content": ["returns", "market_reaction"],
        })
        self.assertEqual(validated["status"], "PASS", validated)
        return validated

    def _route(self, requirement, **overrides):
        route = {
            "requirement": requirement,
            "adapter_id": "official-corp-actions.design.v1",
            "content_classes": ["official_corporate_actions"],
            "entity_scope": {"issuer_id": "AAPL"},
            "clock_cutoff": "2026-10-20T15:00:00Z",
            "version_policy": "AS_PUBLISHED_AT_OR_BEFORE_CUTOFF",
            "locator_parameters": {"issuer_id": "AAPL"},
        }
        route.update(overrides)
        return route

    def test_declared_documentary_gap_projects_to_existing_firewall_plan(self):
        requirement = "official holder/record/ex-date data when eligibility matters"
        adapter = self._adapter()
        result = build_evidence_acquisition_intents(
            self._readiness([requirement]),
            declared_routes=[self._route(requirement)],
            validated_adapters={adapter["adapter_id"]: adapter},
        )
        self.assertEqual(result["status"], "READY_PLAN_ONLY")
        self.assertEqual(result["summary"], {"requirement_count": 1, "ready_count": 1, "blocked_count": 0, "unresolved_count": 0})
        intent = result["intents"][0]
        self.assertEqual(intent["status"], "READY_PLAN_ONLY")
        self.assertEqual(intent["acquisition_plan"]["status"], "READY_AWAITING_SOURCE_ACTIVATION_AUTHORITY")
        self.assertEqual(intent["acquisition_plan"]["plan"]["execution_mode"], "PLAN_ONLY_NO_NETWORK")
        self.assertFalse(intent["acquisition_plan"]["network_execution_authorized"])
        self.assertFalse(intent["acquisition_plan"]["network_call_performed"])
        self.assertFalse(result["outcome_accessed"])
        self.assertEqual(result["economic_result"], "NOT_OBSERVED")
        self.assertEqual(result["authority"], CLOSED_AUTHORITY)

    def test_missing_declared_route_is_unresolved_without_inventing_source(self):
        result = build_evidence_acquisition_intents(
            self._readiness(["point-in-time event availability"]),
            declared_routes=[],
            validated_adapters={},
        )
        self.assertEqual(result["status"], "INCOMPLETE_UNRESOLVED")
        intent = result["intents"][0]
        self.assertEqual(intent["status"], "UNRESOLVED_NO_DECLARED_ROUTE")
        self.assertIsNone(intent["request"])
        self.assertIsNone(intent["acquisition_plan"])

    def test_declared_route_with_missing_validated_adapter_is_unresolved(self):
        requirement = "point-in-time event availability"
        result = build_evidence_acquisition_intents(
            self._readiness([requirement]),
            declared_routes=[self._route(requirement)],
            validated_adapters={},
        )
        self.assertEqual(result["status"], "INCOMPLETE_UNRESOLVED")
        self.assertEqual(result["intents"][0]["status"], "UNRESOLVED_ADAPTER_NOT_DECLARED")
        self.assertIsNone(result["intents"][0]["request"])

    def test_outcome_like_requirement_blocks_before_route_matching(self):
        result = build_evidence_acquisition_intents(
            self._readiness(["future returns after the event"]),
            declared_routes=[],
            validated_adapters={},
        )
        self.assertEqual(result["status"], "BLOCK")
        intent = result["intents"][0]
        self.assertEqual(intent["status"], "BLOCK_FORBIDDEN_REQUIREMENT")
        self.assertEqual(intent["blockers"], ["FORBIDDEN_OUTCOME_LIKE_REQUIREMENT"])
        self.assertIsNone(intent["request"])

    def test_forbidden_content_class_blocks_even_if_adapter_declares_it(self):
        requirement = "point-in-time event availability"
        adapter = self._adapter(["returns"])
        route = self._route(requirement, content_classes=["returns"])
        result = build_evidence_acquisition_intents(
            self._readiness([requirement]),
            declared_routes=[route],
            validated_adapters={adapter["adapter_id"]: adapter},
        )
        self.assertEqual(result["status"], "BLOCK")
        self.assertEqual(result["intents"][0]["status"], "BLOCK_FORBIDDEN_CONTENT_CLASS")
        self.assertIsNone(result["intents"][0]["request"])

    def test_missing_or_naive_pit_cutoff_blocks_without_guessing(self):
        requirement = "point-in-time event availability"
        adapter = self._adapter()
        for cutoff in ("", "2026-10-20T15:00:00"):
            with self.subTest(cutoff=cutoff):
                result = build_evidence_acquisition_intents(
                    self._readiness([requirement]),
                    declared_routes=[self._route(requirement, clock_cutoff=cutoff)],
                    validated_adapters={adapter["adapter_id"]: adapter},
                )
                self.assertEqual(result["status"], "BLOCK")
                self.assertEqual(result["intents"][0]["status"], "BLOCK_INVALID_DECLARED_ROUTE")
                self.assertIn("CLOCK_CUTOFF_NOT_PIT_BOUND", result["intents"][0]["blockers"])
                self.assertIsNone(result["intents"][0]["request"])

    def test_unknown_version_policy_blocks(self):
        requirement = "point-in-time event availability"
        adapter = self._adapter()
        result = build_evidence_acquisition_intents(
            self._readiness([requirement]),
            declared_routes=[self._route(requirement, version_policy="UNKNOWN")],
            validated_adapters={adapter["adapter_id"]: adapter},
        )
        self.assertEqual(result["status"], "BLOCK")
        self.assertIn("VERSION_POLICY_NOT_DECLARED", result["intents"][0]["blockers"])

    def test_multiple_exact_routes_block_as_ambiguous(self):
        requirement = "point-in-time event availability"
        adapter = self._adapter()
        route = self._route(requirement)
        result = build_evidence_acquisition_intents(
            self._readiness([requirement]),
            declared_routes=[route, deepcopy(route)],
            validated_adapters={adapter["adapter_id"]: adapter},
        )
        self.assertEqual(result["status"], "BLOCK")
        self.assertEqual(result["intents"][0]["status"], "BLOCK_AMBIGUOUS_DECLARED_ROUTE")

    def test_projection_is_deterministic_and_declared_route_order_independent(self):
        req_a = "point-in-time event availability"
        req_b = "official holder/record/ex-date data when eligibility matters"
        readiness = self._readiness([req_b, req_a])
        adapter = self._adapter()
        adapters = {adapter["adapter_id"]: adapter}
        routes = [self._route(req_b), self._route(req_a)]
        first = build_evidence_acquisition_intents(
            readiness, declared_routes=routes, validated_adapters=adapters,
        )
        second = build_evidence_acquisition_intents(
            deepcopy(readiness), declared_routes=list(reversed(routes)), validated_adapters=adapters,
        )
        self.assertEqual(first, second)
        self.assertEqual(first["requirements"], sorted([req_a, req_b]))
        self.assertEqual(first["status"], "READY_PLAN_ONLY")
        self.assertEqual(len(first["projection_hash"]), 64)

    def test_readiness_hash_binding_and_outcome_boundary_fail_closed(self):
        readiness = self._readiness(["point-in-time event availability"])
        corrupted = deepcopy(readiness)
        corrupted["qualification"]["readiness_hash"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "READINESS_QUALIFICATION_BINDING_MISMATCH"):
            build_evidence_acquisition_intents(corrupted, declared_routes=[], validated_adapters={})

        outcome = deepcopy(readiness)
        outcome["outcome_accessed"] = True
        with self.assertRaisesRegex(ValueError, "OUTCOME_BEARING_READINESS_FORBIDDEN"):
            build_evidence_acquisition_intents(outcome, declared_routes=[], validated_adapters={})


if __name__ == "__main__":
    unittest.main()

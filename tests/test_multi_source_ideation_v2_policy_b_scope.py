from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import build_context_snapshot
from research.research_os.multi_source_ideation_bindings import information_value_from_research_intelligence


def snap():
    keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
    return build_context_snapshot(ideation_cycle_id="b",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={})


class PolicyBScopeTests(unittest.TestCase):
    def test_unknown_research_action_fails_closed(self):
        out=information_value_from_research_intelligence(snapshot=snap(),decision={"action":"CREATE_READY_TASK","executable":True})
        self.assertEqual(out["status"],"INVALID_INPUT"); self.assertIsNone(out["artifact_kind"])

    def test_existing_information_value_binding_keeps_documentary_rescue_passive(self):
        for action in ("ARCHAEOLOGY_LOOKUP", "REUSE_EXISTING_EVIDENCE"):
            with self.subTest(action=action):
                out = information_value_from_research_intelligence(
                    snapshot=snap(),
                    decision={
                        "action": action, "executable": True, "candidate_id": "C1",
                        "reason_codes": ["BOUNDED_DOCUMENTARY_IMPLEMENTATION_RESCUE"],
                        "uncertainty_resolved": "check one source permission",
                        "selected_action": {"action": action, "cost_units": 0},
                        "scheduler_mutation": False,
                    },
                )
                self.assertEqual(out["status"], "SEED_EMITTED")
                self.assertEqual(out["artifact_kind"], "IDEATION_SEED")
                self.assertEqual(out["payload"]["research_action"], action)
                self.assertEqual(out["payload"]["selected_action"]["cost_units"], 0)
                self.assertNotIn("task_created", out)

    def test_validation_escalation_is_not_ideation_proposal(self):
        out=information_value_from_research_intelligence(snapshot=snap(),decision={"action":"ESCALATE_VALIDATION","executable":True})
        self.assertEqual(out["status"],"NO_ACTION"); self.assertIsNone(out["artifact_kind"])


if __name__ == "__main__": unittest.main()

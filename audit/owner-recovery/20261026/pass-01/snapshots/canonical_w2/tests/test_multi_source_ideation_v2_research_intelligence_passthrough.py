from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import build_context_snapshot
from research.research_os.multi_source_ideation_bindings import information_value_from_research_intelligence


def snap():
    keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
    return build_context_snapshot(ideation_cycle_id="ri",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={})


class ResearchIntelligencePassthroughTests(unittest.TestCase):
    def test_reason_codes_and_selected_action_are_preserved(self):
        decision={"action":"ACQUIRE_EVIDENCE_INTENT","executable":True,"candidate_id":"c","reason_codes":["R1","R2"],"uncertainty_resolved":"timing","selected_action":{"action":"ACQUIRE_EVIDENCE_INTENT","cost_units":"UNKNOWN"}}
        out=information_value_from_research_intelligence(snapshot=snap(),decision=decision)
        self.assertEqual(out["payload"]["reason_codes"],["R1","R2"]); self.assertEqual(out["payload"]["selected_action"],decision["selected_action"])


if __name__ == "__main__": unittest.main()

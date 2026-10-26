from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import build_context_snapshot
from research.research_os.multi_source_ideation_bindings import systematic_coverage_from_frontier


def snap():
    keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
    return build_context_snapshot(ideation_cycle_id="f",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={})


class FrontierFailClosedTests(unittest.TestCase):
    def test_scientifically_exhausted_is_terminal_without_proposal(self):
        out=systematic_coverage_from_frontier(snapshot=snap(),frontier_decision={"action":"NO_ACTION","executable":False,"frontier_state":"SCIENTIFICALLY_EXHAUSTED"},source_plan=None)
        self.assertEqual(out["status"],"FRONTIER_EXHAUSTED"); self.assertIsNone(out["artifact_kind"])

    def test_unrecognized_source_plan_status_is_invalid_input(self):
        out=systematic_coverage_from_frontier(snapshot=snap(),frontier_decision={"action":"GENERATE_MECHANISM","executable":True},source_plan={"status":"MAGIC_SOURCE"})
        self.assertEqual(out["status"],"INVALID_INPUT")


if __name__ == "__main__": unittest.main()

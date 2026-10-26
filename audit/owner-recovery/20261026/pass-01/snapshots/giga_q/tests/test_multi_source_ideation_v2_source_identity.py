from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import build_context_snapshot
from research.research_os.multi_source_ideation_bindings import systematic_coverage_from_frontier


def snap():
    keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
    return build_context_snapshot(ideation_cycle_id="s",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={})


class SourceIdentityFailClosedTests(unittest.TestCase):
    def test_path_only_source_is_not_accepted_as_canonical_identity(self):
        out=systematic_coverage_from_frontier(snapshot=snap(),frontier_decision={"action":"GENERATE_MECHANISM","executable":True},source_plan={"status":"SOURCE_SELECTED","source":{"path":"looks-qualified.json"}})
        self.assertEqual(out["status"],"BLOCKED")
        self.assertEqual(out["reason"],"SOURCE_CONTENT_IDENTITY_MISSING")


if __name__ == "__main__": unittest.main()

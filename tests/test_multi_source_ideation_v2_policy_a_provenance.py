from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import build_context_snapshot
from research.research_os.multi_source_ideation_bindings import systematic_coverage_from_frontier


class PolicyAProvenanceTests(unittest.TestCase):
    def test_source_provenance_is_preserved_on_seed(self):
        keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
        s=build_context_snapshot(ideation_cycle_id="a",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={})
        source={"path":"p","packet_hash":"ph","blob_sha":"bs","record_hash":"rh","source_ref":"sr","available_at":"t"}
        out=systematic_coverage_from_frontier(snapshot=s,frontier_decision={"action":"GENERATE_MECHANISM","executable":True},source_plan={"status":"SOURCE_SELECTED","source":source,"frontier_id":"f","family":"EVENT_DOCUMENT"})
        self.assertEqual(out["payload"]["source_provenance"],source)


if __name__ == "__main__": unittest.main()

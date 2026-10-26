from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import DeterministicFakeBackend, build_context_snapshot, policy_c


class ModelSelectionTests(unittest.TestCase):
    def test_selection_is_explicit_not_implicit_first_item(self):
        keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
        s=build_context_snapshot(ideation_cycle_id="sel",created_at="2026-10-21T20:00:00Z",refs={k:k for k in keys},relevant_schema_versions={})
        alts=[{"summary":"first"},{"summary":"second"}]
        a,r=policy_c(snapshot=s,backend=DeterministicFakeBackend({"alternatives":alts,"selected_alternative_index":1}),mandate={})
        self.assertEqual(a["payload"]["summary"],"second"); self.assertEqual(r["selected_alternative_index"],1)


if __name__ == "__main__": unittest.main()

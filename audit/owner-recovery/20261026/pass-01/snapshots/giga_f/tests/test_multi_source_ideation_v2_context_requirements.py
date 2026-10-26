from __future__ import annotations

import unittest

from research.research_os.multi_source_ideation import build_context_snapshot


class ContextRequirementTests(unittest.TestCase):
    def test_each_required_snapshot_ref_is_mandatory(self):
        keys=("memory_snapshot_ref","ancestry_snapshot_ref","frontier_snapshot_ref","evidence_snapshot_ref","source_catalog_snapshot_ref","capability_snapshot_ref","authority_snapshot_ref","active_work_snapshot_ref")
        full={k:k for k in keys}
        for missing in keys:
            refs=dict(full); refs.pop(missing)
            with self.subTest(missing=missing):
                with self.assertRaises(ValueError): build_context_snapshot(ideation_cycle_id="c",created_at="2026-10-21T20:00:00Z",refs=refs,relevant_schema_versions={})


if __name__ == "__main__": unittest.main()
